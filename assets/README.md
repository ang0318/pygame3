# assets/ 素材目录完整规范

## 目录结构

```
assets/
├── README.md                  ← 本文件
│
├── 音乐 ───────────────────────────────────────────────────────────────
├── bgm.mp3 / bgm.ogg / bgm.wav   ← 全局背景音乐（自动探测，三选一即可）
│
├── 背景图 ─────────────────────────────────────────────────────────────
├── bg_menu.png                ← 主菜单背景（缺失则显示动态网格）
├── bg_level1.png              ← 关卡1背景（缺失则纯色填充）
├── bg_level2.png              ← 关卡2背景（缺失则纯色填充）
│   ※ 尺寸建议 960×540 px，会自动拉伸适配窗口
│
├── UI 图标（全部纯代码绘制，此处无需放文件）──────────────────────────
│   音乐控制图标已内置，不依赖任何图片
│
├── 通用角色素材 ────────────────────────────────────────────────────────
├── player_idle_0.png          ← 玩家静止帧         32×48 px
├── player_run_0.png ~ _3.png  ← 玩家跑步动画（4帧） 32×48 px
├── player_jump_0.png          ← 玩家跳跃帧         32×48 px
│
├── npc_{sprite_key}_idle_0.png   ← NPC 静止帧      32×48 px
├── npc_{sprite_key}_talk_0.png   ← NPC 说话帧      32×48 px
│   sprite_key 预设值：guide / gatekeeper / boss / default
│
├── platform_default.png       ← 通用平台纹理（可平铺，任意尺寸）
├── gem.png                    ← 宝石图标            18×18 px
│
└── levels/                    ← 关卡专属素材（覆盖同名通用素材）
    ├── level1/
    │   ├── bg_level1.png      ← 关卡1背景（也可放这里，效果相同）
    │   ├── platform_default.png
    │   └── npc_guide_idle_0.png
    └── level2/
        ├── bg_level2.png
        ├── platform_default.png
        └── gem.png
```

---

## 素材三级降级（永不报错）

```
1. assets/levels/levelN/<filename>   关卡专属（最优先）
2. assets/<filename>                 通用素材
3. 同尺寸颜色色块                    兜底，代码自动生成
```

---

## 背景图规范

| 文件名 | 对应场景 | 说明 |
|---|---|---|
| `bg_menu.png` | 主菜单 | 缺失时显示动态网格动效 |
| `bg_level1.png` | 关卡1 | 缺失时纯色 (#1e1e2e) |
| `bg_level2.png` | 关卡2 | 缺失时纯色 (#1e1e2e) |

新增关卡时在对应 `level*.py` 中设置：
```python
self._bg_image_key = "bg_level3.png"
```

---

## 背景音乐规范

`main.py` 自动按 `.mp3 → .ogg → .wav` 顺序探测，放一个即可：
```
assets/bgm.mp3    ← 推荐（最通用）
assets/bgm.ogg    ← 次选
assets/bgm.wav    ← 备选（文件较大）
```

---

## 编辑器中的隐藏物体

`edit.py` 中按 `H` 可将选中物体切换为**隐藏**状态：
- 编辑器中以半透明显示
- JSON 中记录 `"hidden": true`
- 游戏中**仍然有效**（碰撞正常，只是没有视觉渲染）
- 适合用于：背景图中已有地面视觉，但需要保留碰撞体的场景

---

## 快速替换素材

1. 按上表命名好文件
2. 放入 `assets/` 或 `assets/levels/levelN/`
3. 重新运行 `python main.py`，自动生效，无需改代码

---

## 命名规范汇总

| 类型 | 命名格式 | 尺寸建议 |
|---|---|---|
| 玩家帧 | `player_{state}_{frame}.png` | 32×48 |
| NPC 帧 | `npc_{key}_{state}_{frame}.png` | 32×48 |
| 平台纹理 | `platform_{key}.png` | 任意（可平铺） |
| 宝石 | `gem.png` | 18×18 |
| 背景图 | `bg_{scene}.png` | 960×540 |
| 背景音乐 | `bgm.mp3` / `.ogg` / `.wav` | — |
