"""
关卡 2 对话数据
过关条件：收集 >= 3 颗宝石 且 Boss 所有问答正确
"""

DIALOGUES: dict[str, list[dict]] = {
    "intro": [
        {"text": "关卡 2！收集 3 颗以上宝石，再来挑战 Boss！"},
    ],
    "boss": [
        {"text": "不错，宝石收集达标！现在接受终极考验！"},
        {
            "question_pool": [
                {
                    "text": "下列哪个是不可变（immutable）类型？",
                    "choices": ["list", "dict", "tuple"],
                    "answer": 2,
                },
                {
                    "text": "O(n log n) 是哪种排序算法的平均复杂度？",
                    "choices": ["冒泡排序", "插入排序", "快速排序"],
                    "answer": 2,
                },
                {
                    "text": "pygame 中检测矩形碰撞用哪个方法？",
                    "choices": ["rect.hit()", "rect.colliderect()", "rect.overlap()"],
                    "answer": 1,
                },
                {
                    "text": "Python 中哪个内置函数返回列表长度？",
                    "choices": ["size()", "count()", "len()"],
                    "answer": 2,
                },
                {
                    "text": "以下哪个关键字用于继承父类？",
                    "choices": ["extends", "super", "class 子(父)"],
                    "answer": 2,
                },
                {
                    "text": "哪个符号用于 Python 的幂运算？",
                    "choices": ["^", "**", "pow"],
                    "answer": 1,
                },
            ],
            "question_count": 3,   # 每次随机抽 3 题
        },
        {"text": "全部正确！你已通关所有关卡！感谢游玩！"},
    ],
}

# Boss 未满足宝石条件时的提示
BOSS_LOCKED = [{"text": "你还没收集到足够的宝石，先去探索地图吧！"}]
