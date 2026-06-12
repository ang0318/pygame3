# 场景系统 & 关卡开发指南

---

## 场景是什么

游戏中每个"画面"都是一个场景：主菜单、关卡 1、关卡 2、胜利页…

所有场景继承 [`BaseScene`](../engine/scene_manager.py)，由 [`SceneManager`](../engine/scene_manager.py) 用栈管理。

---

## BaseScene 生命周期

```
push/replace
     ↓
on_enter()     ← 初始化、重置状态
     ↓
loop: handle_event → update → draw
     ↓
on_exit()      ← 清理（pop/replace 时触发）
```

实现一个最简场景：

```python
from engine.scene_manager import BaseScene, SceneManager
import pygame

class MyScene(BaseScene):
    def on_enter(self):
        self._timer = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.pop()   # 返回上一场景

    def update(self, dt):
        self._timer += dt

    def draw(self, screen):
        screen.fill(self.settings.COLOR_BG)
        font = self.assets.font(self.settings.FONT_NAME, 32)
        t = font.render(f"t={self._timer:.1f}", True, self.settings.COLOR_TEXT)
        screen.blit(t, (100, 100))
```

---

## BaseLevelScene — 关卡基类

[`BaseLevelScene`](../scenes/base_level.py) 在 `BaseScene` 基础上封装了：

- 平台物理 & 摄像机跟随（指数平滑，帧率无关）
- NPC 对话 & 问答流程
- HUD 显示
- 背景图加载

子类**只需实现两个方法**：

```python
class Level3Scene(BaseLevelScene):
    def _build_level(self) -> None:
        """构建关卡：加载 JSON，拿到 player / platforms / npcs"""
        ...

    def _on_all_npc_done(self) -> None:
        """所有必须完成的 NPC 对话完成后触发（过关逻辑）"""
        self.bus.emit("next_level")
```

> **过关条件**：只有 `optional=False`（默认）的 NPC 全部 `finished` 才触发 `_on_all_npc_done()`。
> 引导型 NPC 在 layout.json 中设置 `"optional": true` 即可排除在外。

### 可配置属性（在 `__init__` 中设置）

| 属性 | 说明 | 示例 |
|------|------|------|
| `self._level_asset_id` | 关卡素材目录编号 | `1` → `levels/level1/assets/` |
| `self._bg_image_key` | 背景图文件名 | `"bg_level1.png"` |
| `self.hud.level_name` | HUD 顶部显示的关卡名 | `"关卡 1 - 知识入门"` |

---

## 摄像机

`BaseLevelScene` 内置水平摄像机，使用**指数平滑**跟随玩家（帧率无关）：

```python
# 渲染时减去 cam_x 即可
screen.blit(sprite.image, (sprite.rect.x - int(self._cam_x), sprite.rect.y))
```

平滑系数 `speed=6`，约 0.17 秒追上目标位置的 90%，手感流畅不跳变。
摄像机范围自动夹紧到 `[0, world_w - SCREEN_W]`，不会超出关卡边界。

---

## 现有场景速览

| 文件 | 类名 | 职责 |
|------|------|------|
| [`scenes/menu_scene.py`](../scenes/menu_scene.py) | `MenuScene` | 主菜单，发送 `start_game` 事件 |
| [`levels/level1/scene.py`](../levels/level1/scene.py) | `Level1Scene` | 关卡1，问答闯关 |
| [`levels/level2/scene.py`](../levels/level2/scene.py) | `Level2Scene` | 关卡2，宝石+问答 |
| [`scenes/win_scene.py`](../scenes/win_scene.py) | `WinScene` | 胜利/通关庆祝 |

---

## 新增关卡

详见 [如何新增一关](10_add_level.md)。
