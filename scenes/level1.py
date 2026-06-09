"""
关卡 1 —— 知识问答入门关
地图：三段平台 + 两个 NPC（一个闲聊引导、一个问答守门）
过关条件：回答正确所有问题
"""
from __future__ import annotations
import pygame
from engine.scene_manager import SceneManager
from scenes.base_level    import BaseLevelScene
from entities.player      import Player
from entities.npc         import NPC
from entities.platform    import Platform


# ── 关卡数据（问答题库） ───────────────────────────────────────────────────
_GUIDE_DIALOGUE = [
    {"text": "欢迎来到冒险！我是向导阿明。\n用 ← → 移动，Space / W / ↑ 跳跃，E 键与 NPC 对话。"},
    {"text": "前方的守门者会考你几道题，答对才能进入下一关。加油！"},
]

_GATEKEEPER_DIALOGUE = [
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
]


class Level1Scene(BaseLevelScene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.hud.level_name = "关卡 1 · 知识入门"
        self._world_w       = 1600

    # ── 构建关卡 ──────────────────────────────────────────────────────────
    def _build_level(self) -> None:
        cfg = self.settings
        W, H = cfg.SCREEN_W, cfg.SCREEN_H

        # 地面
        self.platforms.add(Platform(0,   H - 40, 1600, 40, cfg))
        # 中台
        self.platforms.add(Platform(300, H - 140, 200, 20, cfg))
        self.platforms.add(Platform(600, H - 220, 200, 20, cfg))
        self.platforms.add(Platform(900, H - 160, 300, 20, cfg))
        # 高台（守门者站台）
        self.platforms.add(Platform(1200, H - 260, 300, 20, cfg))

        # 玩家出生点
        self.player = Player(80, H - 40, cfg)

        # 向导 NPC（左侧）
        guide = NPC(250, H - 40, _GUIDE_DIALOGUE, cfg, name="向导阿明")
        # 守门者 NPC（右侧高台）
        gatekeeper = NPC(1300, H - 260, _GATEKEEPER_DIALOGUE, cfg, name="守门者")
        self.npcs = [guide, gatekeeper]

    # ── 过关回调 ──────────────────────────────────────────────────────────
    def _on_all_npc_done(self) -> None:
        # 延迟 1 帧后切换到关卡 2（通过事件总线）
        self.bus.emit("level_complete", {"next": "level2"})

    # ── 监听过关事件（on_enter 时注册） ───────────────────────────────────
    def on_enter(self) -> None:
        super().on_enter()
        self.bus.subscribe("level_complete", self._goto_next)

    def on_exit(self) -> None:
        self.bus.unsubscribe("level_complete", self._goto_next)

    def _goto_next(self, data: dict) -> None:
        if data and data.get("next") == "level2":
            from scenes.level2 import Level2Scene
            self.manager.replace(Level2Scene(self.manager))
