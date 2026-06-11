# 快速上手

## 环境要求

- Python 3.10 或更高
- pygame-ce 2.x（`requirements.txt` 已指定）

## 安装

```bash
# 克隆或下载项目后，在项目根目录执行：
pip install -r requirements.txt
```

## 运行游戏

```bash
python main.py
```

启动后显示主菜单，↑↓ 选择，Enter 确认。

## 运行关卡编辑器

```bash
python edit.py
```

启动后在终端列出所有关卡，输入编号进入可视化编辑窗口。

## 没有素材也能运行

项目内置"三级降级"机制：图片缺失时自动用纯色色块占位，**不会报错也不会崩溃**。你可以先跑起来，再慢慢替换素材。

## 目录一览

```
pygame3/
├── main.py              ← 游戏入口，只管初始化和主循环
├── edit.py              ← 关卡可视化编辑器
├── requirements.txt     ← 依赖列表
│
├── engine/              ← 核心引擎（通常不需要修改）
│   ├── settings.py      ← 全局配置（分辨率、物理参数、颜色…）
│   ├── event_bus.py     ← 发布/订阅事件总线
│   ├── asset_loader.py  ← 资源加载器（带缓存 + 三级降级）
│   ├── scene_manager.py ← 场景基类 + 栈式场景管理器
│   ├── level_loader.py  ← 从 JSON 构建关卡实体
│   └── level_registry.py← 自动扫描 scenes/level*.py
│
├── scenes/              ← 所有场景
│   ├── menu_scene.py    ← 主菜单
│   ├── base_level.py    ← 关卡基类（物理、摄像机、对话驱动）
│   ├── level1.py        ← 关卡 1
│   ├── level2.py        ← 关卡 2（含宝石收集玩法）
│   └── win_scene.py     ← 通关庆祝页
│
├── entities/            ← 游戏实体
│   ├── player.py        ← 玩家（移动、跳跃、动画）
│   ├── npc.py           ← NPC（对话、状态机）
│   └── platform.py      ← 平台（静态碰撞体）
│
├── ui/                  ← UI 组件
│   ├── hud.py           ← 顶部状态栏（分数、生命、关卡名）
│   ├── dialogue_box.py  ← 对话框（打字机 + 选项）
│   └── music_control.py ← 右上角音乐控制条
│
├── levels/              ← 关卡布局数据
│   ├── level1_layout.json
│   └── level2_layout.json
│
└── assets/              ← 素材（图片、音乐）
    ├── README.md        ← 素材规范（旧版，详见 docs/08_assets.md）
    └── levels/          ← 关卡专属素材目录
```

## 下一步

- 想改游戏参数 → [引擎模块](04_engine.md)
- 想加新关卡 → [新增关卡](10_add_level.md)
- 想替换图片 → [素材规范](08_assets.md)
- 想编辑关卡布局 → [关卡编辑器](09_level_editor.md)
