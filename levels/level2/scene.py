"""
关卡 2 场景
素材、布局、对话数据全部在 levels/level2/ 目录内自包含。

目录结构：
  levels/level2/
    layout.json      —— 平台/NPC/宝石/玩家出生点布局
    dialogues.py     —— 对话与题库数据
    scene.py         —— 本文件，关卡场景类

过关条件：收集 >= 3 颗宝石 且 Boss 所有问答正确
过关后：bus.emit("game_over", {"win": True, "score": N})
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import pygame

from engine.scene_manager import SceneManager
from engine.level_loader  import LevelLoader
from scenes.base_level    import BaseLevelScene
from entities.npc         import NPC
from levels.level2.dialogues import DIALOGUES, BOSS_LOCKED


# ── 宝石实体 ──────────────────────────────────────────────────────────────────
class Gem(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int,
                 color: tuple = (249, 226, 175),
                 assets=None) -> None:
        super().__init__()
        size = (18, 18)
        if assets:
            self.image = assets.safe_image("gem.png", size, color)
        else:
            self.image = pygame.Surface(size, pygame.SRCALPHA)
            pts = [(9, 0), (18, 9), (9, 18), (0, 9)]
            pygame.draw.polygon(self.image, color, pts)
            pygame.draw.polygon(self.image, (255, 255, 255), pts, 2)
        self.image   = pygame.transform.scale(self.image, size)
        self.rect    = self.image.get_rect(center=(x, y))
        self._base_y = float(y)
        self._timer  = 0.0

    def update(self, dt: float) -> None:   # type: ignore[override]
        self._timer += dt
        self.rect.centery = int(self._base_y + math.sin(self._timer * 3) * 5)


# ── 关卡 2 场景 ───────────────────────────────────────────────────────────────
class Level2Scene(BaseLevelScene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self._level_asset_id = 2
        self._bg_image_key   = "bg_level2.png"
        self.hud.level_name  = "关卡 2 - 跳跃挑战"
        self.gems:            pygame.sprite.Group = pygame.sprite.Group()
        self._gem_count       = 0
        self._gem_required    = 3
        self._boss: NPC | None = None

    # ── 构建关卡 ─────────────────────────────────────────────────────────
    def _build_level(self) -> None:
        # 展开题库（随机抽题）
        expanded = {k: self.expand_dialogue(v) for k, v in DIALOGUES.items()}
        loader = LevelLoader(
            "levels/level2/layout.json",
            self.settings, self.assets, expanded,
        )
        loader.build(self.platforms, self.npcs)
        self.player   = loader.player
        self._world_w = loader.world_w
        self._boss    = self.npcs[-1] if self.npcs else None

        # 宝石从 JSON 加载
        layout_path = Path("levels/level2/layout.json")
        if layout_path.exists():
            with open(layout_path, encoding="utf-8") as f:
                data = json.load(f)
            for g in data.get("gems", []):
                if g.get("hidden", False):
                    continue
                self.gems.add(Gem(g["x"], g["y"], assets=self.assets))

    # ── on_enter ─────────────────────────────────────────────────────────
    def on_enter(self) -> None:
        self.gems       = pygame.sprite.Group()
        self._gem_count = 0
        super().on_enter()

    # ── 更新 ─────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        self.gems.update(dt)
        if self.player:
            for _ in pygame.sprite.spritecollide(self.player, self.gems, True):
                self._gem_count += 1
                self.hud.score  += 50
        super().update(dt)
        self.hud.level_name = f"关卡 2 - 宝石 {self._gem_count}/{self._gem_required}"

    # ── 事件（Boss 宝石门槛） ─────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> None:
        if (not self.dialogue.active
                and event.type == pygame.KEYDOWN
                and event.key == pygame.K_e
                and self.player
                and self._boss):
            dist = abs(self._boss.rect.centerx - self.player.rect.centerx)
            if dist < NPC.INTERACT_DIST and not self._boss.talking and not self._boss.finished:
                if self._gem_count < self._gem_required:
                    self.dialogue.open(BOSS_LOCKED[0]["text"])
                    return
        super().handle_event(event)

    # ── 渲染 ─────────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        # 先调用基类渲染世界层（平台、NPC、玩家、HUD）
        self._draw_world(screen)

        # 宝石（世界层，在对话框之下）
        cx = int(self._cam_x)
        for gem in self.gems:
            screen.blit(gem.image, (gem.rect.x - cx, gem.rect.y))

        # 宝石计数 UI（HUD层，在对话框之下）
        font    = self.assets.font(self.settings.FONT_NAME, 18)
        gem_txt = font.render(
            f"宝石 {self._gem_count} / {self._gem_required}",
            True, self.settings.COLOR_GOLD)
        screen.blit(gem_txt, (12, self.settings.SCREEN_H - 30))

        # 对话框最后画，确保最高图层
        self.dialogue.draw(screen)

    # ── 过关 ─────────────────────────────────────────────────────────────
    def _on_all_npc_done(self) -> None:
        self.bus.emit("next_level")
