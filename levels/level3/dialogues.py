"""
关卡 3 对话数据
过关条件：接住 >= 10 个下落物品 且 守门人所有问答正确
"""

DIALOGUES: dict[str, list[dict]] = {
    "hint": [
        {"text": "欢迎来到第三关！天空中会不断落下星星，用左右方向键移动接住它们！\n接满 10 颗后来找我答题，即可通关！"},
    ],
    "gatekeeper": [
        {"text": "干得不错！接住了足够多的星星！现在接受最终考验，回答我的问题！"},
        {
            "question_pool": [
                {
                    "text": "Python 中如何定义一个只读属性？",
                    "choices": ["@staticmethod", "@property", "@classmethod"],
                    "answer": 1,
                },
                {
                    "text": "pygame.sprite.Group 的 draw() 方法需要哪个参数？",
                    "choices": ["Surface（屏幕）", "Rect（区域）", "Color（颜色）"],
                    "answer": 0,
                },
                {
                    "text": "以下哪个方法用于检测两个精灵组之间的碰撞？",
                    "choices": ["spritecollide()", "groupcollide()", "colliderect()"],
                    "answer": 1,
                },
                {
                    "text": "Python 中 enumerate() 函数的作用是？",
                    "choices": ["返回元素个数", "同时返回索引和值", "生成随机排列"],
                    "answer": 1,
                },
                {
                    "text": "pygame.time.Clock.tick(FPS) 返回的是？",
                    "choices": ["当前帧率", "上一帧到本帧的毫秒数", "游戏总运行秒数"],
                    "answer": 1,
                },
                {
                    "text": "下列哪个数据结构是 FIFO（先进先出）？",
                    "choices": ["栈（Stack）", "队列（Queue）", "树（Tree）"],
                    "answer": 1,
                },
                {
                    "text": "Python 的 __init__.py 文件的作用是？",
                    "choices": ["初始化变量", "标记目录为包", "定义入口函数"],
                    "answer": 1,
                },
                {
                    "text": "以下哪个关键字用于捕获异常？",
                    "choices": ["catch", "except", "handle"],
                    "answer": 1,
                },
            ],
            "question_count": 3,
        },
        {"text": "太厉害了！三关全部通关！你是真正的编程勇者！"},
    ],
}

# 守门人：物品数量不足时的提示
GATEKEEPER_LOCKED = [{"text": "你接到的星星还不够多，继续努力吧！"}]
