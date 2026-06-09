"""玩家实体 —— 支持左右移动、跳跃、重力、平台碰撞"""
from __future__ import annotations
import pygame
from engine.settings import Settings


class Player(pygame.sprite.Sprite):
    """
    状态机简单版本：idle / run / jump
    扩展时只需在 _update_state() 中增加新状态即可。
    """

    def __init__(self, x: float, y: float, settings: Settings) -> None:
        super().__init__()
        self.cfg = settings

        # 外观（纯色矩形，后期可替换为 spritesheet）
        self.image = pygame.Surface((32, 48), pygame.SRCALPHA)
        self._draw_shape()

        self.rect        = self.image.get_rect(midbottom=(x, y))
        self.pos         = pygame.math.Vector2(self.rect.x, self.rect.y)

        # 物理
        self.vel         = pygame.math.Vector2(0, 0)
        self.on_ground   = False

        # 状态
        self.facing_right = True
        self.state        = "idle"   # idle | run | jump

    # ── 绘制占位图形 ──────────────────────────────────────────────────────
    def _draw_shape(self) -> None:
        self.image.fill((0, 0, 0, 0))
        c = self.cfg.COLOR_PLAYER
        # 身体
        pygame.draw.rect(self.image, c, (8, 16, 16, 26), border_radius=4)
        # 头
        pygame.draw.circle(self.image, c, (16, 12), 10)
        # 眼睛
        pygame.draw.circle(self.image, (30, 30, 46), (19, 10), 3)

    # ── 主更新 ────────────────────────────────────────────────────────────
    def update(self, dt: float, platforms: pygame.sprite.Group) -> None:  # type: ignore[override]
        self._handle_input()
        self._apply_gravity()
        self._move_x(platforms)
        self._move_y(platforms)
        self._update_state()
        self._sync_rect()

    # ── 输入 ──────────────────────────────────────────────────────────────
    def _handle_input(self) -> None:
        keys = pygame.key.get_pressed()
        self.vel.x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -self.cfg.PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = self.cfg.PLAYER_SPEED
            self.facing_right = True
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel.y = self.cfg.JUMP_SPEED
            self.on_ground = False

    # ── 物理 ──────────────────────────────────────────────────────────────
    def _apply_gravity(self) -> None:
        self.vel.y += self.cfg.GRAVITY
        if self.vel.y > 20:          # 终端速度
            self.vel.y = 20

    def _move_x(self, platforms: pygame.sprite.Group) -> None:
        self.pos.x += self.vel.x
        self.rect.x = round(self.pos.x)
        for p in pygame.sprite.spritecollide(self, platforms, False):
            if self.vel.x > 0:
                self.rect.right  = p.rect.left
            elif self.vel.x < 0:
                self.rect.left   = p.rect.right
            self.pos.x = float(self.rect.x)
            self.vel.x = 0

    def _move_y(self, platforms: pygame.sprite.Group) -> None:
        self.pos.y += self.vel.y
        self.rect.y = round(self.pos.y)
        self.on_ground = False
        for p in pygame.sprite.spritecollide(self, platforms, False):
            if self.vel.y > 0:
                self.rect.bottom = p.rect.top
                self.on_ground   = True
            elif self.vel.y < 0:
                self.rect.top    = p.rect.bottom
            self.pos.y = float(self.rect.y)
            self.vel.y = 0

    def _update_state(self) -> None:
        if not self.on_ground:
            self.state = "jump"
        elif self.vel.x != 0:
            self.state = "run"
        else:
            self.state = "idle"

    def _sync_rect(self) -> None:
        self.pos.x = float(self.rect.x)
        self.pos.y = float(self.rect.y)

    # ── 公开工具 ──────────────────────────────────────────────────────────
    def reset(self, x: float, y: float) -> None:
        self.rect.midbottom = (x, y)
        self.pos.update(self.rect.x, self.rect.y)
        self.vel.update(0, 0)
        self.on_ground = False
