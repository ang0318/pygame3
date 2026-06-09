"""
关卡 2 —— 跳跃 + 问答进阶关
新玩法：
  1. 地图更宽，平台错落有致
  2. 地图中散落"知识宝石"（Collectible），踩到加分
  3. 终点 Boss NPC 有更多题目，且需要收集足够宝石才能挑战
过关条件：收集 ≥ 3 颗宝石 且 Boss 所有问答正确
"""
from __future__ import annotations
import pygame
from engine.scene_manager import SceneManager
from scenes.base_level    import BaseLevelScene
from entities.player      import Player
from entities.npc         import NPC
from entities.platform    import Platform


# ── 题库 ─────────────────────────────────────────────────────────────────────
_INTRO_DIALOGUE = [
    {"text": "关卡 2！收集 3 颗以上宝石，再来挑战我！"},
]

_BOSS_LOCKED = [
    {"text": "你还没收集到足够的宝石，先去探索地图吧！"},
]

_BOSS_DIALOGUE = [
    {"text": "不错，宝石收集达标！现在接受终极考验！"},
    {
        "text": "进阶题一：下列哪个是不可变（immutable）类型？",
        "choices": ["list", "dict", "tuple", "set"],
        "answer": 2,
    },
    {
        "text": "进阶题二：O(n log n) 是哪种排序算法的平均复杂度？",
        "choices": ["冒泡排序", "插入排序", "快速排序", "选择排序"],
        "answer": 2,
    },
    {
        "text": "进阶题三：pygame 中检测矩形碰撞用哪个方法？",
        "choices": ["rect.hit()", "rect.colliderect()", "rect.overlap()", "rect.touch()"],
        "answer": 1,
    },
    {"text": "全部正确！你已通关所有关卡！感谢游玩！"},
]


# ── 宝石实体（轻量，直接写在 level2） ─────────────────────────────────────
class Gem(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, color: tuple = (249, 226, 175)) -> None:
        super().__init__()
        self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
        # 菱形
        pts = [(9, 0), (18, 9), (9, 18), (0, 9)]
        pygame.draw.polygon(self.image, color, pts)
        pygame.draw.polygon(self.image, (255, 255, 255), pts, 2)
        self.rect     = self.image.get_rect(center=(x, y))
        self._base_y  = float(y)
        self._timer   = 0.0

    def update(self, dt: float) -> None:   # type: ignore[override]
        self._timer += dt
        import math
        self.rect.centery = int(self._base_y + math.sin(self._timer * 3) * 5)


# ── 关卡 2 场景 ───────────────────────────────────────────────────────────────
class Level2Scene(BaseLevelScene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.hud.level_name = "关卡 2 · 跳跃挑战"
        self._world_w       = 2400
        self.gems:           pygame.sprite.Group = pygame.sprite.Group()
        self._gem_count      = 0
        self._gem_required   = 3
        self._boss_talked    = False

    # ── 构建关卡 ─────────────────────────────────────────────────────────
    def _build_level(self) -> None:
        cfg = self.settings
        H   = cfg.SCREEN_H

        # ── 平台布局 ─────────────────────────────────────────────────────
        platforms_data = [
            # (x,   y,        w,   h)
            (0,    H - 40,  2400, 40),   # 地面
            (200,  H - 130,  160, 16),
            (420,  H - 200,  160, 16),
            (640,  H - 290,  160, 16),
            (860,  H - 200,  200, 16),
            (1100, H - 310,  180, 16),
            (1340, H - 240,  200, 16),
            (1580, H - 340,  180, 16),
            (1800, H - 260,  220, 16),
            (2050, H - 370,  180, 16),
            (2250, H - 300,  140, 16),   # Boss 站台下方
            (2200, H - 420,  200, 20),   # Boss 站台
        ]
        for x, y, w, h in platforms_data:
            self.platforms.add(Platform(x, y, w, h, cfg))

        # ── 玩家出生点 ───────────────────────────────────────────────────
        self.player = Player(60, H - 40, cfg)

        # ── 宝石散布 ─────────────────────────────────────────────────────
        gems_pos = [
            (280,  H - 155),
            (500,  H - 225),
            (720,  H - 315),
            (940,  H - 225),
            (1180, H - 335),
            (1660, H - 365),
            (1880, H - 285),
        ]
        for gx, gy in gems_pos:
            self.gems.add(Gem(gx, gy))

        # ── NPC ─────────────────────────────────────────────────────────
        intro_npc = NPC(160, H - 40, _INTRO_DIALOGUE, cfg, name="路标")
        self._boss = NPC(2280, H - 420, _BOSS_DIALOGUE, cfg, name="最终 Boss")
        self.npcs  = [intro_npc, self._boss]

    # ── on_enter ─────────────────────────────────────────────────────────
    def on_enter(self) -> None:
        self.gems      = pygame.sprite.Group()
        self._gem_count = 0
        self._boss_talked = False
        super().on_enter()
        self.bus.subscribe("level_complete", self._on_win)

    def on_exit(self) -> None:
        self.bus.unsubscribe("level_complete", self._on_win)

    # ── 更新 ─────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        self.gems.update(dt)
        # 收集宝石
        if self.player:
            hit = pygame.sprite.spritecollide(self.player, self.gems, True)
            for _ in hit:
                self._gem_count  += 1
                self.hud.score   += 50
        super().update(dt)
        self.hud.level_name = f"关卡 2 · 宝石 {self._gem_count}/{self._gem_required}"

    # ── 事件（拦截 Boss 挑战条件） ────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.dialogue.active and event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if self.player:
                for npc in self.npcs:
                    dist = abs(npc.rect.centerx - self.player.rect.centerx)
                    if dist < NPC.INTERACT_DIST and not npc.talking and not npc.finished:
                        if npc is self._boss and self._gem_count < self._gem_required:
                            # 宝石不足，弹出提示
                            from entities.npc import NPC as _NPC
                            tmp = _NPC(npc.rect.x, npc.rect.y,
                                       _BOSS_LOCKED, self.settings, name="最终 Boss")
                            self._active_npc = tmp   # 临时 NPC，不加入 self.npcs
                            self.dialogue.open(_BOSS_LOCKED[0]["text"])
                            return
        super().handle_event(event)

    # ── 渲染 ─────────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)
        cx = int(self._cam_x)
        for gem in self.gems:
            screen.blit(gem.image, (gem.rect.x - cx, gem.rect.y))

        # 宝石计数角标
        font = self.assets.font(self.settings.FONT_NAME, 18)
        gem_txt = font.render(f"宝石 {self._gem_count} / {self._gem_required}", True,
                              self.settings.COLOR_GOLD)
        screen.blit(gem_txt, (12, self.settings.SCREEN_H - 30))

    # ── 过关 ─────────────────────────────────────────────────────────────
    def _on_all_npc_done(self) -> None:
        self.bus.emit("level_complete", {"next": "win"})

    def _on_win(self, data: dict) -> None:
        if data and data.get("next") == "win":
            from scenes.win_scene import WinScene
            self.manager.replace(WinScene(self.manager, self.hud.score))
