"""资源加载器 —— 带缓存，避免重复 IO"""
from __future__ import annotations
import pygame


class AssetLoader:
    """懒加载 + 内存缓存，支持图片、音效、字体。"""

    def __init__(self) -> None:
        self._images: dict[str, pygame.Surface] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._fonts:  dict[tuple, pygame.font.Font] = {}

    # ── 图片 ────────────────────────────────────────────────────────────────
    def image(self, path: str, convert_alpha: bool = True) -> pygame.Surface:
        if path not in self._images:
            surf = pygame.image.load(path)
            self._images[path] = surf.convert_alpha() if convert_alpha else surf.convert()
        return self._images[path]

    # ── 音效 ────────────────────────────────────────────────────────────────
    def sound(self, path: str) -> pygame.mixer.Sound:
        if path not in self._sounds:
            self._sounds[path] = pygame.mixer.Sound(path)
        return self._sounds[path]

    # ── 字体 ────────────────────────────────────────────────────────────────
    def font(self, name: str | None, size: int) -> pygame.font.Font:
        """
        name: SysFont 名称字符串（如 'microsoftyahei'）或 None（回退到默认字体）。
        统一用 SysFont 以支持中文字符。
        """
        key = (name, size)
        if key not in self._fonts:
            if name:
                f = pygame.font.SysFont(name, size)
            else:
                f = pygame.font.SysFont("microsoftyahei", size)
            self._fonts[key] = f
        return self._fonts[key]

    def clear(self) -> None:
        self._images.clear()
        self._sounds.clear()
        self._fonts.clear()
