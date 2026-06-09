"""
Adventure Quest — 主入口
运行方式：python main.py
"""
import sys
import pygame

from engine.settings     import Settings
from engine.event_bus    import EventBus
from engine.asset_loader import AssetLoader
from engine.scene_manager import SceneManager
from scenes.menu_scene   import MenuScene


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

    # 退出事件
    running = True
    def _quit(_=None):
        nonlocal running
        running = False
    bus.subscribe("quit", _quit)

    # 初始场景
    mgr.push(MenuScene(mgr))

    while running:
        dt = clock.tick(cfg.FPS) / 1000.0   # 秒

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            mgr.handle_event(event)

        mgr.update(dt)
        mgr.draw(screen)
        pygame.display.flip()

        # 没有场景则退出
        if mgr.current is None:
            running = False

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
