# 实体：Player / NPC / Platform / Gem

---

## Player — 玩家

文件：[`entities/player.py`](../entities/player.py)

### 功能

- 左右移动、跳跃、重力、平台碰撞
- 三态动画：`idle` / `run` / `jump`
- 支持图片帧序列，缺失时用色块占位
- 水平镜像翻转（朝向跟随移速方向）

### 创建

```python
player = Player(x=80, y=460, settings=cfg, assets=asset_loader)
```

### 每帧更新

```python
player.update(dt, platforms_group)
```

### 触发跳跃

跳跃用边缘检测（只响应按下瞬间），在 `KEYDOWN` 事件中设置：

```python
if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
    player.jump_pressed = True
```

### 重置位置

```python
player.reset(x, y)   # 重置到指定出生点（速度归零）
```

### 素材约定

| 文件名 | 用途 | 尺寸建议 |
|--------|------|---------|
| `player_idle_0.png` | 静止帧 | 32×48 |
| `player_run_0~3.png` | 跑步动画（4帧） | 32×48 |
| `player_jump_0.png` | 跳跃帧 | 32×48 |

---

## NPC

文件：[`entities/npc.py`](../entities/npc.py)

### 功能

- 玩家靠近（默认 80px 内）时显示闪烁 `[E] 对话` 提示
- 按 E 键触发对话，按对话列表顺序播放
- 支持问答题（带选项），回答完毕标记为 `finished`
- 单套帧动画（idle），无 talking 状态区分

### 创建

```python
npc = NPC(
    x=300, y=400,
    dialogue=[
        {"text": "你好！"},
        {"text": "问题", "choices": ["A", "B", "C"], "answer": 1},
    ],
    settings=cfg,
    name="向导",
    sprite_key="guide",   # 对应 npc_guide_idle_0.png
    assets=asset_loader,
)
```

### 关键属性

| 属性 | 说明 |
|------|------|
| `npc.talking` | 当前是否正在对话 |
| `npc.finished` | 所有对话是否完成 |
| `npc.optional` | 是否为可选 NPC（不计入过关条件） |
| `npc.step` | 当前对话步骤索引 |
| `npc.current_dialogue` | 当前对话条目（dict 或 None） |

### 可选 NPC（optional）

在 layout.json 中标记 `"optional": true`，该 NPC 的对话完成与否**不影响过关判定**。
适合引导型、剧情型 NPC，无需玩家必须交互。

```json
{ "x": 200, "y": 400, "name": "向导", "dialogue_key": "guide", "optional": true }
```

### 朝向规则

素材必须**面朝右**。代码在以下时机自动处理翻转：

- 触发对话时（`try_interact()`）：调用 `face_toward(player_rect)`，NPC 自动朝向玩家
- 也可以手动调用：`npc.face_toward(player_rect)`

### 素材约定

| 文件名 | 用途 |
|--------|------|
| `npc.png` | 所有 NPC 共用的唯一帧（**必须面朝右**） |

### 互动距离

默认 80px，可修改类常量：

```python
NPC.INTERACT_DIST = 100
```

---

## Platform — 静态平台

文件：[`entities/platform.py`](../entities/platform.py)

### 功能

- 静态碰撞体（不移动）
- 支持贴图平铺（图片重复填充至目标尺寸）
- 支持隐形模式（`hidden=True`）：有碰撞，视觉完全透明

### 创建

```python
platform = Platform(
    x=100, y=400,
    w=200, h=20,
    settings=cfg,
    sprite_key="default",   # 对应 platform_default.png
    assets=asset_loader,
    hidden=False,
)
```

### 隐形平台用途

背景图中已绘制地面视觉，但需要保留碰撞体时，把平台设为 `hidden=True`。在关卡编辑器中按 `H` 键切换。

### 素材约定

| 文件名 | 用途 |
|--------|------|
| `platform_{sprite_key}.png` | 平台贴图（可平铺，任意尺寸） |

---

## Gem — 宝石（Level 2 专用）

定义在 [`scenes/level2.py`](../scenes/level2.py) 内，可按需提取到 `entities/`。

### 功能

- 上下浮动动画（正弦波）
- 玩家碰到即拾取（从精灵组移除）
- 支持从 JSON 的 `gems` 字段加载

### JSON 格式

```json
"gems": [
    {"x": 400, "y": 300},
    {"x": 600, "y": 200, "hidden": true}
]
```

`hidden: true` 的宝石在游戏中**不创建**（不可见也不可拾取）。
