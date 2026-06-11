# 对话 & 问答系统详解

---

## 对话数据结构

每个 NPC 绑定一个对话列表（`list[dict]`），按顺序逐条播放。

### 普通对话（无选项）

```python
{"text": "你好！这是普通对话，按 Enter 继续。"}
```

### 问答题（有选项）

```python
{
    "text": "下列哪个是 Python 的关键字？",
    "choices": ["print", "def", "run"],
    "answer": 1,   # 正确答案的索引（0-based），"def" 是正确答案
}
```

- `choices`：选项列表，↑↓ 切换，Enter 确认
- `answer`：正确选项的索引（从 0 开始）
- 答错时显示红色反馈，**重新播放该题**（NPC 不前进）
- 答对时显示绿色反馈，NPC 前进到下一步，`hud.score += 100`

---

## 题库（随机抽题）

题库用 `question_pool` 替代单道题，每次游戏随机抽取指定数量：

```python
{
    "question_pool": [
        {"text": "题目1", "choices": ["A","B","C"], "answer": 0},
        {"text": "题目2", "choices": ["X","Y","Z"], "answer": 2},
        {"text": "题目3", "choices": ["P","Q","R"], "answer": 1},
        # 可以放任意多道题
    ],
    "question_count": 2,   # 每次随机抽 2 道（省略则全部出题）
}
```

展开题库发生在 `_build_level()` 中：

```python
expanded = {k: self.expand_dialogue(v) for k, v in _DIALOGUES.items()}
```

`expand_dialogue()` 是 `BaseLevelScene` 的静态方法，遇到 `question_pool` 就随机抽题并展开为普通题目列表，原列表不变。

---

## 完整对话示例

```python
_DIALOGUES = {
    "guide": [
        {"text": "欢迎！我是向导。"},            # 普通对话
        {"text": "跟我学一道题："},              # 普通对话
        {
            "text": "1+1=?",
            "choices": ["1", "2", "3"],
            "answer": 1,
        },                                        # 单道题
        {"text": "答对了！继续前进！"},           # 普通对话（答对后才到这里）
    ],
    "boss": [
        {"text": "接受终极考验！"},
        {
            "question_pool": [
                {"text": "A?", "choices": ["a","b"], "answer": 0},
                {"text": "B?", "choices": ["c","d"], "answer": 1},
                {"text": "C?", "choices": ["e","f"], "answer": 0},
            ],
            "question_count": 2,    # 从 3 道中随机抽 2 道
        },
        {"text": "全部正确！通关！"},
    ],
}
```

---

## 对话流程图

```
玩家按 E
   ↓
NPC.try_interact() → 开启 talking 状态
   ↓
_open_dialogue_step(npc)
   ↓
有 choices？
├─ 否 → 显示文字，等待 Enter → npc.advance() → 下一步
└─ 是 → 显示文字+选项，等待 Enter
              ↓
         判断答案
         ├─ 正确 → show_feedback(True) → npc.advance() → 下一步
         └─ 错误 → show_feedback(False) → 重放当前题
                          ↓
                   feedback_done=True（动画结束）
```

---

## ESC 中断对话

按 `ESC` 可随时中断对话，NPC 进度**不会丢失**（`npc.step` 保留），下次靠近再按 E 可从头重新对话（`try_interact` 重置 `step=0`）。

如需从中断处续接，可修改 `try_interact()` 不重置 step：

```python
def try_interact(self, player_rect):
    if self.finished:
        return False
    dist = abs(self.rect.centerx - player_rect.centerx)
    if dist < self.INTERACT_DIST and not self.talking:
        self.talking = True
        # self.step = 0   ← 注释掉这行，则续接上次进度
        return True
    return False
```

---

## 开发者模式

对话激活时按 `C` 键，跳过当前问答并强制判为正确（得分 +100），方便测试关卡流程而不用每次都答题。

此功能在 [`scenes/base_level.py`](../scenes/base_level.py) 的 `_dev_skip_question()` 中实现，发布版可按需删除对应的 `elif event.key == pygame.K_c` 分支。

---

## 在 NPC 完成后触发自定义逻辑

`BaseLevelScene` 在所有 NPC 均 `finished=True` 时自动调用 `_on_all_npc_done()`：

```python
def _on_all_npc_done(self) -> None:
    # 默认行为：进入下一关
    self.bus.emit("next_level")
```

也可以在这里触发动画、解锁门、播放音效等。
