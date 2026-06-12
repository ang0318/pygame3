"""
关卡 3 场景 —— 星星接接乐
玩法：从屏幕顶部随机位置持续落下"星星"，玩家在底部平台上
      左右移动接住星星。接满 REQUIRED 颗后找守门人答题，全对即过关。

特色机制：
  - FallingItem：星星从随机 x 坐标、屏幕顶部生成，匀加速落下
  - 落到底部未接住则扣分（最低 0）并显示短暂的"miss"特效
  - 关卡无横向滚动（world_w = SCREEN_W），摄像机固定
  - 加速曲线：随接住数量增多，生成速率与下落速度逐渐提升
"""
from __future__ import annotations

import math
import random
import pygame

from engine.scene_manager import SceneManager
from engine.level_loader  import LevelLoader
from scenes.base_level    import BaseLevelScene
from entities.npc         import NPC
from levels.level3.dialogues import DIALOGUES, GATEKEEPER_LOCKED


# ── 星星实体 ──────────────────────────────────────────────────────────────────

class FallingItem(pygame.sprite.Sprite):
    """从屏幕顶部落下的星星。"""

    # 颜色池：每颗星随机选一种
    COLORS = [
        (249, 226, 175),   # 金
        (137, 220, 235),   # 青
        (166, 227, 161),   # 绿
        (250, 179, 135),   # 橙
        (203, 166, 247),   # 紫
        (243, 139, 168),   # 粉
    ]

    SIZE = 20   # 碰撞框边长（像素）

    def __init__(self, screen_w: int, speed: float) -> None:
        super().__init__()
        self._color  = random.choice(self.COLORS)
        self._angle  = 0.0           # 自转角度（纯视觉）
        self._speed  = speed         # 下落速度（px/s）

        # 构造五角星 Surface
        self.image = self._make_star(self.SIZE, self._color)
        # 随机水平位置，留边距避免贴边
        x = random.randint(self.SIZE, screen_w - self.SIZE)
        self.rect  = self.image.get_rect(midtop=(x, -self.SIZE))
        self._pos_y = float(self.rect.y)

    # ── 绘制五角星 ────────────────────────────────────────────────────────
    @staticmethod
    def _make_star(size: int, color: tuple,
                   angle_offset: float = 0.0) -> pygame.Surface:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size / 2, size / 2
        r_outer = size / 2
        r_inner = size / 4.5
        pts = []
        for i in range(10):
            angle = math.radians(angle_offset - 90 + i * 36)
            r = r_outer if i % 2 == 0 else r_inner
            pts.append((cx + r * math.cos(angle),
                        cy + r * math.sin(angle)))
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.polygon(surf, (255, 255, 255), pts, 1)
        return surf

    def update(self, dt: float) -> None:   # type: ignore[override]
        self._pos_y  += self._speed * dt
        self._angle   = (self._angle + 120 * dt) % 360   # 旋转效果
        self.rect.y   = int(self._pos_y)
        # 每帧重绘旋转后的星星
        self.image = self._make_star(self.SIZE, self._color, self._angle)


# ── Miss 特效（短暂显示在漏接位置） ──────────────────────────────────────────

class MissEffect:
    """在漏接位置显示淡出的 "miss!" 文字。"""

    DURATION = 0.8   # 秒

    def __init__(self, x: int, y: int, font: pygame.font.Font) -> None:
        self.x     = x
        self.y     = y
        self._font = font
        self._t    = 0.0
        self.done  = False

    def update(self, dt: float) -> None:
        self._t += dt
        if self._t >= self.DURATION:
            self.done = True

    def draw(self, screen: pygame.Surface) -> None:
        if self.done:
            return
        alpha   = max(0, int(255 * (1 - self._t / self.DURATION)))
        surf    = self._font.render("miss!", True, (243, 139, 168))
        surf.set_alpha(alpha)
        # 向上浮动
        oy = int(self._t / self.DURATION * 30)
        screen.blit(surf, (self.x - surf.get_width() // 2, self.y - oy))


# ── 关卡 3 场景 ───────────────────────────────────────────────────────────────

class Level3Scene(BaseLevelScene):
    """
    过关条件：接住 >= ITEM_REQUIRED 颗星星，且守门人问答全部正确。
    """

    ITEM_REQUIRED    = 10      # 需要接住的星星数
    SPAWN_INTERVAL   = 1.8     # 初始生成间隔（秒）
    SPAWN_INTERVAL_MIN = 0.45  # 最短生成间隔（秒）
    ITEM_SPEED_BASE  = 130.0   # 初始下落速度（px/s）
    ITEM_SPEED_MAX   = 320.0   # 最高下落速度（px/s）

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self._level_asset_id = 3
        self._bg_image_key   = "bg_level3.png"   # 不存在时自动降级为纯色
        self.hud.level_name  = "关卡 3 - 星星接接乐"

        self._items:        pygame.sprite.Group = pygame.sprite.Group()
        self._miss_effects: list[MissEffect]    = []

        self._caught   = 0         # 已接住数
        self._missed   = 0         # 漏接数
        self._spawn_t  = 0.0       # 累计生成计时
        self._gatekeeper: NPC | None = None

    # ── 构建关卡 ─────────────────────────────────────────────────────────
    def _build_level(self) -> None:
        expanded = {k: self.expand_dialogue(v) for k, v in DIALOGUES.items()}
        loader   = LevelLoader(
            "levels/level3/layout.json",
            self.settings, self.assets, expanded,
        )
        loader.build(self.platforms, self.npcs)
        self.player      = loader.player
        self._world_w    = loader.world_w

        # 守门人是 npcs 中 optional=False 的那位（最后一个）
        self._gatekeeper = next(
            (n for n in reversed(self.npcs)
             if not getattr(n, "optional", False)),
            None,
        )

    # ── on_enter ─────────────────────────────────────────────────────────
    def on_enter(self) -> None:
        self._items        = pygame.sprite.Group()
        self._miss_effects = []
        self._caught       = 0
        self._missed       = 0
        self._spawn_t      = 0.0
        super().on_enter()

    # ── 当前难度参数 ──────────────────────────────────────────────────────
    def _current_interval(self) -> float:
        """随接住数线性缩短生成间隔。"""
        ratio    = min(self._caught / self.ITEM_REQUIRED, 1.0)
        interval = self.SPAWN_INTERVAL - ratio * (self.SPAWN_INTERVAL - self.SPAWN_INTERVAL_MIN)
        return max(interval, self.SPAWN_INTERVAL_MIN)

    def _current_speed(self) -> float:
        """随接住数线性提升下落速度。"""
        ratio = min(self._caught / self.ITEM_REQUIRED, 1.0)
        return self.ITEM_SPEED_BASE + ratio * (self.ITEM_SPEED_MAX - self.ITEM_SPEED_BASE)

    # ── 更新 ─────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        # 对话激活时暂停物品生成与下落
        if self.dialogue.active:
            super().update(dt)
            return

        # 生成新星星
        self._spawn_t += dt
        if self._spawn_t >= self._current_interval():
            self._spawn_t -= self._current_interval()
            self._items.add(
                FallingItem(self.settings.SCREEN_W, self._current_speed())
            )

        # 更新所有星星
        self._items.update(dt)

        # 检测玩家接住
        if self.player:
            caught = pygame.sprite.spritecollide(self.player, self._items, True)
            for _ in caught:
                self._caught += 1
                self.hud.score += 30

        # 检测漏接（落出底部）
        for item in list(self._items):
            if item.rect.top > self.settings.SCREEN_H:
                self._miss_effects.append(
                    MissEffect(item.rect.centerx,
                               self.settings.SCREEN_H - 20,
                               self._font_small)
                )
                item.kill()
                self._missed += 1
                self.hud.score = max(0, self.hud.score - 10)

        # 更新 miss 特效
        for eff in self._miss_effects[:]:
            eff.update(dt)
            if eff.done:
                self._miss_effects.remove(eff)

        # 基类（玩家物理、NPC、摄像机、过关检测）
        super().update(dt)

        # 动态 HUD 标题
        self.hud.level_name = (
            f"关卡 3 - 接住 {self._caught}/{self.ITEM_REQUIRED}  "
            f"漏接 {self._missed}"
        )

    # ── 事件（守门人门槛检查） ────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> None:
        if (not self.dialogue.active
                and event.type == pygame.KEYDOWN
                and event.key == pygame.K_e
                and self.player
                and self._gatekeeper):
            gk   = self._gatekeeper
            dist = abs(gk.rect.centerx - self.player.rect.centerx)
            if dist < NPC.INTERACT_DIST and not gk.talking and not gk.finished:
                if self._caught < self.ITEM_REQUIRED:
                    self.dialogue.open(GATEKEEPER_LOCKED[0]["text"])
                    return
        super().handle_event(event)

    # ── 渲染 ─────────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        self._draw_world(screen)

        # 星星（世界坐标，本关无横向滚动，cx 始终为 0）
        cx = int(self._cam_x)
        for item in self._items:
            screen.blit(item.image,
                        (item.rect.x - cx, item.rect.y))

        # Miss 特效（屏幕坐标）
        for eff in self._miss_effects:
            eff.draw(screen)

        # 底部进度条：接住数 / 需求数
        self._draw_progress(screen)

        self.dialogue.draw(screen)

    def _draw_progress(self, screen: pygame.Surface) -> None:
        """在屏幕底部画接住进度条。"""
        W    = self.settings.SCREEN_W
        H    = self.settings.SCREEN_H
        bw   = 300          # 进度条宽
        bh   = 14
        bx   = (W - bw) // 2
        by   = H - 18
        fill = int(bw * min(self._caught / self.ITEM_REQUIRED, 1.0))

        # 背景槽
        pygame.draw.rect(screen, (60, 60, 80), (bx, by, bw, bh), border_radius=6)
        # 已填充
        if fill > 0:
            pygame.draw.rect(screen, self.settings.COLOR_GOLD,
                             (bx, by, fill, bh), border_radius=6)
        # 边框
        pygame.draw.rect(screen, (180, 180, 200), (bx, by, bw, bh), 2, border_radius=6)

        # 文字
        label = self._font_small.render(
            f"★ {self._caught} / {self.ITEM_REQUIRED}",
            True, self.settings.COLOR_GOLD,
        )
        screen.blit(label, (bx + bw + 8, by - 1))

    # ── 过关回调 ─────────────────────────────────────────────────────────
    def _on_all_npc_done(self) -> None:
        self.bus.emit("next_level")
