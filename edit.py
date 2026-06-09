"""
关卡可视化编辑器
运行方式：python edit.py

功能：
  - 启动后列出所有 levels/*.json，输入编号选择关卡
  - 进入 pygame 编辑窗口（与游戏逻辑分辨率一致：960×540）
  - 拖拽任意物体调整位置，实时显示坐标
  - 平台可调整宽高（拖拽右边缘 / 下边缘）
  - 左/右方向键滚动世界视图（摄像机平移）
  - 右键删除物体
  - 工具栏：[P] 添加平台  [N] 添加NPC  [G] 添加宝石  [S] 保存  [ESC] 退出
  - 保存时直接覆写原 JSON 文件
"""
from __future__ import annotations
import json
import sys
import os
from pathlib import Path
from copy import deepcopy
import pygame

# ── 常量 ─────────────────────────────────────────────────────────────────────
SCREEN_W  = 960
SCREEN_H  = 540
FPS       = 60
FONT_NAME = "microsoftyahei"

# 颜色
C_BG        = (20,  20,  34)
C_GRID      = (40,  40,  60)
C_PLATFORM  = (94,  129, 172)
C_NPC       = (250, 179, 135)
C_GEM       = (249, 226, 175)
C_SPAWN     = (166, 227, 161)
C_SELECT    = (255, 255, 100)
C_HANDLE    = (255, 100, 100)
C_TEXT      = (205, 214, 244)
C_TOOLBAR   = (30,  30,  50)
C_HINT      = (120, 120, 160)

TOOLBAR_H   = 40
HANDLE_SIZE = 8    # 缩放把手大小


# ── 数据模型 ──────────────────────────────────────────────────────────────────
class EditorObject:
    """编辑器中所有可拖拽物体的基类。"""
    kind: str = "base"

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.selected = False

    def get_rect(self) -> pygame.Rect:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError

    def draw(self, surface: pygame.Surface, cam_x: int, font: pygame.font.Font) -> None:
        raise NotImplementedError


class EdPlatform(EditorObject):
    kind = "platform"
    def __init__(self, x: int, y: int, w: int = 160, h: int = 20,
                 sprite_key: str = "default") -> None:
        super().__init__(x, y)
        self.w          = w
        self.h          = h
        self.sprite_key = sprite_key

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def resize_handle_rect(self) -> pygame.Rect:
        """右下角缩放把手。"""
        return pygame.Rect(self.x + self.w - HANDLE_SIZE,
                           self.y + self.h - HANDLE_SIZE,
                           HANDLE_SIZE * 2, HANDLE_SIZE * 2)

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h,
                "sprite_key": self.sprite_key}

    def draw(self, surface: pygame.Surface, cam_x: int, font: pygame.font.Font) -> None:
        r = pygame.Rect(self.x - cam_x, self.y, self.w, self.h)
        color = C_SELECT if self.selected else C_PLATFORM
        pygame.draw.rect(surface, color, r, border_radius=3)
        pygame.draw.rect(surface, _lighten(color, 40), pygame.Rect(r.x, r.y, r.w, 4))
        # 缩放把手
        hr = self.resize_handle_rect()
        pygame.draw.rect(surface, C_HANDLE,
                         pygame.Rect(hr.x - cam_x, hr.y, hr.w, hr.h))
        # 坐标标注
        if self.selected:
            lbl = font.render(f"({self.x},{self.y}) {self.w}x{self.h}", True, C_SELECT)
            surface.blit(lbl, (r.x, r.y - 18))


class EdNPC(EditorObject):
    kind = "npc"
    W, H = 32, 48
    def __init__(self, x: int, y: int, name: str = "NPC",
                 sprite_key: str = "default",
                 dialogue_key: str = "guide") -> None:
        super().__init__(x, y)
        self.name         = name
        self.sprite_key   = sprite_key
        self.dialogue_key = dialogue_key

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.W // 2, self.y - self.H, self.W, self.H)

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "name": self.name,
                "sprite_key": self.sprite_key, "dialogue_key": self.dialogue_key}

    def draw(self, surface: pygame.Surface, cam_x: int, font: pygame.font.Font) -> None:
        r    = self.get_rect()
        rx   = r.x - cam_x
        color = C_SELECT if self.selected else C_NPC
        pygame.draw.rect(surface, color, (rx + 8, r.y + 16, 16, 26), border_radius=3)
        pygame.draw.circle(surface, color, (rx + 16, r.y + 12), 10)
        if self.selected:
            lbl = font.render(f"{self.name} ({self.x},{self.y})", True, C_SELECT)
            surface.blit(lbl, (rx, r.y - 18))
        else:
            lbl = font.render(self.name, True, C_NPC)
            surface.blit(lbl, (rx, r.y - 16))


class EdGem(EditorObject):
    kind = "gem"
    SIZE = 16
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

    def get_rect(self) -> pygame.Rect:
        s = self.SIZE
        return pygame.Rect(self.x - s // 2, self.y - s // 2, s, s)

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}

    def draw(self, surface: pygame.Surface, cam_x: int, font: pygame.font.Font) -> None:
        cx, cy = self.x - cam_x, self.y
        s      = self.SIZE
        color  = C_SELECT if self.selected else C_GEM
        pts    = [(cx, cy - s // 2), (cx + s // 2, cy),
                  (cx, cy + s // 2), (cx - s // 2, cy)]
        pygame.draw.polygon(surface, color, pts)
        if self.selected:
            lbl = font.render(f"({self.x},{self.y})", True, C_SELECT)
            surface.blit(lbl, (cx - 20, cy - s // 2 - 18))


class EdSpawn(EditorObject):
    kind = "spawn"
    W, H = 32, 48
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.W // 2, self.y - self.H, self.W, self.H)

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}

    def draw(self, surface: pygame.Surface, cam_x: int, font: pygame.font.Font) -> None:
        r  = self.get_rect()
        rx = r.x - cam_x
        color = C_SELECT if self.selected else C_SPAWN
        pygame.draw.rect(surface, color, (rx, r.y, r.w, r.h), 2, border_radius=4)
        pygame.draw.line(surface, color,
                         (rx + r.w // 2, r.y), (rx + r.w // 2, r.bottom), 2)
        lbl = font.render(f"出生点 ({self.x},{self.y})", True, color)
        surface.blit(lbl, (rx, r.y - 18))


# ── 编辑器主体 ────────────────────────────────────────────────────────────────
class Editor:
    def __init__(self, json_path: str) -> None:
        self.json_path = json_path
        self._load_json()

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(f"关卡编辑器 — {Path(json_path).name}")
        self.clock  = pygame.time.Clock()
        self.font   = pygame.font.SysFont(FONT_NAME, 16)
        self.font_s = pygame.font.SysFont(FONT_NAME, 13)

        self.cam_x:    int  = 0
        self.world_w:  int  = self._meta.get("world_w", SCREEN_W)
        self.cam_speed = 6

        # 物体列表
        self.objects: list[EditorObject] = []
        self._import_objects()

        # 交互状态
        self._drag_obj:   EditorObject | None = None
        self._drag_off:   tuple[int, int]     = (0, 0)
        self._resize_obj: EdPlatform | None   = None
        self._resize_orig: tuple[int, int, int, int] = (0, 0, 0, 0)
        self._resize_mouse_start: tuple[int, int] = (0, 0)

        self._status = "就绪  [P]平台 [N]NPC [G]宝石 [S]保存 [ESC]退出 | 右键删除 | 拖拽调整位置"

    # ── JSON 加载 ─────────────────────────────────────────────────────────
    def _load_json(self) -> None:
        with open(self.json_path, encoding="utf-8") as f:
            self._data = json.load(f)
        self._meta = self._data.get("meta", {})

    def _import_objects(self) -> None:
        d = self._data
        # 出生点
        sp = d.get("player_spawn", {"x": 80, "y": SCREEN_H - 40})
        self.objects.append(EdSpawn(sp["x"], sp["y"]))
        # 平台
        for p in d.get("platforms", []):
            self.objects.append(EdPlatform(
                p["x"], p["y"], p["w"], p["h"],
                p.get("sprite_key", "default")))
        # NPC
        for n in d.get("npcs", []):
            self.objects.append(EdNPC(
                n["x"], n["y"],
                n.get("name", "NPC"),
                n.get("sprite_key", "default"),
                n.get("dialogue_key", "guide")))
        # 宝石
        for g in d.get("gems", []):
            self.objects.append(EdGem(g["x"], g["y"]))

    # ── 保存 ─────────────────────────────────────────────────────────────
    def _save(self) -> None:
        out: dict = {"meta": deepcopy(self._meta)}
        out["meta"]["world_w"] = self.world_w

        spawns    = [o for o in self.objects if o.kind == "spawn"]
        platforms = [o for o in self.objects if o.kind == "platform"]
        npcs      = [o for o in self.objects if o.kind == "npc"]
        gems      = [o for o in self.objects if o.kind == "gem"]

        if spawns:
            out["player_spawn"] = spawns[0].to_dict()
        out["platforms"] = [p.to_dict() for p in platforms]
        out["npcs"]      = [n.to_dict() for n in npcs]
        out["gems"]      = [g.to_dict() for g in gems]

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        self._status = f"已保存 → {self.json_path}"

    # ── 选中最前方物体 ────────────────────────────────────────────────────
    def _pick(self, wx: int, wy: int) -> EditorObject | None:
        """wx/wy 为世界坐标。返回最上层命中的物体。"""
        for obj in reversed(self.objects):
            r = obj.get_rect()
            if r.collidepoint(wx, wy):
                return obj
        return None

    def _pick_resize_handle(self, wx: int, wy: int) -> EdPlatform | None:
        for obj in reversed(self.objects):
            if isinstance(obj, EdPlatform):
                hr = obj.resize_handle_rect()
                if hr.collidepoint(wx, wy):
                    return obj
        return None

    def _deselect_all(self) -> None:
        for obj in self.objects:
            obj.selected = False

    # ── 主循环 ────────────────────────────────────────────────────────────
    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            # ── 输入 ──────────────────────────────────────────────────────
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.cam_x = max(0, self.cam_x - self.cam_speed)
            if keys[pygame.K_RIGHT]:
                max_cam = max(0, self.world_w - SCREEN_W)
                self.cam_x = min(max_cam, self.cam_x + self.cam_speed)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_s:
                        self._save()
                    elif event.key == pygame.K_p:
                        self._add_platform()
                    elif event.key == pygame.K_n:
                        self._add_npc()
                    elif event.key == pygame.K_g:
                        self._add_gem()
                    elif event.key == pygame.K_DELETE:
                        self.objects = [o for o in self.objects
                                        if not o.selected or o.kind == "spawn"]

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    # 工具栏区域不处理
                    if my < TOOLBAR_H:
                        continue
                    wx = mx + self.cam_x  # 转世界坐标
                    wy = my

                    if event.button == 1:  # 左键
                        # 先检测缩放把手
                        robj = self._pick_resize_handle(wx, wy)
                        if robj:
                            self._resize_obj = robj
                            self._resize_orig = (robj.x, robj.y, robj.w, robj.h)
                            self._resize_mouse_start = (wx, wy)
                        else:
                            obj = self._pick(wx, wy)
                            self._deselect_all()
                            if obj:
                                obj.selected    = True
                                self._drag_obj  = obj
                                self._drag_off  = (wx - obj.x, wy - obj.y)
                            else:
                                self._drag_obj = None

                    elif event.button == 3:  # 右键删除
                        obj = self._pick(wx, wy)
                        if obj and obj.kind != "spawn":
                            self.objects.remove(obj)
                            self._status = "已删除"

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self._drag_obj   = None
                        self._resize_obj = None

                elif event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    wx = mx + self.cam_x
                    wy = my
                    if self._drag_obj:
                        self._drag_obj.x = wx - self._drag_off[0]
                        self._drag_obj.y = wy - self._drag_off[1]
                        self._status = (f"拖拽中: ({self._drag_obj.x}, "
                                        f"{self._drag_obj.y})")
                    elif self._resize_obj:
                        ox, oy, ow, oh = self._resize_orig
                        dx = wx - self._resize_mouse_start[0]
                        dy = wy - self._resize_mouse_start[1]
                        self._resize_obj.w = max(20, ow + dx)
                        self._resize_obj.h = max(8,  oh + dy)
                        self._status = (f"调整尺寸: {self._resize_obj.w}"
                                        f"x{self._resize_obj.h}")

            # ── 渲染 ──────────────────────────────────────────────────────
            self._draw()

        pygame.quit()

    # ── 添加物体 ──────────────────────────────────────────────────────────
    def _add_platform(self) -> None:
        cx = self.cam_x + SCREEN_W // 2
        cy = SCREEN_H // 2
        self._deselect_all()
        p = EdPlatform(cx - 80, cy, 160, 20)
        p.selected = True
        self.objects.append(p)
        self._status = "已添加平台，可拖拽定位"

    def _add_npc(self) -> None:
        cx = self.cam_x + SCREEN_W // 2
        cy = SCREEN_H - 40
        self._deselect_all()
        n = EdNPC(cx, cy, name="NPC", sprite_key="guide", dialogue_key="guide")
        n.selected = True
        self.objects.append(n)
        self._status = "已添加 NPC，可拖拽定位"

    def _add_gem(self) -> None:
        cx = self.cam_x + SCREEN_W // 2
        cy = SCREEN_H // 2
        self._deselect_all()
        g = EdGem(cx, cy)
        g.selected = True
        self.objects.append(g)
        self._status = "已添加宝石，可拖拽定位"

    # ── 绘制 ──────────────────────────────────────────────────────────────
    def _draw(self) -> None:
        self.screen.fill(C_BG)
        self._draw_grid()

        # 世界边界线
        right_x = self.world_w - self.cam_x
        pygame.draw.line(self.screen, (200, 80, 80),
                         (right_x, TOOLBAR_H), (right_x, SCREEN_H), 2)
        wlbl = self.font_s.render(f"世界宽度 {self.world_w}px", True, (200, 80, 80))
        self.screen.blit(wlbl, (right_x - wlbl.get_width() - 4, TOOLBAR_H + 4))

        # 所有物体
        for obj in self.objects:
            obj.draw(self.screen, self.cam_x, self.font)

        self._draw_toolbar()

    def _draw_grid(self) -> None:
        offset = self.cam_x % 60
        for x in range(-offset, SCREEN_W, 60):
            pygame.draw.line(self.screen, C_GRID, (x, TOOLBAR_H), (x, SCREEN_H))
        for y in range(TOOLBAR_H, SCREEN_H, 60):
            pygame.draw.line(self.screen, C_GRID, (0, y), (SCREEN_W, y))
        # 原点标记
        ox = 0 - self.cam_x
        if 0 <= ox <= SCREEN_W:
            pygame.draw.line(self.screen, (80, 80, 120),
                             (ox, TOOLBAR_H), (ox, SCREEN_H), 2)

    def _draw_toolbar(self) -> None:
        pygame.draw.rect(self.screen, C_TOOLBAR, (0, 0, SCREEN_W, TOOLBAR_H))
        pygame.draw.line(self.screen, C_GRID, (0, TOOLBAR_H), (SCREEN_W, TOOLBAR_H))

        items = [
            (f"关卡: {self._meta.get('name','')}",  C_TEXT),
            (f"视角: {self.cam_x}px",               C_HINT),
            (f"物体: {len(self.objects)}",           C_HINT),
            (self._status,                           C_TEXT),
        ]
        x = 8
        for txt, color in items:
            s = self.font_s.render(txt, True, color)
            self.screen.blit(s, (x, (TOOLBAR_H - s.get_height()) // 2))
            x += s.get_width() + 24

        # 快捷键提示（右侧）
        hint = self.font_s.render(
            "[P]平台  [N]NPC  [G]宝石  [Del]删除选中  [S]保存  [ESC]退出",
            True, C_HINT)
        self.screen.blit(hint, (SCREEN_W - hint.get_width() - 8,
                                (TOOLBAR_H - hint.get_height()) // 2))

        pygame.display.flip()


# ── 工具函数 ──────────────────────────────────────────────────────────────────
def _lighten(color: tuple, amount: int) -> tuple:
    return tuple(min(255, v + amount) for v in color[:3])


# ── 入口 ──────────────────────────────────────────────────────────────────────
def main() -> None:
    levels_dir = Path("levels")
    jsons = sorted(levels_dir.glob("*_layout.json"))

    if not jsons:
        print("未找到任何关卡文件（levels/*_layout.json）")
        sys.exit(1)

    print("=" * 40)
    print("  关卡可视化编辑器")
    print("=" * 40)
    for i, p in enumerate(jsons, 1):
        # 尝试读取关卡名
        try:
            with open(p, encoding="utf-8") as f:
                meta = json.load(f).get("meta", {})
            name = meta.get("name", p.stem)
        except Exception:
            name = p.stem
        print(f"  [{i}] {name}  ({p})")

    print()
    while True:
        raw = input(f"输入编号 (1-{len(jsons)})，回车确认：").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(jsons):
            chosen = jsons[int(raw) - 1]
            break
        print("无效编号，请重新输入。")

    print(f"\n正在打开编辑器：{chosen}")
    editor = Editor(str(chosen))
    editor.run()


if __name__ == "__main__":
    main()
