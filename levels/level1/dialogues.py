"""
关卡 1 对话数据
question_pool: 题库（可放任意数量题目）
question_count: 随机抽几题（省略则全抽）
"""

DIALOGUES: dict[str, list[dict]] = {
    "guide": [
        {"text": "欢迎来到冒险！我是向导阿明。\n用 A/D 或方向键移动，空格/W 跳跃，E 键与 NPC 对话。"},
        {"text": "前方的守门者会考你几道题，答对才能进入下一关。加油！"},
    ],
    "gatekeeper": [
        {"text": "停！想过关？先回答我的问题！"},
        {
            "question_pool": [
                {
                    "text": "Python 中哪个关键字用于定义函数？",
                    "choices": ["class", "def", "func"],
                    "answer": 1,
                },
                {
                    "text": "列表 [1, 2, 3] 的长度是？",
                    "choices": ["2", "3", "4"],
                    "answer": 1,
                },
                {
                    "text": "pygame.display.flip() 的作用是？",
                    "choices": ["关闭窗口", "刷新屏幕", "播放音效"],
                    "answer": 1,
                },
                {
                    "text": "Python 中注释使用哪个符号？",
                    "choices": ["//", "#", "/*"],
                    "answer": 1,
                },
                {
                    "text": "哪个语句用于退出循环？",
                    "choices": ["continue", "pass", "break"],
                    "answer": 2,
                },
            ],
            "question_count": 3,   # 每次随机抽 3 题
        },
        {"text": "全部答对！前方通道已开启，祝你好运！"},
    ],
}
