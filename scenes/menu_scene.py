"""主菜单场景"""
from __future__ import annotations
import pygame
from engine.scene_manager import BaseScene, SceneManager


class MenuScene(BaseScene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self._font_big   = self.assets.font(self.settings.FONT_NAME, 52)
        self._font_small = self.assets.font(self.settings.FONT_NAME, 26)
        self._options    = ["开始游戏 (关卡 1)", "退出"]
        self._sel        = 0
        self._bg_y       = 0.0   # 视差背景偏移

    def on_enter(self) -> None:
        self._sel = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._sel = (self._sel - 1) % len(self._options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._sel = (self._sel + 1) % len(self._options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._confirm()

    def _confirm(self) -> None:
        if self._sel == 0:
            self.bus.emit("start_game")   # main.py 监听，通过 LevelRegistry 启动第一关
        else:
            self.bus.emit("quit")

    def update(self, dt: float) -> None:
        self._bg_y = (self._bg_y + 20 * dt) % self.settings.SCREEN_H

    def draw(self, screen: pygame.Surface) -> None:
        # 背景图（assets/bg_menu.png 或任意支持格式，缺失则降级到网格动效）
        bg = self.assets.safe_image(
            "bg_menu.png",
            (self.settings.SCREEN_W, self.settings.SCREEN_H),
            self.settings.COLOR_BG,
        )
        # 判断是否真的加载到了图片（非色块）
        # safe_image 缺失时返回纯色 Surface，尺寸与 fallback_size 相同
        # 通过检查是否存在文件来决定渲染方式
        from pathlib import Path
        if Path("assets/bg_menu.png").exists():
            bg = pygame.transform.scale(
                bg, (self.settings.SCREEN_W, self.settings.SCREEN_H))
            screen.blit(bg, (0, 0))
        else:
            screen.fill(self.settings.COLOR_BG)
            self._draw_grid(screen)

        # 标题
        title = self._font_big.render(self.settings.TITLE, True, self.settings.COLOR_GOLD)
        screen.blit(title, (self.settings.SCREEN_W // 2 - title.get_width() // 2, 100))

        # 菜单项
        for i, opt in enumerate(self._options):
            color = self.settings.COLOR_GOLD if i == self._sel else self.settings.COLOR_TEXT
            prefix = ">> " if i == self._sel else "   "
            s = self._font_small.render(prefix + opt, True, color)
            screen.blit(s, (self.settings.SCREEN_W // 2 - s.get_width() // 2, 240 + i * 52))

        # 操作提示
        hint = self._font_small.render("↑↓ 选择   Enter 确认", True, (100, 100, 130))
        screen.blit(hint, (self.settings.SCREEN_W // 2 - hint.get_width() // 2,
                           self.settings.SCREEN_H - 40))

    def _draw_grid(self, screen: pygame.Surface) -> None:
        """背景网格动效"""
        c = (40, 40, 60)
        for x in range(0, self.settings.SCREEN_W, 60):
            pygame.draw.line(screen, c, (x, 0), (x, self.settings.SCREEN_H))
        offset = int(self._bg_y)
        for y in range(-60, self.settings.SCREEN_H + 60, 60):
            pygame.draw.line(screen, c, (0, (y + offset) % self.settings.SCREEN_H),
                             (self.settings.SCREEN_W, (y + offset) % self.settings.SCREEN_H))
