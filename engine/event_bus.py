"""轻量级事件总线 —— 解耦各模块间通信"""
from collections import defaultdict
from typing import Callable, Any


class EventBus:
    """
    发布/订阅模式。
    用法：
        bus.subscribe("player_died", my_callback)
        bus.emit("player_died", {"reason": "fall"})
    """

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable) -> None:
        self._listeners[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        self._listeners[event].remove(callback)

    def emit(self, event: str, data: Any = None) -> None:
        for cb in list(self._listeners[event]):
            cb(data)

    def clear(self) -> None:
        self._listeners.clear()
