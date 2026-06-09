"""
资源加载器 —— 带缓存 + 素材热插拔
核心设计：
  safe_image(path, fallback_size, fallback_color)
    → 尝试加载图片，找不到/加载失败则返回对应尺寸的纯色 Surface
  frames(pattern, count, size, color)
    → 批量加载帧动画序列（如 player_run_0.png … player_run_3.png）
      任何一帧缺失都使用同尺寸色块代替，保证帧数量一致
"""
from __future__ import annotations
import pygame
from pathlib import Path


class AssetLoader:

    def __init__(self) -> None:
        self._images: dict[str, pygame.Surface] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._fonts:  dict[tuple, pygame.font.Font] = {}

    # ── 字体 ─────────────────────────────────────────────────────────────
    def font(self, name: str | None, size: int) -> pygame.font.Font:
        """用系统字体名称加载，统一走 SysFont 支持中文。"""
        key = (name, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.SysFont(name or "microsoftyahei", size)
        return self._fonts[key]

    # ── 图片（严格加载，抛异常） ──────────────────────────────────────────
    def image(self, path: str, convert_alpha: bool = True) -> pygame.Surface:
        if path not in self._images:
            surf = pygame.image.load(path)
            self._images[path] = surf.convert_alpha() if convert_alpha else surf.convert()
        return self._images[path]

    # ── 图片（安全加载，失败返回色块） ───────────────────────────────────
    def safe_image(self,
                   path: str,
                   fallback_size: tuple[int, int],
                   fallback_color: tuple[int, int, int] | tuple[int, int, int, int],
                   convert_alpha: bool = True) -> pygame.Surface:
        """
        尝试从 path 加载图片。
        若文件不存在或加载失败，返回 fallback_size 大小的 fallback_color 纯色 Surface。
        结果同样被缓存，键为 path（不存在时键为 path+"#fallback"）。
        """
        if path in self._images:
            return self._images[path]

        fb_key = path + "#fallback"
        if Path(path).exists():
            try:
                surf = pygame.image.load(path)
                surf = surf.convert_alpha() if convert_alpha else surf.convert()
                self._images[path] = surf
                return surf
            except Exception:
                pass

        # 生成/返回缓存色块
        if fb_key not in self._images:
            surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
            surf.fill(fallback_color)
            self._images[fb_key] = surf
        return self._images[fb_key]

    # ── 帧动画序列加载 ────────────────────────────────────────────────────
    def frames(self,
               pattern: str,
               count: int,
               fallback_size: tuple[int, int],
               fallback_color: tuple[int, int, int],
               convert_alpha: bool = True) -> list[pygame.Surface]:
        """
        批量加载帧序列。
        pattern 中须含 {} 作为帧编号占位符，例如：
            "assets/player_run_{}.png"  → 加载 _0 … _(count-1)
        任何一帧缺失都无缝替换为色块，保证返回长度恒等于 count。
        """
        result = []
        for i in range(count):
            path = pattern.format(i)
            result.append(self.safe_image(path, fallback_size, fallback_color, convert_alpha))
        return result

    # ── 音效 ─────────────────────────────────────────────────────────────
    def sound(self, path: str) -> pygame.mixer.Sound | None:
        """安全加载音效，失败返回 None（调用方自行判断）。"""
        if path in self._sounds:
            return self._sounds[path]
        if Path(path).exists():
            try:
                self._sounds[path] = pygame.mixer.Sound(path)
                return self._sounds[path]
            except Exception:
                pass
        return None

    def clear(self) -> None:
        self._images.clear()
        self._sounds.clear()
        self._fonts.clear()
