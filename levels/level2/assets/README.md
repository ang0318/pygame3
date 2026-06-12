# 关卡 2 专属素材

把关卡 2 的图片、音效放在这里。

引擎查找优先级：
1. `levels/level2/assets/<文件名>`  ← 本目录（优先）
2. `assets/<文件名>`                ← 通用素材（兜底）

## 常用文件名约定

| 文件名             | 用途               |
|--------------------|--------------------|
| `bg_level2.png`    | 关卡背景图         |
| `player_idle_0.png`| 玩家静止帧         |
| `player_run_0.png` | 玩家跑步帧         |
| `guide.png`        | NPC 引导者贴图     |
| `gatekeeper.png`   | NPC Boss 贴图      |
| `platform.png`     | 平台贴图           |
| `gem.png`          | 宝石贴图           |

不需要的文件名直接不放，引擎会自动用 `assets/` 里的通用版本或颜色色块兜底。
