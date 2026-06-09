"""NPC 实体 —— 带对话气泡、问答状态机"""
from __future__ import annotations
import pygame
from engine.settings import Settings


class NPC(pygame.sprite.Sprite):
    """
    NPC 携带一组问答数据，玩家靠近并按 E 时触发对话。
    对话数据格式（列表，按顺序播放）：
        [
          {"text": "你好！", "choices": None},                         # 纯叙述
          {"text": "2+2=?",  "choices": ["3","4","5"], "answer": 1},   # 问答，answer 为正确选项索引
        ]
    """

    INTERACT_DIST = 80   # 触发距离（像素）

    def __init__(self, x: float, y: float,
                 dialogue: list[dict],
                 settings: Settings,
                 name: str = "NPC") -> None:
        super().__init__()
        self.cfg      = settings
        self.dialogue = dialogue
        self.name     = name

        # 外观
        self.image = pygame.Surface((32, 48), pygame.SRCALPHA)
        self._draw_shape()
        self.rect  = self.image.get_rect(midbottom=(x, y))

        # 对话状态
        self.talking   = False
        self.step      = 0       # 当前对话步骤
        self.finished  = False   # 全部对话已完成

        # 悬浮提示计时（闪烁）
        self._hint_timer = 0.0

    # ── 外观 ──────────────────────────────────────────────────────────────
    def _draw_shape(self) -> None:
        self.image.fill((0, 0, 0, 0))
        c = self.cfg.COLOR_NPC
        pygame.draw.rect(self.image, c, (8, 16, 16, 26), border_radius=4)
        pygame.draw.circle(self.image, c, (16, 12), 10)
        # 叹号标记
        pygame.draw.circle(self.image, self.cfg.COLOR_GOLD, (16, 2), 3)

    # ── 更新 ──────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:  # type: ignore[override]
        self._hint_timer += dt

    # ── 渲染 ──────────────────────────────────────────────────────────────
    def draw_hint(self, screen: pygame.Surface,
                  font: pygame.font.Font,
                  player_rect: pygame.Rect) -> None:
        """玩家足够近时显示 [E] 互动提示。"""
        if self.talking or self.finished:
            return
        dist = abs(self.rect.centerx - player_rect.centerx)
        if dist < self.INTERACT_DIST:
            alpha = 255 if int(self._hint_timer * 3) % 2 == 0 else 140
            surf  = font.render("[E] 对话", True, self.cfg.COLOR_GOLD)
            surf.set_alpha(alpha)
            pos   = (self.rect.centerx - surf.get_width() // 2,
                     self.rect.top - 24)
            screen.blit(surf, pos)

    # ── 互动 ──────────────────────────────────────────────────────────────
    def try_interact(self, player_rect: pygame.Rect) -> bool:
        """返回 True 表示成功开启对话。"""
        if self.finished:
            return False
        dist = abs(self.rect.centerx - player_rect.centerx)
        if dist < self.INTERACT_DIST and not self.talking:
            self.talking = True
            self.step    = 0
            return True
        return False

    @property
    def current_dialogue(self) -> dict | None:
        if self.step < len(self.dialogue):
            return self.dialogue[self.step]
        return None

    def advance(self) -> bool:
        """推进到下一句，返回 False 表示对话已全部结束。"""
        self.step += 1
        if self.step >= len(self.dialogue):
            self.talking  = False
            self.finished = True
            return False
        return True
