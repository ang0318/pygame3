"""
右上角音乐控制组件
- 图标全部纯代码绘制，不依赖任何图片文件
- 支持 M 键切换静音，, / . 键调节音量
- 点击控件也可切换静音
"""
from __future__ import annotations
import pygame
from engine.settings     import Settings
from engine.asset_loader import AssetLoader


def _draw_music_icon(surface: pygame.Surface,
                     cx: int, cy: int, r: int,
                     color: tuple, muted: bool) -> None:
    """在 surface 上绘制音符/静音图标（纯代码）。"""
    if not muted:
        # 音符：圆头 + 竖线 + 横线
        pygame.draw.circle(surface, color, (cx - r // 2, cy + r // 3), r // 3)
        pygame.draw.line(surface, color,
                         (cx - r // 6, cy + r // 3),
                         (cx - r // 6, cy - r // 2), 2)
        pygame.draw.line(surface, color,
                         (cx - r // 6, cy - r // 2),
                         (cx + r // 2, cy - r), 2)
        pygame.draw.circle(surface, color, (cx + r // 2, cy - r + r // 3), r // 3)
    else:
        # 静音：喇叭 + 叉
        pts = [(cx - r, cy - r // 3),
               (cx - r // 3, cy - r // 3),
               (cx, cy - r),
               (cx, cy + r),
               (cx - r // 3, cy + r // 3),
               (cx - r, cy + r // 3)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.line(surface, (243, 139, 168),
                         (cx + r // 3, cy - r // 2),
                         (cx + r, cy + r // 2), 2)
        pygame.draw.line(surface, (243, 139, 168),
                         (cx + r, cy - r // 2),
                         (cx + r // 3, cy + r // 2), 2)


class MusicControl:
    """右上角迷你音乐控制条（纯代码绘制，不依赖图片）。"""

    W, H   = 130, 28
    MARGIN = 8

    def __init__(self, settings: Settings, assets: AssetLoader) -> None:
        self.cfg    = settings
        self.muted  = False
        self.volume = 0.5

        self._font = assets.font(settings.FONT_NAME, 14)
        self.rect  = pygame.Rect(
            settings.SCREEN_W - self.W - self.MARGIN,
            self.MARGIN + 36,
            self.W, self.H,
        )

    # ── 事件 ─────────────────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self._toggle_mute(); return True
            if event.key == pygame.K_COMMA:
                self._set_volume(self.volume - 0.1); return True
            if event.key == pygame.K_PERIOD:
                self._set_volume(self.volume + 0.1); return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._toggle_mute(); return True
        return False

    def _toggle_mute(self) -> None:
        self.muted = not self.muted
        pygame.mixer.music.set_volume(0.0 if self.muted else self.volume)

    def _set_volume(self, v: float) -> None:
        self.volume = max(0.0, min(1.0, round(v, 1)))
        if not self.muted:
            pygame.mixer.music.set_volume(self.volume)

    # ── 渲染 ─────────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        # 背景
        bg = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        screen.blit(bg, self.rect.topleft)

        cx = self.rect.x + 14
        cy = self.rect.centery
        icon_color = (243, 139, 168) if self.muted else (166, 227, 161)
        _draw_music_icon(screen, cx, cy, 7, icon_color, self.muted)

        label = "静音" if self.muted else f"{int(self.volume * 100)}%"
        txt   = self._font.render(label, True, self.cfg.COLOR_TEXT)
        screen.blit(txt, (self.rect.x + 28, cy - txt.get_height() // 2))

        hint = self._font.render("[M] [,] [.]", True, (80, 80, 110))
        screen.blit(hint, (self.rect.right - hint.get_width() - 4,
                           cy - hint.get_height() // 2))
