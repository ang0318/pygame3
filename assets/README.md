# assets/ 素材目录说明

所有素材放在此目录下，游戏会自动检测是否存在：
- 存在 → 使用真实素材
- 缺失 → 自动用同尺寸颜色方块代替，逻辑不受任何影响

---

## 玩家素材（建议 32×48 px，PNG 透明背景）

| 文件名 | 说明 |
|---|---|
| `player_idle_0.png` | 静止帧（1 帧） |
| `player_run_0.png` ~ `player_run_3.png` | 跑步动画（4 帧） |
| `player_jump_0.png` | 跳跃帧（1 帧） |

---

## NPC 素材（建议 32×48 px，PNG 透明背景）

文件名格式：`npc_{sprite_key}_{状态}_{帧号}.png`

| sprite_key | 说明 |
|---|---|
| `guide` | 向导 NPC |
| `gatekeeper` | 关卡1 守门者 |
| `boss` | 关卡2 最终 Boss |

例：
- `npc_guide_idle_0.png`
- `npc_boss_talk_0.png`

---

## 平台素材（可平铺纹理，任意尺寸）

文件名格式：`platform_{sprite_key}.png`

| sprite_key | 说明 |
|---|---|
| `default` | 通用平台（目前所有平台使用此 key） |
| `grass` | 草地平台（预留） |
| `stone` | 石头平台（预留） |

---

## 宝石素材

| 文件名 | 建议尺寸 |
|---|---|
| `gem.png` | 18×18 px |

---

## 背景素材（预留，暂未接入）

| 文件名 | 说明 |
|---|---|
| `bg_level1.png` | 关卡1 背景 |
| `bg_level2.png` | 关卡2 背景 |

---

## 快速替换方法

1. 按上表命名好素材文件
2. 放入 `assets/` 目录
3. 重新运行 `python main.py`，自动生效，无需改动任何代码
