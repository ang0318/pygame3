"""全局配置，所有可调参数集中管理"""

class Settings:
    # 窗口
    SCREEN_W: int = 960
    SCREEN_H: int = 540
    TITLE: str = "冒险问答"
    FPS: int = 60

    # 物理
    GRAVITY: float = 0.6
    JUMP_SPEED: float = -14.0
    PLAYER_SPEED: float = 4.0

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
