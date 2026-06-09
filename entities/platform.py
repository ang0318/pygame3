"""平台实体 —— 静态碰撞体，支持颜色/尺寸参数化"""
from __future__ import annotations
import pygame
from engine.settings import Settings


class Platform(pygame.sprite.Sprite):
    """
    通用静态平台。
    后期可派生出：移动平台、可破坏平台、传送平台等子类。
    """

    def __init__(self, x: int, y: int, w: int, h: int,
                 settings: Settings,
                 color: tuple | None = None) -> None:
        super().__init__()
        c          = color or settings.COLOR_PLATFORM
        self.image = pygame.Surface((w, h))
        self.image.fill(c)
        # 简单高光
        pygame.draw.rect(self.image, _lighten(c, 40), (0, 0, w, 4))
        self.rect  = self.image.get_rect(topleft=(x, y))


def _lighten(color: tuple, amount: int) -> tuple:
    return tuple(min(255, v + amount) for v in color)
