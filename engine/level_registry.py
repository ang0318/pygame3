"""
关卡注册表 —— 自动扫描 levels/levelN/scene.py，按编号排序
main.py 只需调用 LevelRegistry.next_scene() 获取下一关场景，
完全不需要知道有几关、叫什么名字。

约定（新结构）：
  levels/level1/scene.py  → 必须包含类 Level1Scene
  levels/level2/scene.py  → Level2Scene
  levels/level42/scene.py → Level42Scene
  编号可以不连续，按数字升序排列。

每个关卡目录是完全自包含的包：
  levels/levelN/
    __init__.py
    layout.json      —— 布局数据
    dialogues.py     —— 对话/题库数据
    scene.py         —— 场景类
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

    _PATTERN = re.compile(r"^level(\d+)$")   # 匹配 levelN 目录名

    def __init__(self, manager: "SceneManager") -> None:
        self.manager   = manager
        self._scenes:  list[type] = []   # 按编号排序的场景类列表
        self._current  = -1
        self._scan()

    # ── 扫描 ─────────────────────────────────────────────────────────────
    def _scan(self) -> None:
        levels_dir = Path("levels")
        entries: list[tuple[int, type]] = []

        for level_dir in levels_dir.iterdir():
            if not level_dir.is_dir():
                continue
            m = self._PATTERN.match(level_dir.name)
            if not m:
                continue
            scene_file = level_dir / "scene.py"
            if not scene_file.exists():
                continue

            num = int(m.group(1))
            # 模块路径：levels.levelN.scene
            mod_path = f"levels.{level_dir.name}.scene"
            try:
                mod = importlib.import_module(mod_path)
            except Exception as e:
                print(f"[LevelRegistry] 警告：导入 {mod_path} 失败：{e}，已跳过")
                continue

            # 类名约定：Level1Scene, Level2Scene …
            class_name = f"Level{num}Scene"
            cls = getattr(mod, class_name, None)
            if cls is None:
                print(f"[LevelRegistry] 警告：{mod_path} 中找不到 {class_name}，已跳过")
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
