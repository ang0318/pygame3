"""
关卡 1 场景
素材、布局、对话数据全部在 levels/level1/ 目录内自包含。

目录结构：
  levels/level1/
    layout.json      —— 平台/NPC/玩家出生点布局
    dialogues.py     —— 对话与题库数据
    scene.py         —— 本文件，关卡场景类

过关条件：回答正确所有 NPC 问题
过关后：bus.emit("next_level")  ← main.py 负责推进到下一关
"""
from __future__ import annotations
from engine.scene_manager import SceneManager
from engine.level_loader  import LevelLoader
from scenes.base_level    import BaseLevelScene
from levels.level1.dialogues import DIALOGUES


class Level1Scene(BaseLevelScene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self._level_asset_id = 1
        self._bg_image_key   = "bg_level1.png"
        self.hud.level_name  = "关卡 1 - 知识入门"

    def _build_level(self) -> None:
        # 展开题库（随机抽题）
        expanded = {k: self.expand_dialogue(v) for k, v in DIALOGUES.items()}
        loader = LevelLoader(
            "levels/level1/layout.json",
            self.settings, self.assets, expanded,
        )
        loader.build(self.platforms, self.npcs)
        self.player   = loader.player
        self._world_w = loader.world_w
        if loader.meta.get("name"):
            self.hud.level_name = loader.meta["name"]

    def _on_all_npc_done(self) -> None:
        self.bus.emit("next_level")
