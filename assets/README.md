# assets/ 素材目录

素材规范已迁移至 [`docs/08_assets.md`](../docs/08_assets.md)，内容更完整、分类更清晰。

## 快速索引

- 素材命名规范 → [docs/08_assets.md](../docs/08_assets.md)
- 三级降级机制 → [docs/08_assets.md#三级降级机制](../docs/08_assets.md)
- 背景图/音乐规范 → [docs/08_assets.md#背景图](../docs/08_assets.md)
- 关卡专属素材 → [docs/08_assets.md#三级降级机制](../docs/08_assets.md)

## 目录结构

```
assets/
├── bgm.mp3 / bgm.ogg / bgm.wav    ← 背景音乐（三选一）
├── bg_menu.png                     ← 主菜单背景
├── bg_level1.png                   ← 关卡1背景
├── bg_level2.png                   ← 关卡2背景
├── player_idle_0.png               ← 玩家静止帧
├── player_run_0~3.png              ← 玩家跑步动画（4帧）
├── player_jump_0.png               ← 玩家跳跃帧
├── npc_{key}_idle_0.png            ← NPC 静止帧
├── npc_{key}_talk_0.png            ← NPC 说话帧
├── platform_default.png            ← 通用平台贴图
├── gem.png                         ← 宝石图标
└── levels/
    ├── level1/                     ← 关卡1专属素材（可选，覆盖通用）
    └── level2/                     ← 关卡2专属素材（可选，覆盖通用）
```

所有素材缺失时自动用色块占位，不会导致游戏崩溃。
