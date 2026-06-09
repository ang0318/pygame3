"""
Adventure Quest — 主入口
职责（仅此三项，永远不需要改）：
  1. 初始化 pygame、窗口、时钟
  2. 管理背景音乐 + MusicControl UI
  3. 监听事件总线：
       next_level  → 推进到下一关（LevelRegistry 自动找到正确的关卡类）
       game_over   → 显示胜利/失败结算页
       quit        → 退出
"""
import sys
import pygame

from engine.settings       import Settings
from engine.event_bus      import EventBus
from engine.asset_loader   import AssetLoader
from engine.scene_manager  import SceneManager
from engine.level_registry import LevelRegistry
from ui.music_control      import MusicControl
from scenes.menu_scene     import MenuScene


def _try_play_music(path: str, volume: float = 0.5) -> None:
    """尝试播放背景音乐，文件不存在时静默跳过。"""
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)   # -1 = 无限循环
    except Exception:
        pass   # 没有音乐文件时不报错


def main() -> None:
    pygame.init()
    pygame.mixer.init()

    cfg    = Settings()
    screen = pygame.display.set_mode((cfg.SCREEN_W, cfg.SCREEN_H))
    pygame.display.set_caption(cfg.TITLE)
    clock  = pygame.time.Clock()

    bus    = EventBus()
    assets = AssetLoader()
    mgr    = SceneManager(cfg, bus, assets)

    # ── 背景音乐（素材缺失则静默） ────────────────────────────────────────
    _try_play_music("assets/bgm.ogg")
    music_ui = MusicControl(cfg, assets)

    # ── 关卡注册表（自动扫描 scenes/level*.py） ───────────────────────────
    registry = LevelRegistry(mgr)

    # ── 事件总线回调 ──────────────────────────────────────────────────────
    running = True

    def _on_quit(_=None) -> None:
        nonlocal running
        running = False

    def _on_next_level(_=None) -> None:
        """推进到下一关；若已是最后一关则触发 game_over。"""
        scene = registry.advance()
        if scene:
            mgr.replace(scene)
        else:
            bus.emit("game_over", {"win": True, "score": 0})

    def _on_game_over(data: dict | None) -> None:
        data = data or {}
        from scenes.win_scene import WinScene
        score = data.get("score", 0)
        mgr.replace(WinScene(mgr, score))

    bus.subscribe("quit",       _on_quit)
    bus.subscribe("next_level", _on_next_level)
    bus.subscribe("game_over",  _on_game_over)

    # ── 初始场景：主菜单 ──────────────────────────────────────────────────
    # 菜单"开始游戏"后由菜单自己把第一关压入栈；
    # 这里提前把 registry.start() 与菜单关联。
    def _start_game(_=None) -> None:
        scene = registry.start()
        if scene:
            mgr.replace(scene)

    bus.subscribe("start_game", _start_game)
    mgr.push(MenuScene(mgr))

    # ── 主循环 ────────────────────────────────────────────────────────────
    while running:
        dt = clock.tick(cfg.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            music_ui.handle_event(event)
            mgr.handle_event(event)

        mgr.update(dt)
        mgr.draw(screen)

        # MusicControl 始终浮于最顶层
        music_ui.draw(screen)
        pygame.display.flip()

        if mgr.current is None:
            running = False

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
