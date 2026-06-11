# 如何新增一关

以新增"关卡 3"为例，全程只需三步。

---

## 步骤 1：创建关卡布局 JSON

手动创建或复制已有关卡修改：

```bash
copy levels\level2_layout.json levels\level3_layout.json
```

或者直接用编辑器新建，先创建一个最小结构：

```json
{
  "meta": {
    "name": "关卡 3 - 自定义名称",
    "world_w": 1920
  },
  "player_spawn": { "x": 80, "y": 460 },
  "platforms": [
    { "x": 0, "y": 500, "w": 1920, "h": 40, "sprite_key": "default", "hidden": true }
  ],
  "npcs": [
    {
      "x": 500, "y": 500,
      "name": "NPC名字",
      "sprite_key": "guide",
      "dialogue_key": "guide"
    }
  ],
  "gems": []
}
```

然后用编辑器精调位置：

```bash
python edit.py   # 选择 level3
```

---

## 步骤 2：创建场景文件

新建 `scenes/level3.py`，文件名和类名必须遵循约定：

```python
# scenes/level3.py
from __future__ import annotations
from engine.scene_manager import SceneManager
from engine.level_loader  import LevelLoader
from scenes.base_level    import BaseLevelScene

# ── 对话数据 ──────────────────────────────────────────────────────────────────
_DIALOGUES = {
    "guide": [
        {"text": "欢迎来到关卡 3！"},
        {"text": "完成对话即可过关。"},
    ],
}


class Level3Scene(BaseLevelScene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self._level_asset_id = 3              # 对应 assets/levels/level3/（可选）
        self._bg_image_key   = "bg_level3.png"  # 背景图文件名（缺失时用纯色）
        self.hud.level_name  = "关卡 3 - 自定义名称"

    def _build_level(self) -> None:
        expanded = {k: self.expand_dialogue(v) for k, v in _DIALOGUES.items()}
        loader = LevelLoader(
            "levels/level3_layout.json",
            self.settings, self.assets, expanded,
        )
        loader.build(self.platforms, self.npcs)
        self.player   = loader.player
        self._world_w = loader.world_w

    def _on_all_npc_done(self) -> None:
        # 如果后面还有关卡：
        self.bus.emit("next_level")
        # 如果是最后一关：
        # self.bus.emit("game_over", {"win": True, "score": self.hud.score})
```

**命名约定必须遵守：**
- 文件名：`scenes/level3.py`
- 类名：`Level3Scene`

---

## 步骤 3：完成

不需要改 `main.py`，不需要注册任何东西。

`LevelRegistry` 启动时会自动扫描 `scenes/level*.py`，按数字编号排序，Level3Scene 会自动排在 Level2Scene 之后。

运行验证：

```bash
python main.py
```

---

## 自定义过关条件

`_on_all_npc_done()` 在**所有 NPC 的对话都完成**后自动触发。如果你需要额外条件（如关卡 2 的宝石收集），覆写 `update()` 中的检查逻辑：

```python
def update(self, dt: float) -> None:
    super().update(dt)
    # 额外条件：例如玩家到达终点区域
    if self.player and self.player.rect.x > 1800:
        self.bus.emit("next_level")
```

---

## 带题库的问答

对话中加入 `question_pool` 字段，详见 [对话 & 问答系统](11_dialogue_qa.md)。

---

## 关卡专属素材（可选）

创建 `assets/levels/level3/` 目录，放入同名素材文件，会自动覆盖通用 `assets/` 中的同名文件。

详见 [素材规范](08_assets.md)。
