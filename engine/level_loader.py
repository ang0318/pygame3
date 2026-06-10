"""
通用关卡加载器 —— 从 JSON 读取布局，构建实体
所有关卡共用此加载器，JSON 格式见 levels/README 或 edit.py 说明。
"""
from __future__ import annotations
import json
from pathlib import Path
import pygame

from engine.settings     import Settings
from engine.asset_loader import AssetLoader
from entities.player     import Player
from entities.npc        import NPC
from entities.platform   import Platform


class LevelLoader:
    """
    用法：
        loader = LevelLoader("levels/level1_layout.json", settings, assets)
        loader.build(platforms_group, npcs_list)
        player = loader.player
        world_w = loader.world_w
        meta    = loader.meta
    """

    def __init__(self, json_path: str,
                 settings: Settings,
                 assets: AssetLoader,
                 dialogue_map: dict[str, list[dict]]) -> None:
        """
        dialogue_map: { dialogue_key: [对话数据列表] }
        JSON 中每个 NPC 用 dialogue_key 索引到实际对话内容。
        """
        self.cfg          = settings
        self.assets       = assets
        self.dialogue_map = dialogue_map
        self.player: Player | None = None
        self.world_w      = settings.SCREEN_W
        self.meta: dict   = {}

        data_path = Path(json_path)
        if not data_path.exists():
            raise FileNotFoundError(f"关卡布局文件不存在：{json_path}")
        with open(data_path, encoding="utf-8") as f:
            self._data = json.load(f)

    def build(self,
              platforms: pygame.sprite.Group,
              npcs_out:  list[NPC]) -> None:
        """构建所有实体，写入传入的容器。"""
        d   = self._data
        cfg = self.cfg
        ast = self.assets

        self.meta    = d.get("meta", {})
        self.world_w = self.meta.get("world_w", cfg.SCREEN_W)

        # ── 玩家 ─────────────────────────────────────────────────────────
        sp = d.get("player_spawn", {"x": 80, "y": cfg.SCREEN_H - 40})
        self.player = Player(sp["x"], sp["y"], cfg, assets=ast)

        # ── 平台 ─────────────────────────────────────────────────────────
        for p in d.get("platforms", []):
            platforms.add(Platform(
                p["x"], p["y"], p["w"], p["h"],
                cfg,
                sprite_key=p.get("sprite_key", "default"),
                assets=ast,
                hidden=p.get("hidden", False),   # 隐形平台：有碰撞，视觉透明
            ))

        # ── NPC ──────────────────────────────────────────────────────────
        for n in d.get("npcs", []):
            if n.get("hidden", False):   # 隐藏 NPC：游戏中不创建（不可见不可交互）
                continue
            key      = n.get("dialogue_key", "")
            dialogue = self.dialogue_map.get(key, [{"text": f"（{n['name']} 暂无对话）"}])
            npcs_out.append(NPC(
                n["x"], n["y"],
                dialogue,
                cfg,
                name=n.get("name", "NPC"),
                sprite_key=n.get("sprite_key", "default"),
                assets=ast,
            ))
