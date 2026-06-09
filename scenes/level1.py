"""
关卡 1 —— 从 levels/level1_layout.json 加载所有物体位置
对话内容仍在此文件管理（纯逻辑，不含坐标）
过关条件：回答正确所有问题
"""
from __future__ import annotations
import pygame
from engine.scene_manager import SceneManager
from engine.level_loader  import LevelLoader
from scenes.base_level    import BaseLevelScene

# ── 对话数据（与坐标分离，只管剧情逻辑） ──────────────────────────────────
_DIALOGUES: dict[str, list[dict]] = {
    "guide": [
        {"text": "欢迎来到冒险！我是向导阿明。\n用 A/D 或方向键移动，Space/W 跳跃，E 键与 NPC 对话。"},
        {"text": "前方的守门者会考你几道题，答对才能进入下一关。加油！"},
    ],
    "gatekeeper": [
        {"text": "停！想过关？先回答我的问题！"},
        {
            "text": "问题一：Python 中哪个关键字用于定义函数？",
            "choices": ["class", "def", "func", "define"],
            "answer": 1,
        },
        {
            "text": "问题二：列表 [1,2,3] 的长度是？",
            "choices": ["2", "3", "4", "不确定"],
            "answer": 1,
        },
        {
            "text": "问题三：pygame.display.flip() 的作用是？",
            "choices": ["关闭窗口", "刷新屏幕", "播放音效", "加载图片"],
            "answer": 1,
        },
        {"text": "全部答对！前方通道已开启，祝你好运！"},
    ],
}


class Level1Scene(BaseLevelScene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.hud.level_name = "关卡 1 - 知识入门"

    # ── 构建关卡（从 JSON 加载） ───────────────────────────────────────────
    def _build_level(self) -> None:
        loader = LevelLoader(
            "levels/level1_layout.json",
            self.settings,
            self.assets,
            _DIALOGUES,
        )
        loader.build(self.platforms, self.npcs)
        self.player   = loader.player
        self._world_w = loader.world_w
        if loader.meta.get("name"):
            self.hud.level_name = loader.meta["name"]

    # ── 过关回调 ──────────────────────────────────────────────────────────
    def _on_all_npc_done(self) -> None:
        self.bus.emit("level_complete", {"next": "level2"})

    def on_enter(self) -> None:
        super().on_enter()
        self.bus.subscribe("level_complete", self._goto_next)

    def on_exit(self) -> None:
        self.bus.unsubscribe("level_complete", self._goto_next)

    def _goto_next(self, data: dict) -> None:
        if data and data.get("next") == "level2":
            from scenes.level2 import Level2Scene
            self.manager.replace(Level2Scene(self.manager))
