"""胜利场景 —— 通关庆祝"""
from __future__ import annotations
import math
import random
import pygame
from engine.scene_manager import BaseScene, SceneManager


class _Particle:
    def __init__(self, w: int, h: int) -> None:
        self.x   = random.randint(0, w)
        self.y   = random.randint(-h, 0)
        self.vy  = random.uniform(60, 160)
        self.vx  = random.uniform(-30, 30)
        self.c   = random.choice([(249,226,175),(166,227,161),(137,180,250),(243,139,168)])
        self.r   = random.randint(4, 8)
        self.life= random.uniform(2, 5)
        self.age = 0.0

    def update(self, dt: float) -> bool:
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.age += dt
        return self.age < self.life


class WinScene(BaseScene):
    def __init__(self, manager: SceneManager, score: int = 0) -> None:
        super().__init__(manager)
        self.score       = score
        self._font_big   = self.assets.font(self.settings.FONT_NAME, 56)
        self._font_mid   = self.assets.font(self.settings.FONT_NAME, 32)
        self._font_small = self.assets.font(self.settings.FONT_NAME, 22)
        self._particles: list[_Particle] = []
        self._timer      = 0.0
        W, H = self.settings.SCREEN_W, self.settings.SCREEN_H
        for _ in range(80):
            self._particles.append(_Particle(W, H))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                from scenes.menu_scene import MenuScene
                self.manager.replace(MenuScene(self.manager))
            elif event.key == pygame.K_ESCAPE:
                self.bus.emit("quit")

    def update(self, dt: float) -> None:
        self._timer += dt
        W, H = self.settings.SCREEN_W, self.settings.SCREEN_H
        self._particles = [p for p in self._particles if p.update(dt)]
        while len(self._particles) < 80:
            self._particles.append(_Particle(W, H))

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(self.settings.COLOR_BG)

        # 彩纸粒子
        for p in self._particles:
            alpha = max(0, int(255 * (1 - p.age / p.life)))
            s = pygame.Surface((p.r*2, p.r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p.c, alpha), (p.r, p.r), p.r)
            screen.blit(s, (int(p.x), int(p.y)))

        W, H = self.settings.SCREEN_W, self.settings.SCREEN_H

        # 标题波动
        wave = math.sin(self._timer * 3) * 6
        t1   = self._font_big.render("通关！", True, self.settings.COLOR_GOLD)
        screen.blit(t1, (W//2 - t1.get_width()//2, int(120 + wave)))

        t2 = self._font_mid.render(f"最终得分：{self.score}", True, self.settings.COLOR_TEXT)
        screen.blit(t2, (W//2 - t2.get_width()//2, 210))

        t3 = self._font_small.render("按 Enter 返回主菜单", True, (120, 120, 160))
        screen.blit(t3, (W//2 - t3.get_width()//2, H - 60))
