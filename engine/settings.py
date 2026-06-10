"""全局配置，所有可调参数集中管理"""

class Settings:
    # 窗口
    SCREEN_W: int = 960
    SCREEN_H: int = 540
    TITLE: str = "冒险问答"
    FPS: int = 30

    # 物理（按 30fps 校准：每帧步进约为 60fps 的 2 倍）
    GRAVITY: float       = 1.1    # 原 0.6×2≈1.2，略低保留手感
    JUMP_SPEED: float    = -18.0  # 跳跃初速
    PLAYER_SPEED: float  = 7.0    # 移速（30fps 下体感加快）
    JUMP_COOLDOWN: float = 0.05   # 从跳起落地后的再跳冷却（秒），极短防瞬间二连弹
    AIR_DAMPING: float   = 0.80   # 空中松键水平衰减

    # 颜色
    COLOR_BG       = (30,  30,  46)
    COLOR_PLATFORM = (94, 129, 172)
    COLOR_PLAYER   = (166, 227, 161)
    COLOR_NPC      = (250, 179, 135)
    COLOR_TEXT     = (205, 214, 244)
    COLOR_OVERLAY  = (0,   0,   0, 180)
    COLOR_CORRECT  = (166, 227, 161)
    COLOR_WRONG    = (243, 139, 168)
    COLOR_GOLD     = (249, 226, 175)

    # 字体：优先使用系统中文字体名称（SysFont），None 则回退到默认
    # 使用 asset_loader.font() 时传入此值
    FONT_NAME: str = "microsoftyahei"   # 微软雅黑，支持中文
