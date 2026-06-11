# 引擎模块详解

`engine/` 目录是整个项目的基础设施层，不含任何游戏逻辑，可以直接复用到其他 pygame 项目。

---

## settings.py — 全局配置

所有可调参数集中在 [`Settings`](../engine/settings.py) 类，修改此处即可全局生效，无需改任何其他文件。

```python
class Settings:
    SCREEN_W = 960      # 窗口宽度（px）
    SCREEN_H = 540      # 窗口高度（px）
    TITLE    = "冒险问答"
    FPS      = 30

    # 物理参数（按 30fps 校准）
    GRAVITY      = 1.1    # 重力加速度（px/帧）
    JUMP_SPEED   = -18.0  # 跳跃初速（负值=向上）
    PLAYER_SPEED = 7.0    # 水平移速
    JUMP_COOLDOWN= 0.05   # 落地后再跳冷却（秒）
    AIR_DAMPING  = 0.80   # 空中松键水平衰减

    # 颜色（RGB 或 RGBA）
    COLOR_BG       = (30,  30,  46)
    COLOR_PLATFORM = (94, 129, 172)
    COLOR_PLAYER   = (166, 227, 161)
    COLOR_GOLD     = (249, 226, 175)
    # ... 其余颜色见源文件

    FONT_NAME = "microsoftyahei"   # 系统字体名，支持中文
```

---

## event_bus.py — 事件总线

[`EventBus`](../engine/event_bus.py) 实现发布/订阅模式，让模块之间完全解耦。

### 用法

```python
bus = EventBus()

# 订阅
bus.subscribe("player_died", lambda data: print(data))

# 发布（data 可以是任意类型）
bus.emit("player_died", {"reason": "fall"})

# 取消订阅
bus.unsubscribe("player_died", my_callback)

# 清空所有监听（场景切换时用）
bus.clear()
```

### 项目内置事件

| 事件名 | 触发方 | 监听方 | data 格式 |
|--------|--------|--------|-----------|
| `start_game` | `MenuScene` | `main.py` | `None` |
| `next_level` | 关卡场景 | `main.py` | `None` |
| `game_over` | 关卡场景 | `main.py` | `{"win": bool, "score": int}` |
| `quit` | 任意场景 | `main.py` | `None` |

---

## scene_manager.py — 场景管理器

### BaseScene — 所有场景的基类

```python
class BaseScene(ABC):
    manager: SceneManager   # 可访问 settings / bus / assets
    settings: Settings
    bus:      EventBus
    assets:   AssetLoader

    def on_enter(self) -> None: ...     # 场景激活时调用
    def on_exit(self) -> None: ...      # 场景离开时调用
    def handle_event(self, event): ...  # pygame 事件
    def update(self, dt: float): ...    # 每帧逻辑
    def draw(self, screen): ...         # 每帧渲染
```

### SceneManager — 栈式管理

```python
mgr = SceneManager(settings, bus, assets)

mgr.push(scene)       # 压栈：新场景覆盖旧场景，旧场景暂停
mgr.pop()             # 弹栈：回到上一个场景
mgr.replace(scene)    # 替换栈顶：旧场景被销毁

mgr.current           # 当前场景（只读属性）
```

> **注意**：`push/pop/replace` 是延迟操作，在 `update()` 开始时统一执行，避免在回调中修改栈导致迭代异常。

---

## asset_loader.py — 资源加载器

[`AssetLoader`](../engine/asset_loader.py) 提供带缓存的资源加载，并实现**三级降级**——永不因缺少素材而崩溃。

### 三级查找顺序

```
1. assets/levels/levelN/<filename>   关卡专属素材（最优先）
2. assets/<filename>                 通用素材
3. 同尺寸纯色色块                    兜底，代码自动生成
```

### 常用 API

```python
# 切换关卡上下文（在 on_enter() 中调用）
assets.set_level(1)          # 启用 assets/levels/level1/ 前缀
assets.set_level(None)       # 退回通用目录

# 加载图片（安全，有降级）
surf = assets.safe_image(
    "player_idle_0.png",
    fallback_size=(32, 48),
    fallback_color=(166, 227, 161),
)

# 加载帧序列（内部循环调用 safe_image）
frames = assets.frames(
    "player_run_{}.png",  # {} 会被替换为 0,1,2,3
    count=4,
    fallback_size=(32, 48),
    fallback_color=(166, 227, 161),
)

# 加载字体（缓存）
font = assets.font("microsoftyahei", 22)

# 加载音效（安全，缺失返回 None）
sfx = assets.sound("jump.wav")
if sfx:
    sfx.play()
```

---

## level_loader.py — 关卡布局加载器

[`LevelLoader`](../engine/level_loader.py) 读取 `levels/*.json`，构建平台、NPC、玩家出生点。

```python
loader = LevelLoader(
    "levels/level1_layout.json",
    settings,
    assets,
    dialogue_map,          # { "guide": [...对话数据...] }
)
loader.build(platforms_group, npcs_list)

player  = loader.player    # Player 实例
world_w = loader.world_w   # 关卡总宽度（px）
meta    = loader.meta      # JSON 的 meta 字段
```

JSON 格式参见 [关卡编辑器](09_level_editor.md) 文档。

---

## level_registry.py — 关卡注册表

[`LevelRegistry`](../engine/level_registry.py) 在启动时**自动扫描** `scenes/level*.py`，按编号排序，无需手动注册。

### 约定

- 文件名：`scenes/levelN.py`（N 为正整数）
- 类名：`LevelNScene`（与文件名一致）
- 编号可以不连续（如 1、2、5），按数字升序排列

```python
registry = LevelRegistry(manager)

first = registry.start()     # 返回第一关场景实例
next_ = registry.advance()   # 推进到下一关，已是最后一关返回 None

registry.total          # 关卡总数
registry.current_index  # 当前关卡索引（0-based）
registry.has_next       # 是否还有下一关
```
