# Adventure Quest（冒险问答）

基于 pygame 的 2D 横版闯关 + 问答游戏框架。可直接运行，也可作为二次开发脚手架。

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

> 需要 Python 3.10+，pygame-ce 2.x

## 关卡一览

| 关卡 | 主题 | 玩法 | 过关条件 |
|------|------|------|----------|
| 第一关 | 知识入门 | 横版跑跳，找守门者答题 | 守门者问答全对 |
| 第二关 | 跳跃挑战 | 多平台跳跃，收集宝石，挑战 Boss | 收集 ≥ 3 颗宝石 且 Boss 问答全对 |
| 第三关 | 星星接接乐 | 在底部平台左右移动接住从上方落下的星星 | 接住 ≥ 10 颗星星 且 守门人问答全对 |

## 操作说明

| 按键 | 功能 |
|------|------|
| ← / → / A / D | 左右移动 |
| Space / ↑ / W | 跳跃 |
| E | 与 NPC 对话 |
| Enter | 确认对话 / 选择答案 |
| ↑ / ↓ | 切换选项 |
| ESC | 中断对话 / 返回菜单 |
| C | 开发者跳题（答题激活时有效） |

## 文档导航

| 文档 | 内容 |
|------|------|
| [快速上手](docs/01_quickstart.md) | 安装、运行、目录一览 |
| [操作键位](docs/02_controls.md) | 游戏 & 编辑器所有按键 |
| [目录结构](docs/03_project_structure.md) | 每个文件/目录的职责 |
| [引擎模块](docs/04_engine.md) | Settings / EventBus / AssetLoader / SceneManager / LevelRegistry |
| [场景系统](docs/05_scenes.md) | 场景生命周期、菜单、关卡、胜利页 |
| [实体](docs/06_entities.md) | Player / NPC / Platform / Gem |
| [UI 组件](docs/07_ui.md) | HUD / DialogueBox / MusicControl |
| [素材规范](docs/08_assets.md) | 文件命名、尺寸、三级降级机制 |
| [关卡编辑器](docs/09_level_editor.md) | edit.py 完整使用手册 |
| [新增关卡](docs/10_add_level.md) | 从零添加一关的完整步骤 |
| [对话 & 问答](docs/11_dialogue_qa.md) | 对话数据格式、题库、答题流程 |

## 项目结构速览

```
pygame3/
├── main.py          ← 唯一入口
├── edit.py          ← 可视化关卡编辑器
├── engine/          ← 核心引擎（一般不需要改）
├── scenes/          ← 所有场景（菜单、关卡…）
├── entities/        ← 玩家、NPC、平台
├── ui/              ← HUD、对话框、音乐控制
├── levels/
│   ├── level1/      ← 关卡 1（知识入门）
│   ├── level2/      ← 关卡 2（跳跃挑战）
│   └── level3/      ← 关卡 3（星星接接乐）
└── assets/          ← 图片、音乐素材
```

## 核心特性

- **零素材可运行** — 所有图片缺失时自动用色块占位，不报错
- **自动发现关卡** — `levels/levelN/scene.py` 按编号自动注册，无需修改 `main.py`
- **可视化编辑器** — `python edit.py` 拖拽编辑平台/NPC/宝石位置
- **事件总线解耦** — 场景间通信通过 `EventBus`，不直接引用
- **题库随机抽题** — 每局从题库随机抽取指定数量题目
- **难度自适应** — 第三关星星下落速度和生成频率随进度自动提升
