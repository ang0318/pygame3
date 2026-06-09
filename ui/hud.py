"""HUD —— 顶部状态栏（关卡名、分数、生命）"""
from __future__ import annotations
import pygame
from engine.settings import Settings


class HUD:
    def __init__(self, settings: Settings, font: pygame.font.Font) -> None:
        self.cfg   = settings
        self.font  = font
        self.score = 0
        self.lives = 3
        self.level_name = ""

    def draw(self, screen: pygame.Surface) -> None:
        # 半透明顶栏
        bar = pygame.Surface((self.cfg.SCREEN_W, 36), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 120))
        screen.blit(bar, (0, 0))

        # 关卡名（居中）
        if self.level_name:
            ts = self.font.render(self.level_name, True, self.cfg.COLOR_GOLD)
            screen.blit(ts, (self.cfg.SCREEN_W // 2 - ts.get_width() // 2, 6))

        # 分数（左）
        ss = self.font.render(f"Score: {self.score}", True, self.cfg.COLOR_TEXT)
        screen.blit(ss, (12, 6))

        # 生命（右）
        ls = self.font.render(f"生命 x{self.lives}", True, (243, 139, 168))
        screen.blit(ls, (self.cfg.SCREEN_W - ls.get_width() - 12, 6))
