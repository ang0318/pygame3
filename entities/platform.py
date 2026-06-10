"""
平台实体 —— 静态碰撞体，支持贴图/纯色自动降级
素材约定（缺失则使用纯色）：
  assets/platform_{key}.png   平台贴图，key 由调用方传入（如 "grass"、"stone"）
建议宽高与平台尺寸一致，或使用可平铺纹理。
"""
from __future__ import annotations
import pygame
from engine.settings     import Settings
from engine.asset_loader import AssetLoader


class Platform(pygame.sprite.Sprite):
    """
    通用静态平台。
    有素材时将素材平铺到目标尺寸；无素材时退回纯色 + 高光。
    后期可派生出移动平台、可破坏平台等子类。
    """

    def __init__(self, x: int, y: int, w: int, h: int,
                 settings: Settings,
                 color: tuple | None = None,
                 sprite_key: str = "default",
                 assets: AssetLoader | None = None,
                 hidden: bool = False) -> None:
        super().__init__()
        c = color or settings.COLOR_PLATFORM

        if hidden:
            # 隐形平台：完全透明 surface，保留 rect 碰撞体
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))
        elif assets:
            tile = assets.safe_image(
                f"assets/platform_{sprite_key}.png",
                fallback_size=(w, h),
                fallback_color=c,
            )
            # 将纹理平铺到目标尺寸
            self.image = _tile_surface(tile, w, h)
        else:
            self.image = _make_plain(w, h, c)

        self.rect = self.image.get_rect(topleft=(x, y))


# ── 辅助函数 ──────────────────────────────────────────────────────────────────
def _make_plain(w: int, h: int, color: tuple) -> pygame.Surface:
    surf = pygame.Surface((w, h))
    surf.fill(color)
    pygame.draw.rect(surf, _lighten(color, 40), (0, 0, w, 4))
    return surf


def _tile_surface(tile: pygame.Surface, w: int, h: int) -> pygame.Surface:
    """将 tile 重复平铺到 (w, h) 画布上。"""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    tw, th = tile.get_size()
    for tx in range(0, w, tw):
        for ty in range(0, h, th):
            surf.blit(tile, (tx, ty))
    return surf


def _lighten(color: tuple, amount: int) -> tuple:
    return tuple(min(255, v + amount) for v in color[:3])
