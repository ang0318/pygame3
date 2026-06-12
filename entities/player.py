"""
玩家实体 —— 支持左右移动、跳跃、重力、平台碰撞
素材约定（放入 assets/ 目录，缺失则自动用色块代替）：
  assets/player_idle_0.png          静止帧（1 帧）
  assets/player_run_0.png           跑步帧 0
  assets/player_run_1.png           跑步帧 1
  assets/player_jump_0.png          跳跃帧（1 帧）
所有图片尺寸建议 32×48 px，加载后自动缩放到 PLAYER_W × PLAYER_H。
"""
from __future__ import annotations
import pygame
from engine.settings    import Settings
from engine.asset_loader import AssetLoader

# 玩家显示尺寸（与碰撞箱一致）
PLAYER_W = 32
PLAYER_H = 48


class Player(pygame.sprite.Sprite):
    """
    状态机：idle / run / jump
    渲染优先使用外部素材，缺失时用纯色占位方块，行为逻辑完全不受影响。
    """

    def __init__(self, x: float, y: float,
                 settings: Settings,
                 assets: AssetLoader | None = None) -> None:
        super().__init__()
        self.cfg    = settings
        self._size  = (PLAYER_W, PLAYER_H)

        # ── 加载帧动画 ────────────────────────────────────────────────────
        if assets:
            fb = settings.COLOR_PLAYER
            self._frames: dict[str, list[pygame.Surface]] = {
                "idle": assets.frames(
                    "assets/player_idle_{}.png", 1, self._size, fb),
                "run":  assets.frames(
                    "assets/player_run_{}.png",  2, self._size, fb),
                "jump": assets.frames(
                    "assets/player_jump_{}.png", 1, self._size, fb),
            }
        else:
            # 没有 AssetLoader 时全部用色块（向后兼容）
            self._frames = {k: [self._make_fallback()] for k in ("idle", "run", "jump")}

        # 缩放所有帧到统一尺寸
        self._frames = {
            k: [pygame.transform.scale(f, self._size) for f in v]
            for k, v in self._frames.items()
        }

        # 动画计时
        self._anim_timer = 0.0
        self._anim_fps   = 8.0       # 帧/秒
        self._frame_idx  = 0

        self.image = self._frames["idle"][0]
        self.rect  = self.image.get_rect(midbottom=(x, y))
        self.pos   = pygame.math.Vector2(self.rect.x, self.rect.y)

        # 物理
        self.vel       = pygame.math.Vector2(0, 0)
        self.on_ground = False
        self._jump_cooldown        = 0.0    # 跳跃冷却计时器（倒计时到 0 才能再跳）
        self._just_jumped          = False  # 本次跳跃已起跳，落地后才启动冷却
        self._pressing_horizontal  = False  # 本帧是否按了方向键
        self.jump_pressed          = False  # 外部通过 KEYDOWN 事件设置，消费后自动清零

        # 状态
        self.facing_right = True
        self.state        = "idle"

    # ── 占位色块（无 assets 时使用） ──────────────────────────────────────
    def _make_fallback(self) -> pygame.Surface:
        surf = pygame.Surface(self._size, pygame.SRCALPHA)
        surf.fill(self.cfg.COLOR_PLAYER)
        # 简单线条模拟人形
        c2 = (30, 30, 46)
        pygame.draw.circle(surf, c2, (PLAYER_W // 2, 10), 8)         # 头
        pygame.draw.rect(surf, c2, (PLAYER_W//2-5, 18, 10, 18), 2)   # 身
        return surf

    # ── 主更新 ────────────────────────────────────────────────────────────
    def update(self, dt: float, platforms: pygame.sprite.Group) -> None:  # type: ignore[override]
        if self._jump_cooldown > 0:
            self._jump_cooldown = max(0.0, self._jump_cooldown - dt)
        self._handle_input()
        self._apply_gravity(dt)
        self._move_x(platforms)
        self._move_y(platforms)
        self._update_state()
        self._animate(dt)
        self._sync_rect()

    # ── 输入 ─────────────────────────────────────────────────────────────
    def _handle_input(self) -> None:
        keys = pygame.key.get_pressed()
        self._pressing_horizontal = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -self.cfg.PLAYER_SPEED
            self.facing_right = False
            self._pressing_horizontal = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = self.cfg.PLAYER_SPEED
            self.facing_right = True
            self._pressing_horizontal = True
        else:
            if self.on_ground:
                self.vel.x = 0   # 落地后松键立即停

        # 跳跃：仅响应按下瞬间（jump_pressed 由 handle_event 的 KEYDOWN 设置）
        can_jump = self.on_ground and self._jump_cooldown <= 0
        if self.jump_pressed and can_jump:
            self.vel.y         = self.cfg.JUMP_SPEED
            self.on_ground     = False
            self._just_jumped  = True
        self.jump_pressed = False   # 每帧消费后清零

    # ── 物理 ─────────────────────────────────────────────────────────────
    def _apply_gravity(self, dt: float) -> None:
        self.vel.y = min(self.vel.y + self.cfg.GRAVITY, 20)
        # 空中松开方向键时才施加水平阻尼，按着键时保持全速
        if not self.on_ground and not self._pressing_horizontal:
            self.vel.x *= self.cfg.AIR_DAMPING

    def _move_x(self, platforms: pygame.sprite.Group) -> None:
        self.pos.x += self.vel.x
        self.rect.x = round(self.pos.x)
        for p in pygame.sprite.spritecollide(self, platforms, False):
            if self.vel.x > 0:
                self.rect.right = p.rect.left
            elif self.vel.x < 0:
                self.rect.left  = p.rect.right
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
                # 只有从跳跃状态落地时才启动冷却，防止瞬间二连跳
                if self._just_jumped:
                    self._jump_cooldown = self.cfg.JUMP_COOLDOWN
                    self._just_jumped   = False
            elif self.vel.y < 0:
                self.rect.top    = p.rect.bottom
            self.pos.y = float(self.rect.y)
            self.vel.y = 0

    # ── 状态 & 动画 ───────────────────────────────────────────────────────
    def _update_state(self) -> None:
        new_state = "jump" if not self.on_ground else ("run" if self.vel.x != 0 else "idle")
        if new_state != self.state:
            self.state       = new_state
            self._frame_idx  = 0
            self._anim_timer = 0.0

    def _animate(self, dt: float) -> None:
        frame_list = self._frames[self.state]
        if len(frame_list) > 1:
            self._anim_timer += dt
            if self._anim_timer >= 1.0 / self._anim_fps:
                self._anim_timer -= 1.0 / self._anim_fps
                self._frame_idx   = (self._frame_idx + 1) % len(frame_list)

        base = frame_list[self._frame_idx % len(frame_list)]
        # 镜像翻转
        self.image = base if self.facing_right else pygame.transform.flip(base, True, False)

    def _sync_rect(self) -> None:
        self.pos.x = float(self.rect.x)
        self.pos.y = float(self.rect.y)

    # ── 公开工具 ──────────────────────────────────────────────────────────
    def reset(self, x: float, y: float) -> None:
        self.rect.midbottom = (x, y)
        self.pos.update(self.rect.x, self.rect.y)
        self.vel.update(0, 0)
        self.on_ground      = False
        self._jump_cooldown = 0.0
        self._just_jumped   = False
