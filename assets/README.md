# assets/ 素材目录完整规范

## 目录结构

```
assets/
├── README.md            ← 本文件
│
├── bgm.ogg              ← 全局背景音乐（循环播放，缺失则静音）
├── icon_music_on.png    ← 音乐控制图标（开）  18×18 px
├── icon_music_off.png   ← 音乐控制图标（关）  18×18 px
│
│── 通用素材（所有关卡共享）─────────────────────────────────────
├── player_idle_0.png    ← 玩家静止帧         32×48 px
├── player_run_0.png     ┐
├── player_run_1.png     │ 玩家跑步动画（4帧） 32×48 px
├── player_run_2.png     │
├── player_run_3.png     ┘
├── player_jump_0.png    ← 玩家跳跃帧         32×48 px
│
├── npc_guide_idle_0.png       ← 向导 NPC 静止  32×48 px
├── npc_guide_talk_0.png       ← 向导 NPC 说话  32×48 px
├── npc_gatekeeper_idle_0.png  ← 守门者静止     32×48 px
├── npc_gatekeeper_talk_0.png  ← 守门者说话     32×48 px
├── npc_boss_idle_0.png        ← Boss 静止      32×48 px
├── npc_boss_talk_0.png        ← Boss 说话      32×48 px
├── npc_default_idle_0.png     ← 通用 NPC 静止  32×48 px
│
├── platform_default.png ← 通用平台纹理（可平铺，任意尺寸）
├── gem.png              ← 宝石图标            18×18 px
│
└── levels/              ← 关卡专属素材（覆盖同名通用素材）──────
    ├── level1/
    │   ├── platform_default.png  ← 关卡1专属平台纹理（覆盖通用）
    │   ├── npc_guide_idle_0.png  ← 关卡1专属向导外观（覆盖通用）
    │   └── bgm_level.ogg         ← 关卡1专属 BGM（预留，暂未接入）
    └── level2/
        ├── platform_default.png  ← 关卡2专属平台纹理
        ├── npc_boss_idle_0.png   ← 关卡2专属 Boss 外观
        └── gem.png               ← 关卡2专属宝石样式（覆盖通用）
```

---

## 素材查找顺序（三级降级，永不报错）

```
AssetLoader.safe_image("player_idle_0.png", ...)
  ↓ 1. 先找  assets/levels/levelN/player_idle_0.png  （关卡专属）
  ↓ 2. 再找  assets/player_idle_0.png               （通用素材）
  ↓ 3. 最后  生成同尺寸颜色色块                      （兜底，永不崩溃）
```

关卡上下文由 [`base_level.py`](../scenes/base_level.py) 的 `on_enter()` 自动切换，
每关在 `__init__` 中声明 `self._level_asset_id = N` 即可。

---

## 快速替换素材（无需改任何代码）

1. 按上表命名好 PNG 文件
2. 放入对应目录（通用 → `assets/`，关卡专属 → `assets/levels/levelN/`）
3. 重新运行 `python main.py`，自动生效

---

## 新增关卡素材

新建 `scenes/level3.py` 时，同步创建 `assets/levels/level3/` 目录，
只需放入与通用素材**不同**的文件，其余自动复用通用素材。

---

## 命名规范汇总

| 类型 | 命名格式 | 尺寸建议 |
|---|---|---|
| 玩家帧 | `player_{state}_{frame}.png` | 32×48 px |
| NPC 帧 | `npc_{sprite_key}_{state}_{frame}.png` | 32×48 px |
| 平台纹理 | `platform_{sprite_key}.png` | 任意（可平铺） |
| 宝石 | `gem.png` | 18×18 px |
| UI 图标 | `icon_{name}.png` | 18×18 px |
| 背景音乐 | `bgm.ogg` | OGG/MP3/WAV |

---

## 透明度要求

所有角色/道具类图片建议使用 **PNG 透明背景**（RGBA），
pygame 会自动调用 `convert_alpha()` 保留透明通道。
平台纹理可使用不透明 PNG（RGB）。
