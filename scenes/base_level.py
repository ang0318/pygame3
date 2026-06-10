"""关卡基类 —— 封装平台物理、摄像机、对话框驱动逻辑

题库格式（在 NPC 对话列表里使用）：
    {
        "question_pool": [          # 题库，任意数量
            {"text": "题目", "choices": ["A","B","C"], "answer": 0},
            ...
        ],
        "question_count": 2,        # 随机抽几题（默认全抽）
    }
开发者快捷键：
    C —— 跳过当前问答，强制判定为正确（仅在问答激活时有效）
"""
from __future__ import annotations
import random
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
        _build_level()       —— 构造平台、NPC、出生点
        _on_all_npc_done()   —— 所有 NPC 对话完成后的回调（过关逻辑）
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

        # 玩家
        self.player: Player | None = None

        # 摄像机偏移（x 轴跟随）
        self._cam_x      = 0.0
        self._world_w    = self.settings.SCREEN_W

        # 当前交互 NPC
        self._active_npc: NPC | None = None
        self._pending_qa: dict | None = None

        # 过关标志
        self.completed   = False

    # ── 子类必须实现 ──────────────────────────────────────────────────────
    def _build_level(self) -> None:
        raise NotImplementedError

    def _on_all_npc_done(self) -> None:
        raise NotImplementedError

    # ── 生命周期 ──────────────────────────────────────────────────────────
    def on_enter(self) -> None:
        self.assets.set_level(getattr(self, "_level_asset_id", None))
        self.platforms.empty()
        self.npcs.clear()
        self.completed      = False
        self._active_npc    = None
        self._pending_qa    = None
        self.dialogue.close()
        self._build_level()

    # ── 题库扩展：构建时把 question_pool 展开为随机抽取的题目序列 ──────────
    @staticmethod
    def expand_dialogue(dialogue: list[dict]) -> list[dict]:
        """
        遍历对话列表，遇到含 question_pool 的条目时随机抽题展开。
        返回新的对话列表，原列表不变。
        """
        result: list[dict] = []
        for entry in dialogue:
            if "question_pool" in entry:
                pool  = entry["question_pool"]
                count = entry.get("question_count", len(pool))
                count = min(count, len(pool))
                picked = random.sample(pool, count)
                result.extend(picked)
            else:
                result.append(entry)
        return result

    # ── 事件 ──────────────────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> None:
        if self.dialogue.active:
            # ESC 中断对话
            if (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                    and not self.dialogue.feedback_timer > 0):
                self._cancel_dialogue()
                return
            # C 键：开发者跳过当前问答，强制正确
            if (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_c
                    and self._pending_qa is not None
                    and not self.dialogue.feedback_timer > 0):
                self._dev_skip_question()
                return
            self.dialogue.handle_event(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self._try_talk()
            elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                # 跳跃用边缘检测，长按不会重复触发
                if self.player:
                    self.player.jump_pressed = True
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

    def _cancel_dialogue(self) -> None:
        """ESC 中断对话：NPC 回到 idle，保留对话进度。"""
        if self._active_npc:
            self._active_npc.talking = False
        self._active_npc  = None
        self._pending_qa  = None
        self.dialogue.close()

    def _dev_skip_question(self) -> None:
        """C 键：开发者跳过，强制当前问答判为正确。"""
        npc = self._active_npc
        if not npc or not self._pending_qa:
            return
        self._last_answer_correct = True
        self._pending_qa = None
        self.hud.score += 100
        npc.advance()
        self.dialogue.show_feedback(True)

    # ── 更新 ──────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        if not self.player:
            return

        if self.dialogue.active:
            self.dialogue.update(dt)

            if self.dialogue.feedback_done:
                self.dialogue.feedback_done = False
                self._handle_feedback_done()
                return

            if self.dialogue.confirmed:
                self._handle_dialogue_confirmed()
            return

        self.player.update(dt, self.platforms)

        for npc in self.npcs:
            npc.update(dt)

        target_x = self.player.rect.centerx - self.settings.SCREEN_W // 2
        self._cam_x += (target_x - self._cam_x) * min(1.0, dt * 8)
        self._cam_x  = max(0, min(self._cam_x, self._world_w - self.settings.SCREEN_W))

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
        """玩家按 Enter 确认。"""
        self.dialogue.confirmed = False
        npc = self._active_npc
        if not npc:
            self.dialogue.close()
            return

        if self._pending_qa:
            correct_idx = self._pending_qa.get("answer", 0)
            chosen      = self.dialogue.selected_index
            is_correct  = (chosen == correct_idx)
            self._last_answer_correct = is_correct
            # 先不清空 _pending_qa，等 feedback 结束再清
            self.dialogue.show_feedback(is_correct)
            if is_correct:
                self.hud.score += 100
                npc.advance()
            return

        has_more = npc.advance()
        self.dialogue.close()
        if has_more:
            self._open_dialogue_step(npc)
        else:
            self._active_npc = None

    def _handle_feedback_done(self) -> None:
        """反馈动画结束后的处理。"""
        npc = self._active_npc
        if not npc:
            self.dialogue.close()
            return

        correct = getattr(self, "_last_answer_correct", False)
        self._pending_qa = None

        if correct:
            d = npc.current_dialogue
            if d is None:
                self.dialogue.close()
                self._active_npc = None
            else:
                self._open_dialogue_step(npc)
        else:
            self._open_dialogue_step(npc)

    # ── 渲染 ──────────────────────────────────────────────────────────────
    def _draw_world(self, screen: pygame.Surface) -> None:
        """绘制世界层（背景、平台、NPC、玩家、HUD），不含对话框。
        子类可在此之后插入额外内容，最后统一调用 dialogue.draw() 保证最高图层。
        """
        bg_key = getattr(self, "_bg_image_key", None)
        if bg_key:
            bg = self.assets.safe_image(
                bg_key,
                (self.settings.SCREEN_W, self.settings.SCREEN_H),
                self.settings.COLOR_BG,
            )
            bg = pygame.transform.scale(
                bg, (self.settings.SCREEN_W, self.settings.SCREEN_H))
            screen.blit(bg, (0, 0))
        else:
            screen.fill(self.settings.COLOR_BG)
        cx = int(self._cam_x)

        for p in self.platforms:
            screen.blit(p.image, (p.rect.x - cx, p.rect.y))

        for npc in self.npcs:
            screen.blit(npc.image, (npc.rect.x - cx, npc.rect.y))
            if self.player:
                npc.draw_hint(screen, self._font_small,
                              self.player.rect, cx)

        if self.player:
            screen.blit(self.player.image,
                        (self.player.rect.x - cx, self.player.rect.y))

        self.hud.draw(screen)

    def draw(self, screen: pygame.Surface) -> None:
        """默认渲染：世界层 + 对话框（最顶层）。"""
        self._draw_world(screen)
        self.dialogue.draw(screen)
