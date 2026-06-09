"""
右上角音乐控制组件
支持：背景音乐开关、音量调节（左右键）
素材约定（缺失则用文字代替）：
  assets/icon_music_on.png   18×18 px
  assets/icon_music_off.png  18×18 px
"""
from __future__ import annotations
import pygame
from engine.settings     import Settings
from engine.asset_loader import AssetLoader


class MusicControl:
    """
    贴在屏幕右上角的迷你音乐控制条。
    调用方负责在每帧 draw()，并把事件传给 handle_event()。
    """

    W, H = 120, 28
    MARGIN = 8

    def __init__(self, settings: Settings, assets: AssetLoader) -> None:
        self.cfg    = settings
        self.assets = assets
        self.muted  = False
        self.volume = 0.5      # 0.0 ~ 1.0

        self._font  = assets.font(settings.FONT_NAME, 14)
        self.rect   = pygame.Rect(
            settings.SCREEN_W - self.W - self.MARGIN,
            self.MARGIN + 36,   # 顶栏下方
            self.W, self.H,
        )

        # 图标（缺失时用文字）
        icon_size = (18, 18)
        self._icon_on  = assets.safe_image(
            "assets/icon_music_on.png",  icon_size, (166, 227, 161))
        self._icon_off = assets.safe_image(
            "assets/icon_music_off.png", icon_size, (243, 139, 168))

    # ── 事件 ─────────────────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> bool:
        """返回 True 表示事件已被消费。"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self._toggle_mute()
                return True
            if event.key == pygame.K_COMMA:   # < 减音量
                self._set_volume(self.volume - 0.1)
                return True
            if event.key == pygame.K_PERIOD:  # > 加音量
                self._set_volume(self.volume + 0.1)
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._toggle_mute()
                return True
        return False

    # ── 控制 ─────────────────────────────────────────────────────────────
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
        bg.fill((0, 0, 0, 140))
        screen.blit(bg, self.rect.topleft)

        x, y = self.rect.x + 4, self.rect.y + 5
        # 图标
        icon = self._icon_off if self.muted else self._icon_on
        screen.blit(icon, (x, y))

        # 文字
        label = "静音" if self.muted else f"音量 {int(self.volume * 100)}%"
        txt   = self._font.render(label, True, self.cfg.COLOR_TEXT)
        screen.blit(txt, (x + 22, y + 1))

        # 提示
        hint = self._font.render("[M]", True, (100, 100, 130))
        screen.blit(hint, (self.rect.right - hint.get_width() - 4, y + 1))
