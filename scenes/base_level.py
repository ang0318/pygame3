"""关卡基类 —— 封装平台物理、摄像机、对话框驱动逻辑"""
from __future__ import annotations
import pygame
from engine.scene_manager import BaseScene, SceneManager
from entities.player   import Player
from entities.npc      import NPC
from entities.platform import Platform
from ui.dialogue_box   import DialogueBox
from ui.hud            import HUD


class BaseLevelScene(BaseScene):
    """
    子类只需实现：
        _build_level()   —— 构造平台、NPC、出生点
        _on_all_npc_done()  —— 所有 NPC 对话完成后的回调（过关逻辑）
    """

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)

        # 字体
        self._font       = self.assets.font(self.settings.FONT_NAME, 22)
        self._font_small = self.assets.font(self.settings.FONT_NAME, 18)

        # 精灵组
        self.platforms   = pygame.sprite.Group()
        self.npcs:       list[NPC] = []

        # UI
        self.dialogue    = DialogueBox(self.settings, self._font, self._font_small)
        self.hud         = HUD(self.settings, self._font)

        # 玩家（稍后由子类 _build_level 确定坐标）
        self.player: Player | None = None

        # 摄像机偏移（x 轴跟随）
        self._cam_x      = 0.0
        self._world_w    = self.settings.SCREEN_W   # 子类可覆盖

        # 当前交互 NPC
        self._active_npc: NPC | None = None
        self._pending_qa: dict | None = None   # 待评判的问答

        # 过关标志
        self.completed   = False

    # ── 子类必须实现 ──────────────────────────────────────────────────────
    def _build_level(self) -> None:
        raise NotImplementedError

    def _on_all_npc_done(self) -> None:
        raise NotImplementedError

    # ── 生命周期 ──────────────────────────────────────────────────────────
    def on_enter(self) -> None:
        # 每次进入都重建（支持重玩）
        self.platforms.empty()
        self.npcs.clear()
        self.completed      = False
        self._active_npc    = None
        self._pending_qa    = None
        self.dialogue.close()
        self._build_level()

    # ── 事件 ──────────────────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> None:
        if self.dialogue.active:
            self.dialogue.handle_event(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self._try_talk()
            elif event.key == pygame.K_ESCAPE:
                from scenes.menu_scene import MenuScene
                self.manager.replace(MenuScene(self.manager))

    def _try_talk(self) -> None:
        if not self.player:
            return
        for npc in self.npcs:
            if npc.try_interact(self.player.rect):
                self._active_npc = npc
                self._open_dialogue_step(npc)
                break

    # ── 更新 ──────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        if not self.player:
            return

        # 对话框驱动
        if self.dialogue.active:
            self.dialogue.update(dt)
            if self.dialogue.confirmed:
                self._handle_dialogue_confirmed()
            return   # 对话期间冻结玩家

        # 玩家 & 平台
        self.player.update(dt, self.platforms)

        # NPC
        for npc in self.npcs:
            npc.update(dt)

        # 摄像机跟随（水平，带边界夹紧）
        target_x = self.player.rect.centerx - self.settings.SCREEN_W // 2
        self._cam_x += (target_x - self._cam_x) * min(1.0, dt * 8)
        self._cam_x  = max(0, min(self._cam_x, self._world_w - self.settings.SCREEN_W))

        # 检查过关
        if not self.completed and all(n.finished for n in self.npcs):
            self.completed = True
            self._on_all_npc_done()

    # ── 对话流程 ──────────────────────────────────────────────────────────
    def _open_dialogue_step(self, npc: NPC) -> None:
        d = npc.current_dialogue
        if d is None:
            return
        self.dialogue.open(d["text"], d.get("choices"))
        if d.get("choices"):
            self._pending_qa = d
        else:
            self._pending_qa = None

    def _handle_dialogue_confirmed(self) -> None:
        npc = self._active_npc
        if not npc:
            self.dialogue.close()
            return

        if self._pending_qa:
            # 问答判断
            correct_idx = self._pending_qa.get("answer", 0)
            chosen      = self.dialogue.selected_index
            is_correct  = (chosen == correct_idx)
            self._pending_qa = None
            self.dialogue.show_feedback(is_correct)
            if is_correct:
                self.hud.score += 100
                npc.advance()   # 推进到下一句
            # 答错时 npc.step 不变，feedback 结束后会重新显示同一题
            return

        # 普通对话
        has_more = npc.advance()
        self.dialogue.close()
        if has_more:
            self._open_dialogue_step(npc)
        else:
            self._active_npc = None

    # ── 渲染 ──────────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(self.settings.COLOR_BG)
        cx = int(self._cam_x)

        # 平台
        for p in self.platforms:
            screen.blit(p.image, (p.rect.x - cx, p.rect.y))

        # NPC
        for npc in self.npcs:
            screen.blit(npc.image, (npc.rect.x - cx, npc.rect.y))
            if self.player:
                # 临时偏移 player.rect 用于距离判断
                shifted = self.player.rect.move(0, 0)
                npc.draw_hint(screen, self._font_small,
                              pygame.Rect(self.player.rect.x - cx,
                                          self.player.rect.y,
                                          self.player.rect.w,
                                          self.player.rect.h))

        # 玩家
        if self.player:
            screen.blit(self.player.image,
                        (self.player.rect.x - cx, self.player.rect.y))

        # UI
        self.hud.draw(screen)
        self.dialogue.draw(screen)
