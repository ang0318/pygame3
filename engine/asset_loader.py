"""
资源加载器 —— 带缓存 + 素材热插拔 + 关卡独立素材优先
查找顺序（三级降级）：
  1. assets/levels/levelN/<filename>   关卡专属素材
  2. assets/<filename>                 通用素材
  3. 同尺寸颜色色块                    兜底，永不报错
"""
from __future__ import annotations
import pygame
from pathlib import Path


class AssetLoader:

    def __init__(self) -> None:
        self._images: dict[str, pygame.Surface] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._fonts:  dict[tuple, pygame.font.Font] = {}
        self._level_prefix: str = ""   # 当前关卡目录前缀，如 "assets/levels/level1/"

    # ── 关卡上下文 ────────────────────────────────────────────────────────
    def set_level(self, level_id: str | int | None) -> None:
        """
        切换当前关卡上下文。
        level_id = 1  → 专属目录 assets/levels/level1/
        level_id = None → 只查通用目录
        调用时机：关卡场景 on_enter()。
        """
        if level_id is not None:
            self._level_prefix = f"assets/levels/level{level_id}/"
        else:
            self._level_prefix = ""

    # ── 字体 ─────────────────────────────────────────────────────────────
    def font(self, name: str | None, size: int) -> pygame.font.Font:
        key = (name, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.SysFont(name or "microsoftyahei", size)
        return self._fonts[key]

    # ── 图片（严格加载） ──────────────────────────────────────────────────
    def image(self, path: str, convert_alpha: bool = True) -> pygame.Surface:
        if path not in self._images:
            surf = pygame.image.load(path)
            self._images[path] = surf.convert_alpha() if convert_alpha else surf.convert()
        return self._images[path]

    # ── 图片（安全加载，三级降级） ────────────────────────────────────────
    def safe_image(self,
                   filename: str,
                   fallback_size: tuple[int, int],
                   fallback_color: tuple,
                   convert_alpha: bool = True) -> pygame.Surface:
        """
        filename: 相对于 assets/ 的文件名，如 "player_idle_0.png"
                  也可以传完整路径（以 assets/ 开头），会自动解析文件名部分。
        查找顺序：
          1. assets/levels/levelN/<basename>
          2. assets/<basename>（或原始完整路径）
          3. 色块兜底
        """
        # 兼容旧调用（传完整路径）
        basename = Path(filename).name

        candidates = []
        if self._level_prefix:
            candidates.append(self._level_prefix + basename)
        candidates.append(f"assets/{basename}")
        # 也支持传入带子目录的原始路径
        if "/" in filename and not filename.startswith("assets/"):
            candidates.append(filename)

        for path in candidates:
            if path in self._images:
                return self._images[path]
            if Path(path).exists():
                try:
                    surf = pygame.image.load(path)
                    surf = surf.convert_alpha() if convert_alpha else surf.convert()
                    self._images[path] = surf
                    return surf
                except Exception:
                    pass

        # 色块兜底
        fb_key = f"__fallback_{basename}_{fallback_size}_{fallback_color}"
        if fb_key not in self._images:
            surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
            surf.fill(fallback_color)
            self._images[fb_key] = surf
        return self._images[fb_key]

    # ── 帧动画序列 ────────────────────────────────────────────────────────
    def frames(self,
               pattern: str,
               count: int,
               fallback_size: tuple[int, int],
               fallback_color: tuple,
               convert_alpha: bool = True) -> list[pygame.Surface]:
        """
        pattern 含 {} 占位符，如 "player_run_{}.png"
        也兼容旧格式完整路径，如 "assets/player_run_{}.png"
        """
        result = []
        for i in range(count):
            filename = pattern.format(i)
            result.append(self.safe_image(filename, fallback_size,
                                          fallback_color, convert_alpha))
        return result

    # ── 音效（安全加载） ──────────────────────────────────────────────────
    def sound(self, filename: str) -> pygame.mixer.Sound | None:
        basename = Path(filename).name
        candidates = []
        if self._level_prefix:
            candidates.append(self._level_prefix + basename)
        candidates.append(f"assets/{basename}")

        for path in candidates:
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
        self._level_prefix = ""
