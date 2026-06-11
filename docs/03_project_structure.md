# 项目目录结构

```
pygame3/
├── main.py                  ← 主入口（初始化 + 主循环）
├── edit.py                  ← 关卡可视化编辑器
├── requirements.txt         ← 依赖声明
│
├── engine/                  ← 核心引擎（不含游戏逻辑）
│   ├── settings.py          ← 全局配置（分辨率、物理参数、颜色）
│   ├── event_bus.py         ← 发布/订阅事件总线
│   ├── scene_manager.py     ← 场景基类 + 栈式场景管理器
│   ├── asset_loader.py      ← 资源加载器（带缓存 + 三级降级）
│   ├── level_loader.py      ← JSON 关卡布局加载器
│   └── level_registry.py   ← 自动扫描 scenes/level*.py 的关卡注册表
│
├── scenes/                  ← 所有场景
│   ├── base_level.py        ← 关卡基类（物理、摄像机、对话驱动）
│   ├── level1.py            ← 关卡 1 场景
│   ├── level2.py            ← 关卡 2 场景（宝石 + Boss）
│   ├── menu_scene.py        ← 主菜单
│   └── win_scene.py         ← 通关庆祝页
│
├── entities/                ← 游戏实体
│   ├── player.py            ← 玩家（移动、跳跃、动画）
│   ├── npc.py               ← NPC（对话触发、状态机）
│   └── platform.py          ← 静态平台（碰撞体 + 贴图平铺）
│
├── ui/                      ← UI 组件
│   ├── dialogue_box.py      ← 对话框（打字机 + 选项高亮）
│   ├── hud.py               ← 顶部状态栏（分数、关卡名、生命）
│   └── music_control.py     ← 右上角音乐控制条
│
├── levels/                  ← 关卡布局数据
│   ├── level1_layout.json
│   └── level2_layout.json
│
├── assets/                  ← 素材目录
│   ├── README.md            ← 素材规范说明（指向 docs/08_assets.md）
│   └── levels/
│       ├── level1/          ← 关卡 1 专属素材（可选）
│       └── level2/          ← 关卡 2 专属素材（可选）
│
└── docs/                    ← 本文档目录
    ├── 01_quickstart.md
    ├── 02_controls.md
    ├── 03_project_structure.md
    ├── 04_engine.md
    ├── 05_scenes.md
    ├── 06_entities.md
    ├── 07_ui.md
    ├── 08_assets.md
    ├── 09_level_editor.md
    ├── 10_add_level.md
    └── 11_dialogue_qa.md
```

## 各层职责一览

| 层 | 目录/文件 | 说明 |
|----|-----------|------|
| 入口 | `main.py` | 初始化 pygame、管理 BGM、绑定事件总线回调 |
| 引擎 | `engine/` | 无游戏逻辑的通用基础设施 |
| 场景 | `scenes/` | 每个 `levelN.py` 就是一关，增删不影响其他代码 |
| 实体 | `entities/` | 独立的游戏对象，只依赖 engine |
| UI | `ui/` | 独立渲染组件，不持有场景引用 |
| 数据 | `levels/*.json` | 由编辑器生成，手动改也没问题 |
| 素材 | `assets/` | 图片/音频，缺失时自动降级为色块 |
