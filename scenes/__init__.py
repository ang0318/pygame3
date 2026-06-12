# scenes package
# 注意：level1 / level2 场景已迁移到 levels/levelN/scene.py
# 由 LevelRegistry 自动扫描加载，无需在此 import
from .menu_scene import MenuScene
from .win_scene  import WinScene

__all__ = ["MenuScene", "WinScene"]
