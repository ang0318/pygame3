# 如何新增一关

以新增"关卡 3"为例，全程只需三步。

---

## 目录结构约定

每个关卡是完全自包含的 Python 包：

```
levels/
  level3/
    __init__.py      # 空文件，声明包
    layout.json      # 平台/NPC/宝石/出生点布局
    dialogues.py     # 对话与题库数据
    scene.py         # 场景类 Level3Scene
    assets/          # 关卡专属素材（可选）
      .keep
```

---

## 步骤 1：创建目录和 `__init__.py`

```bash
mkdir levels\level3
mkdir levels\level3\assets
type nul > levels\level3\__init__.py
type nul > levels\level3\assets\.keep
```

---

## 步骤 2：创建布局 JSON

新建 `levels/level3/layout.json`：

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
      "x": 400, "y": 500,
      "name": "引导者",
      "sprite_key": "guide",
      "dialogue_key": "guide",
      "optional": true
    },
    {
      "x": 1600, "y": 500,
      "name": "守门者",
      "sprite_key": "gatekeeper",
      "dialogue_key": "gatekeeper"
    }
  ],
  "gems": []
}
```

> `optional: true` 的 NPC 是可选对话，完成与否不影响过关；省略或 `false` 表示必须完成。

然后用编辑器精调位置：

```bash
python edit.py   # 选择 level3
```

---

## 步骤 3：创建对话数据

新建 `levels/level3/dialogues.py`：

```python
DIALOGUES: dict[str, list[dict]] = {
    "guide": [
        {"text": "欢迎来到关卡 3！"},
    ],
    "gatekeeper": [
        {"text": "回答正确才能过关！"},
        {
            "question_pool": [
                {"text": "1+1=?", "choices": ["1", "2", "3"], "answer": 1},
                {"text": "2*3=?", "choices": ["5", "6", "7"], "answer": 1},
            ],
            "question_count": 1,
        },
        {"text": "答对了！前方通道开启！"},
    ],
}
```

---

## 步骤 4：创建场景文件

新建 `levels/level3/scene.py`：

```python
from __future__ import annotations
from engine.scene_manager import SceneManager
from engine.level_loader  import LevelLoader
from scenes.base_level    import BaseLevelScene
from levels.level3.dialogues import DIALOGUES


class Level3Scene(BaseLevelScene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self._level_asset_id = 3
        self._bg_image_key   = "bg_level3.png"   # 缺失时用纯色背景
        self.hud.level_name  = "关卡 3 - 自定义名称"

    def _build_level(self) -> None:
        expanded = {k: self.expand_dialogue(v) for k, v in DIALOGUES.items()}
        loader = LevelLoader(
            "levels/level3/layout.json",
            self.settings, self.assets, expanded,
        )
        loader.build(self.platforms, self.npcs)
        self.player   = loader.player
        self._world_w = loader.world_w
        if loader.meta.get("name"):
            self.hud.level_name = loader.meta["name"]

    def _on_all_npc_done(self) -> None:
        # 后面还有关卡时发送 next_level
        self.bus.emit("next_level")
        # 如果是最后一关：
        # self.bus.emit("game_over", {"win": True, "score": self.hud.score})
```

**命名约定必须遵守：**
- 目录名：`levels/level3/`
- 类名：`Level3Scene`（`Level` + 数字 + `Scene`）

---

## 步骤 5：完成

不需要改 `main.py`，不需要注册任何东西。

`LevelRegistry` 启动时自动扫描 `levels/levelN/scene.py`，按数字编号排序，Level3Scene 会自动排在 Level2Scene 之后。

```bash
python main.py
```

---

## 自定义过关条件

`_on_all_npc_done()` 在**所有非 optional NPC 的对话都完成**后自动触发。

如果需要额外条件（如关卡 2 的宝石收集），覆写 `update()`：

```python
def update(self, dt: float) -> None:
    super().update(dt)
    # 额外条件：例如玩家到达终点区域
    if self.player and self.player.rect.x > 1800 and not self.completed:
        self.completed = True
        self.bus.emit("next_level")
```

---

## 带题库的问答

对话中加入 `question_pool` 字段，详见 [对话 & 问答系统](11_dialogue_qa.md)。

---

## 关卡专属素材（可选）

将素材放入 `levels/level3/assets/`，会自动优先于通用 `assets/` 中的同名文件。

详见 [素材规范](08_assets.md)。
