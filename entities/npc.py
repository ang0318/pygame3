"""
NPC 实体 —— 带对话气泡、问答状态机
素材约定（缺失则自动用色块代替）：
  assets/npc.png   所有 NPC 共用同一张图
建议尺寸 32×48 px。
"""
from __future__ import annotations
import pygame
from engine.settings     import Settings
from engine.asset_loader import AssetLoader

NPC_W = 32
NPC_H = 48


class NPC(pygame.sprite.Sprite):
    """
    NPC 携带一组问答数据，玩家靠近并按 E 时触发对话。
    对话数据格式（列表，按顺序播放）：
        [
          {"text": "你好！", "choices": None},
          {"text": "2+2=?", "choices": ["3","4","5"], "answer": 1},
        ]
    """

    INTERACT_DIST = 80

    def __init__(self, x: float, y: float,
                 dialogue: list[dict],
                 settings: Settings,
                 name: str = "NPC",
                 sprite_key: str = "default",
                 assets: AssetLoader | None = None) -> None:
        super().__init__()
        self.cfg        = settings
        self.dialogue   = dialogue
        self.name       = name
        self._size      = (NPC_W, NPC_H)

        # ── 加载帧 ────────────────────────────────────────────────────────
        if assets:
            fb = settings.COLOR_NPC
            surf = assets.safe_image("npc.png", self._size, fb)
            idle_frames = [surf]
        else:
            idle_frames = [self._make_fallback()]

        self._idle_frames = [pygame.transform.scale(f, self._size) for f in idle_frames]

        self._anim_timer = 0.0
        self._anim_fps   = 4.0
        self._frame_idx  = 0

        self.image = self._idle_frames[0]
        self.rect  = self.image.get_rect(midbottom=(x, y))

        # 朝向（素材约定面朝右，facing_left=True 时水平翻转）
        self._facing_left = False

        # optional=True 的 NPC 不计入过关条件
        self.optional  = False

        # 对话状态
        self.talking   = False
        self.step      = 0
        self.finished  = False
        self._hint_timer = 0.0

    # ── 占位色块 ──────────────────────────────────────────────────────────
    def _make_fallback(self) -> pygame.Surface:
        surf = pygame.Surface(self._size, pygame.SRCALPHA)
        surf.fill(self.cfg.COLOR_NPC)
        c2 = (30, 30, 46)
        pygame.draw.circle(surf, c2, (NPC_W // 2, 10), 8)
        pygame.draw.rect(surf, c2, (NPC_W//2-5, 18, 10, 18), 2)
        # 感叹号
        pygame.draw.circle(surf, self.cfg.COLOR_GOLD, (NPC_W // 2, 2), 3)
        return surf

    # ── 更新 ─────────────────────────────────────────────────────────────
    def update(self, dt: float,                               # type: ignore[override]
               player_rect: "pygame.Rect | None" = None) -> None:
        self._hint_timer += dt

        # 实时朝向玩家（只要玩家位置已知）
        if player_rect is not None:
            self.face_toward(player_rect)

        frames = self._idle_frames
        if len(frames) > 1:
            self._anim_timer += dt
            if self._anim_timer >= 1.0 / self._anim_fps:
                self._anim_timer -= 1.0 / self._anim_fps
                self._frame_idx   = (self._frame_idx + 1) % len(frames)
        base = frames[self._frame_idx % len(frames)]
        # 素材约定面朝右；facing_left 时水平翻转
        self.image = (pygame.transform.flip(base, True, False)
                      if self._facing_left else base)

    def face_toward(self, player_rect: "pygame.Rect") -> None:
        """朝向玩家（玩家在左则翻转素材）。"""
        self._facing_left = player_rect.centerx < self.rect.centerx

    # ── 渲染提示 ──────────────────────────────────────────────────────────
    def draw_hint(self, screen: pygame.Surface,
                  font: pygame.font.Font,
                  player_rect: pygame.Rect,
                  cam_x: int = 0) -> None:
        """
        player_rect: 世界坐标（不减 cam_x）
        cam_x: 当前摄像机偏移，用于将世界坐标转换为屏幕坐标渲染
        """
        if self.talking or self.finished:
            return
        # 用世界坐标比较距离，避免摄像机偏移导致误判
        dist = abs(self.rect.centerx - player_rect.centerx)
        if dist < self.INTERACT_DIST:
            alpha    = 255 if int(self._hint_timer * 3) % 2 == 0 else 140
            surf     = font.render("[E] 对话", True, self.cfg.COLOR_GOLD)
            surf.set_alpha(alpha)
            screen_x = self.rect.centerx - cam_x - surf.get_width() // 2
            screen_y = self.rect.top - 24
            screen.blit(surf, (screen_x, screen_y))

    # ── 互动 ─────────────────────────────────────────────────────────────
    def try_interact(self, player_rect: pygame.Rect) -> bool:
        if self.finished:
            return False
        dist = abs(self.rect.centerx - player_rect.centerx)
        if dist < self.INTERACT_DIST and not self.talking:
            self.face_toward(player_rect)   # 对话前先朝向玩家
            self.talking    = True
            self.step       = 0
            self._frame_idx = 0
            return True
        return False

    @property
    def current_dialogue(self) -> dict | None:
        return self.dialogue[self.step] if self.step < len(self.dialogue) else None

    def advance(self) -> bool:
        self.step += 1
        if self.step >= len(self.dialogue):
            self.talking  = False
            self.finished = True
            return False
        return True
