"""
关卡可视化编辑器
运行方式：python edit.py

功能：
  - 启动后列出所有 levels/*.json，输入编号选择关卡
  - 进入 pygame 编辑窗口（逻辑分辨率 960×540，跨电脑一致）
  - 拖拽物体调整位置，实时显示坐标
  - 平台右下角把手可调整宽高
  - 右键删除物体（出生点不可删）
  - [H] 切换选中物体的隐藏状态（隐藏后仍存储在 JSON，编辑器中半透明显示）
        平台隐藏 = 隐形平台，游戏中不可见但碰撞仍然生效
        NPC/宝石隐藏 = 游戏中不创建（不可见不可交互）
  - Ctrl+Z 撤回操作（最多 50 步）
  - [P] 添加平台  [N] 添加NPC  [G] 添加宝石
  - [S] 保存（覆写原 JSON）  [ESC] 退出
  - 左/右方向键滚动世界视图
"""
from __future__ import annotations
import json
import sys
import copy
from pathlib import Path
from typing import Any
import pygame

# ── 常量 ─────────────────────────────────────────────────────────────────────
SCREEN_W  = 960
SCREEN_H  = 540
FPS       = 60
FONT_NAME = "microsoftyahei"

C_BG       = (20,  20,  34)
C_GRID     = (40,  40,  60)
C_PLATFORM = (94,  129, 172)
C_NPC      = (250, 179, 135)
C_GEM      = (249, 226, 175)
C_SPAWN    = (166, 227, 161)
C_SELECT   = (255, 255, 100)
C_HANDLE   = (255, 100, 100)
C_TEXT     = (205, 214, 244)
C_TOOLBAR  = (30,  30,  50)
C_HINT     = (120, 120, 160)
C_HIDDEN   = (60,  60,  80)    # 隐藏物体的颜色

TOOLBAR_H   = 40
HANDLE_SIZE = 8
MAX_UNDO    = 50   # 最大撤回步数


# ── 数据模型 ──────────────────────────────────────────────────────────────────
class EditorObject:
    kind: str = "base"

    def __init__(self, x: int, y: int) -> None:
        self.x        = x
        self.y        = y
        self.selected = False
        self.hidden   = False   # 隐藏标志

    def get_rect(self) -> pygame.Rect:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError

    def draw(self, surface: pygame.Surface, cam_x: int, font: pygame.font.Font) -> None:
        raise NotImplementedError

    def _alpha_color(self, color: tuple) -> tuple:
        """隐藏状态返回暗色，否则返回原色。"""
        if self.hidden:
            return C_HIDDEN
        return C_SELECT if self.selected else color


class EdPlatform(EditorObject):
    kind = "platform"

    def __init__(self, x: int, y: int, w: int = 160, h: int = 20,
                 sprite_key: str = "default", hidden: bool = False) -> None:
        super().__init__(x, y)
        self.w          = w
        self.h          = h
        self.sprite_key = sprite_key
        self.hidden     = hidden

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def resize_handle_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x + self.w - HANDLE_SIZE,
                           self.y + self.h - HANDLE_SIZE,
                           HANDLE_SIZE * 2, HANDLE_SIZE * 2)

    def to_dict(self) -> dict:
        d = {"x": self.x, "y": self.y, "w": self.w, "h": self.h,
             "sprite_key": self.sprite_key}
        if self.hidden:
            d["hidden"] = True
        return d

    def draw(self, surface: pygame.Surface, cam_x: int, font: pygame.font.Font) -> None:
        color = self._alpha_color(C_PLATFORM)
        r     = pygame.Rect(self.x - cam_x, self.y, self.w, self.h)
        alpha = 80 if self.hidden else 255
        s     = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        s.fill((*color[:3], alpha))
        pygame.draw.rect(s, (*_lighten(color, 40), alpha), (0, 0, r.w, 4))
        surface.blit(s, r.topleft)
        if not self.hidden:
            hr = self.resize_handle_rect()
            pygame.draw.rect(surface, C_HANDLE,
                             pygame.Rect(hr.x - cam_x, hr.y, hr.w, hr.h))
        if self.selected:
            lbl = font.render(
                f"({'隐藏' if self.hidden else ''}平台) ({self.x},{self.y}) {self.w}x{self.h}",
                True, C_SELECT)
            surface.blit(lbl, (r.x, r.y - 18))


class EdNPC(EditorObject):
    kind = "npc"
    W, H = 32, 48

    def __init__(self, x: int, y: int, name: str = "NPC",
                 sprite_key: str = "default", dialogue_key: str = "guide",
                 hidden: bool = False) -> None:
        super().__init__(x, y)
        self.name         = name
        self.sprite_key   = sprite_key
        self.dialogue_key = dialogue_key
        self.hidden       = hidden

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.W // 2, self.y - self.H, self.W, self.H)

    def to_dict(self) -> dict:
        d = {"x": self.x, "y": self.y, "name": self.name,
             "sprite_key": self.sprite_key, "dialogue_key": self.dialogue_key}
        if self.hidden:
            d["hidden"] = True
        return d

    def draw(self, surface: pygame.Surface, cam_x: int, font: pygame.font.Font) -> None:
        r     = self.get_rect()
        rx    = r.x - cam_x
        color = self._alpha_color(C_NPC)
        alpha = 80 if self.hidden else 255
        s     = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color[:3], alpha), (8, 16, 16, 26), border_radius=3)
        pygame.draw.circle(s, (*color[:3], alpha), (16, 12), 10)
        surface.blit(s, (rx, r.y))
        lbl_color = C_SELECT if self.selected else (C_HIDDEN if self.hidden else C_NPC)
        tag = f"{'[隐] ' if self.hidden else ''}{self.name} ({self.x},{self.y})"
        lbl = font.render(tag, True, lbl_color)
        surface.blit(lbl, (rx, r.y - 18))


class EdGem(EditorObject):
    kind = "gem"
    SIZE = 16

    def __init__(self, x: int, y: int, hidden: bool = False) -> None:
        super().__init__(x, y)
        self.hidden = hidden

    def get_rect(self) -> pygame.Rect:
        s = self.SIZE
        return pygame.Rect(self.x - s // 2, self.y - s // 2, s, s)

    def to_dict(self) -> dict:
        d = {"x": self.x, "y": self.y}
        if self.hidden:
            d["hidden"] = True
        return d

    def draw(self, surface: pygame.Surface, cam_x: int, font: pygame.font.Font) -> None:
        cx, cy = self.x - cam_x, self.y
        s      = self.SIZE
        color  = self._alpha_color(C_GEM)
        alpha  = 80 if self.hidden else 255
        pts    = [(cx, cy - s // 2), (cx + s // 2, cy),
                  (cx, cy + s // 2), (cx - s // 2, cy)]
        surf   = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*color[:3], alpha), pts)
        surface.blit(surf, (0, 0))
        if self.selected:
            lbl = font.render(f"({'隐 ' if self.hidden else ''}宝石)({self.x},{self.y})",
                              True, C_SELECT)
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


# ── 撤回历史 ─────────────────────────────────────────────────────────────────
class UndoStack:
    def __init__(self, max_steps: int = MAX_UNDO) -> None:
        self._stack: list[Any] = []
        self._max   = max_steps

    def push(self, state: Any) -> None:
        self._stack.append(copy.deepcopy(state))
        if len(self._stack) > self._max:
            self._stack.pop(0)

    def pop(self) -> Any | None:
        if len(self._stack) < 2:
            return None
        self._stack.pop()          # 丢弃当前状态
        return copy.deepcopy(self._stack[-1])

    def snapshot(self, state: Any) -> None:
        """与上一次不同才推入，避免重复快照。"""
        snap = copy.deepcopy(state)
        if not self._stack or snap != self._stack[-1]:
            self._stack.append(snap)
            if len(self._stack) > self._max:
                self._stack.pop(0)


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

        self.cam_x:   int = 0
        self.world_w: int = self._meta.get("world_w", SCREEN_W)
        self.cam_speed    = 6

        self.objects: list[EditorObject] = []
        self._import_objects()

        # 拖拽/缩放状态
        self._drag_obj:         EditorObject | None = None
        self._drag_off:         tuple[int, int]     = (0, 0)
        self._resize_obj:       EdPlatform | None   = None
        self._resize_orig:      tuple[int,int,int,int] = (0,0,0,0)
        self._resize_mouse_start: tuple[int,int]    = (0,0)

        # 撤回栈
        self._undo = UndoStack()
        self._snapshot()   # 初始状态

        self._status = "就绪  [P]平台 [N]NPC [G]宝石 [H]隐藏 [S]保存 [Ctrl+Z]撤回 [ESC]退出"

    # ── JSON ─────────────────────────────────────────────────────────────
    def _load_json(self) -> None:
        with open(self.json_path, encoding="utf-8") as f:
            self._data = json.load(f)
        self._meta = self._data.get("meta", {})

    def _import_objects(self) -> None:
        d = self._data
        sp = d.get("player_spawn", {"x": 80, "y": SCREEN_H - 40})
        self.objects.append(EdSpawn(sp["x"], sp["y"]))
        for p in d.get("platforms", []):
            self.objects.append(EdPlatform(
                p["x"], p["y"], p["w"], p["h"],
                p.get("sprite_key", "default"),
                hidden=p.get("hidden", False)))
        for n in d.get("npcs", []):
            self.objects.append(EdNPC(
                n["x"], n["y"],
                n.get("name", "NPC"),
                n.get("sprite_key", "default"),
                n.get("dialogue_key", "guide"),
                hidden=n.get("hidden", False)))
        for g in d.get("gems", []):
            self.objects.append(EdGem(g["x"], g["y"],
                                      hidden=g.get("hidden", False)))

    def _save(self) -> None:
        out: dict = {"meta": {**self._meta, "world_w": self.world_w}}
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
        self._status = f"已保存 -> {self.json_path}"

    # ── 撤回快照 ─────────────────────────────────────────────────────────
    def _snapshot(self) -> None:
        state = [(o.kind, o.to_dict(), o.hidden) for o in self.objects]
        self._undo.snapshot(state)

    def _undo_action(self) -> None:
        state = self._undo.pop()
        if state is None:
            self._status = "已到最早状态"
            return
        self.objects.clear()
        for kind, d, hidden in state:
            obj = _dict_to_obj(kind, d)
            if obj:
                obj.hidden = hidden
                self.objects.append(obj)
        self._status = "已撤回"

    # ── 选中 ─────────────────────────────────────────────────────────────
    def _pick(self, wx: int, wy: int) -> EditorObject | None:
        for obj in reversed(self.objects):
            if obj.get_rect().collidepoint(wx, wy):
                return obj
        return None

    def _pick_resize_handle(self, wx: int, wy: int) -> EdPlatform | None:
        for obj in reversed(self.objects):
            if isinstance(obj, EdPlatform):
                if obj.resize_handle_rect().collidepoint(wx, wy):
                    return obj
        return None

    def _deselect_all(self) -> None:
        for obj in self.objects:
            obj.selected = False

    # ── 主循环 ────────────────────────────────────────────────────────────
    def run(self) -> None:
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    ctrl = (pygame.key.get_mods() &
                            (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL))
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif ctrl and event.key == pygame.K_z:
                        self._undo_action()
                    elif event.key == pygame.K_s and not ctrl:
                        self._save()
                    elif event.key == pygame.K_p:
                        self._add_platform()
                    elif event.key == pygame.K_n:
                        self._add_npc()
                    elif event.key == pygame.K_g:
                        self._add_gem()
                    elif event.key == pygame.K_h:
                        self._toggle_hidden()
                    elif event.key == pygame.K_DELETE:
                        self._snapshot()
                        self.objects = [o for o in self.objects
                                        if not o.selected or o.kind == "spawn"]
                        self._status = "已删除选中物体"

                elif event.type == pygame.MOUSEWHEEL:
                    # 鼠标滚轮横向滚动（Shift+滚轮 或 直接横向滚动）
                    scroll = event.x if event.x != 0 else -event.y
                    self.cam_x = max(0,
                                     min(max(0, self.world_w - SCREEN_W),
                                         self.cam_x + scroll * 20))

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if my < TOOLBAR_H:
                        continue
                    wx = mx + self.cam_x
                    wy = my
                    if event.button == 1:
                        robj = self._pick_resize_handle(wx, wy)
                        if robj:
                            self._snapshot()
                            self._resize_obj          = robj
                            self._resize_orig         = (robj.x, robj.y, robj.w, robj.h)
                            self._resize_mouse_start  = (wx, wy)
                        else:
                            obj = self._pick(wx, wy)
                            self._deselect_all()
                            if obj:
                                obj.selected   = True
                                self._snapshot()
                                self._drag_obj = obj
                                self._drag_off = (wx - obj.x, wy - obj.y)
                            else:
                                self._drag_obj = None
                    elif event.button == 3:
                        obj = self._pick(wx, wy)
                        if obj and obj.kind != "spawn":
                            self._snapshot()
                            self.objects.remove(obj)
                            self._status = "已删除"

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if self._drag_obj or self._resize_obj:
                            self._snapshot()
                        self._drag_obj   = None
                        self._resize_obj = None

                elif event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    wx = mx + self.cam_x
                    wy = my
                    if self._drag_obj:
                        self._drag_obj.x = wx - self._drag_off[0]
                        self._drag_obj.y = wy - self._drag_off[1]
                        self._status = f"({self._drag_obj.x}, {self._drag_obj.y})"
                    elif self._resize_obj:
                        ox, oy, ow, oh = self._resize_orig
                        dx = wx - self._resize_mouse_start[0]
                        dy = wy - self._resize_mouse_start[1]
                        self._resize_obj.w = max(20, ow + dx)
                        self._resize_obj.h = max(8,  oh + dy)
                        self._status = (f"尺寸 {self._resize_obj.w}"
                                        f"x{self._resize_obj.h}")

            # 事件队列抽干后再读按键状态，方向键持续滚动视图
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.cam_x = max(0, self.cam_x - self.cam_speed)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.cam_x = min(max(0, self.world_w - SCREEN_W),
                                 self.cam_x + self.cam_speed)

            self._draw()

        pygame.quit()

    # ── 添加物体 ──────────────────────────────────────────────────────────
    def _add_platform(self) -> None:
        cx = self.cam_x + SCREEN_W // 2
        self._deselect_all()
        p = EdPlatform(cx - 80, SCREEN_H // 2, 160, 20)
        p.selected = True
        self._snapshot()
        self.objects.append(p)
        self._status = "已添加平台"

    def _add_npc(self) -> None:
        cx = self.cam_x + SCREEN_W // 2
        self._deselect_all()
        n = EdNPC(cx, SCREEN_H - 40, name="NPC")
        n.selected = True
        self._snapshot()
        self.objects.append(n)
        self._status = "已添加 NPC"

    def _add_gem(self) -> None:
        cx = self.cam_x + SCREEN_W // 2
        self._deselect_all()
        g = EdGem(cx, SCREEN_H // 2)
        g.selected = True
        self._snapshot()
        self.objects.append(g)
        self._status = "已添加宝石"

    def _toggle_hidden(self) -> None:
        """切换所有选中物体的隐藏状态（出生点不可隐藏）。"""
        targets = [o for o in self.objects if o.selected and o.kind != "spawn"]
        if not targets:
            self._status = "请先选中物体再按 H 切换隐藏"
            return
        self._snapshot()
        for obj in targets:
            obj.hidden = not obj.hidden
        state = "隐藏" if targets[0].hidden else "显示"
        self._status = f"已切换为{state}（游戏中仍然有效）"

    # ── 渲染 ──────────────────────────────────────────────────────────────
    def _draw(self) -> None:
        self.screen.fill(C_BG)
        self._draw_grid()

        # 世界边界线
        rx = self.world_w - self.cam_x
        pygame.draw.line(self.screen, (200, 80, 80),
                         (rx, TOOLBAR_H), (rx, SCREEN_H), 2)
        wlbl = self.font_s.render(f"世界宽度 {self.world_w}px", True, (200, 80, 80))
        self.screen.blit(wlbl, (rx - wlbl.get_width() - 4, TOOLBAR_H + 4))

        for obj in self.objects:
            obj.draw(self.screen, self.cam_x, self.font)

        self._draw_toolbar()

    def _draw_grid(self) -> None:
        offset = self.cam_x % 60
        for x in range(-offset, SCREEN_W, 60):
            pygame.draw.line(self.screen, C_GRID, (x, TOOLBAR_H), (x, SCREEN_H))
        for y in range(TOOLBAR_H, SCREEN_H, 60):
            pygame.draw.line(self.screen, C_GRID, (0, y), (SCREEN_W, y))
        ox = -self.cam_x
        if 0 <= ox <= SCREEN_W:
            pygame.draw.line(self.screen, (80, 80, 120),
                             (ox, TOOLBAR_H), (ox, SCREEN_H), 2)

    def _draw_toolbar(self) -> None:
        pygame.draw.rect(self.screen, C_TOOLBAR, (0, 0, SCREEN_W, TOOLBAR_H))
        pygame.draw.line(self.screen, C_GRID, (0, TOOLBAR_H), (SCREEN_W, TOOLBAR_H))

        items = [
            (f"关卡: {self._meta.get('name', '')}",   C_TEXT),
            (f"视角: {self.cam_x}px",                  C_HINT),
            (f"物体: {len(self.objects)}",              C_HINT),
            (self._status,                              C_TEXT),
        ]
        x = 8
        for txt, color in items:
            s = self.font_s.render(txt, True, color)
            self.screen.blit(s, (x, (TOOLBAR_H - s.get_height()) // 2))
            x += s.get_width() + 20

        hint = self.font_s.render(
            "[←→/AD]滚动 [P]平台 [N]NPC [G]宝石 [H]隐藏 [Del]删除 [Ctrl+Z]撤回 [S]保存 [ESC]退出",
            True, C_HINT)
        self.screen.blit(hint, (SCREEN_W - hint.get_width() - 8,
                                (TOOLBAR_H - hint.get_height()) // 2))
        pygame.display.flip()


# ── 辅助函数 ──────────────────────────────────────────────────────────────────
def _lighten(color: tuple, amount: int) -> tuple:
    return tuple(min(255, v + amount) for v in color[:3])


def _dict_to_obj(kind: str, d: dict) -> EditorObject | None:
    """从 to_dict() 的结果重建物体（用于撤回）。"""
    if kind == "spawn":
        return EdSpawn(d["x"], d["y"])
    if kind == "platform":
        return EdPlatform(d["x"], d["y"], d.get("w", 160), d.get("h", 20),
                          d.get("sprite_key", "default"), d.get("hidden", False))
    if kind == "npc":
        return EdNPC(d["x"], d["y"], d.get("name", "NPC"),
                     d.get("sprite_key", "default"),
                     d.get("dialogue_key", "guide"),
                     d.get("hidden", False))
    if kind == "gem":
        return EdGem(d["x"], d["y"], d.get("hidden", False))
    return None


# ── 入口 ──────────────────────────────────────────────────────────────────────
def main() -> None:
    levels_dir = Path("levels")
    jsons = sorted(levels_dir.glob("*_layout.json"))

    if not jsons:
        print("未找到任何关卡文件（levels/*_layout.json）")
        sys.exit(1)

    print("=" * 44)
    print("  关卡可视化编辑器")
    print("=" * 44)
    for i, p in enumerate(jsons, 1):
        try:
            with open(p, encoding="utf-8") as f:
                name = json.load(f).get("meta", {}).get("name", p.stem)
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

    print(f"\n正在打开：{chosen}")
    Editor(str(chosen)).run()


if __name__ == "__main__":
    main()
