"""
关卡注册表 —— 自动扫描 scenes/level*.py，按编号排序
main.py 只需调用 LevelRegistry.next_scene() 获取下一关场景，
完全不需要知道有几关、叫什么名字。

约定：
  scenes/level1.py  → 必须包含与文件名同名的类 Level1Scene
  scenes/level2.py  → Level2Scene
  scenes/level42.py → Level42Scene
  以此类推，编号可以不连续，按数字升序排列。
"""
from __future__ import annotations
import re
import importlib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.scene_manager import BaseScene, SceneManager


class LevelRegistry:
    """
    用法（在 main.py 中）：
        registry = LevelRegistry(manager)
        first_scene = registry.start()      # 获取第一关场景
        next_scene  = registry.advance()    # 推进到下一关，None 表示已通关
    """

    _PATTERN = re.compile(r"^level(\d+)$")   # 匹配 levelN.py

    def __init__(self, manager: "SceneManager") -> None:
        self.manager   = manager
        self._scenes:  list[type] = []   # 按编号排序的场景类列表
        self._current  = -1
        self._scan()

    # ── 扫描 ─────────────────────────────────────────────────────────────
    def _scan(self) -> None:
        scenes_dir = Path("scenes")
        entries: list[tuple[int, type]] = []

        for py_file in scenes_dir.glob("level*.py"):
            stem  = py_file.stem                    # e.g. "level1"
            m     = self._PATTERN.match(stem)
            if not m:
                continue
            num   = int(m.group(1))
            mod   = importlib.import_module(f"scenes.{stem}")
            # 类名约定：Level1Scene, Level2Scene …
            class_name = f"Level{num}Scene"
            cls   = getattr(mod, class_name, None)
            if cls is None:
                print(f"[LevelRegistry] 警告：{py_file} 中找不到 {class_name}，已跳过")
                continue
            entries.append((num, cls))

        entries.sort(key=lambda t: t[0])
        self._scenes = [cls for _, cls in entries]
        print(f"[LevelRegistry] 发现 {len(self._scenes)} 关：{[c.__name__ for c in self._scenes]}")

    # ── 公开 API ─────────────────────────────────────────────────────────
    def start(self) -> "BaseScene | None":
        """返回第一关的场景实例。"""
        self._current = 0
        return self._make_current()

    def advance(self) -> "BaseScene | None":
        """推进到下一关，返回场景实例；已是最后一关则返回 None。"""
        self._current += 1
        return self._make_current()

    @property
    def has_next(self) -> bool:
        return self._current + 1 < len(self._scenes)

    @property
    def total(self) -> int:
        return len(self._scenes)

    @property
    def current_index(self) -> int:
        return self._current

    # ── 内部 ─────────────────────────────────────────────────────────────
    def _make_current(self) -> "BaseScene | None":
        if 0 <= self._current < len(self._scenes):
            return self._scenes[self._current](self.manager)
        return None
