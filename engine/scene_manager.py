"""场景基类 + 场景管理器 —— 整个游戏的调度核心"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .settings import Settings
    from .event_bus import EventBus
    from .asset_loader import AssetLoader


# ──────────────────────────────────────────────────────────────────────────────
# 场景基类
# ──────────────────────────────────────────────────────────────────────────────
class BaseScene(ABC):
    """所有场景（菜单、关卡、对话…）都继承此类。"""

    def __init__(self, manager: "SceneManager") -> None:
        self.manager = manager
        self.settings: Settings    = manager.settings
        self.bus:      EventBus    = manager.bus
        self.assets:   AssetLoader = manager.assets

    # -- 生命周期 -------------------------------------------------------------
    def on_enter(self) -> None:
        """切入场景时调用一次（做初始化/重置）。"""

    def on_exit(self) -> None:
        """切出场景时调用一次（做清理）。"""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None: ...


# ──────────────────────────────────────────────────────────────────────────────
# 场景管理器
# ──────────────────────────────────────────────────────────────────────────────
class SceneManager:
    """
    栈式场景管理：
      push(scene)  —— 压入新场景（旧场景暂停但保留）
      pop()        —— 弹出当前场景，回到上一场景
      replace(scene) —— 替换当前场景（不保留旧场景）
    """

    def __init__(self, settings: "Settings", bus: "EventBus", assets: "AssetLoader") -> None:
        self.settings = settings
        self.bus      = bus
        self.assets   = assets
        self._stack:  list[BaseScene] = []
        self._pending: list[tuple[str, BaseScene | None]] = []   # 延迟操作，避免 update 中修改栈

    # -- 公开 API -------------------------------------------------------------
    def push(self, scene: BaseScene) -> None:
        self._pending.append(("push", scene))

    def pop(self) -> None:
        self._pending.append(("pop", None))

    def replace(self, scene: BaseScene) -> None:
        self._pending.append(("replace", scene))

    @property
    def current(self) -> BaseScene | None:
        return self._stack[-1] if self._stack else None

    # -- 主循环接口 -----------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if self.current:
            self.current.handle_event(event)

    def update(self, dt: float) -> None:
        self._flush_pending()
        if self.current:
            self.current.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        if self.current:
            self.current.draw(screen)

    # -- 内部 -----------------------------------------------------------------
    def _flush_pending(self) -> None:
        for op, scene in self._pending:
            if op == "push" and scene:
                self._stack.append(scene)
                scene.on_enter()
            elif op == "pop" and self._stack:
                old = self._stack.pop()
                old.on_exit()
                if self.current:
                    self.current.on_enter()   # 重新激活
            elif op == "replace" and scene:
                if self._stack:
                    old = self._stack.pop()
                    old.on_exit()
                self._stack.append(scene)
                scene.on_enter()
        self._pending.clear()
