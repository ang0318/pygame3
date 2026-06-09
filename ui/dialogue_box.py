"""对话框 UI —— 打字机效果 + 多选项高亮"""
from __future__ import annotations
import pygame
from engine.settings import Settings


class DialogueBox:
    """
    使用方法：
        box.open(text, choices=["A","B","C"])  # choices=None 表示只有"继续"
        box.update(dt)
        box.draw(screen)
        if box.confirmed:
            idx = box.selected_index   # None 表示无选项
            box.close()
    """

    PAD    = 18
    RADIUS = 12

    def __init__(self, settings: Settings, font: pygame.font.Font,
                 small_font: pygame.font.Font) -> None:
        self.cfg         = settings
        self.font        = font
        self.small_font  = small_font

        W, H = settings.SCREEN_W, settings.SCREEN_H
        bw, bh = W - 80, 160
        self.box_rect = pygame.Rect(40, H - bh - 20, bw, bh)

        self.active          = False
        self.text            = ""
        self.choices: list[str] | None = None
        self.selected_index  = 0
        self.confirmed       = False
        self.feedback: str | None = None   # "correct" | "wrong"
        self.feedback_timer  = 0.0

        # 打字机
        self._full_text   = ""
        self._char_index  = 0.0
        self._char_speed  = 40.0   # 字符/秒
        self._done_typing = False

    # ── 公开 API ─────────────────────────────────────────────────────────
    def open(self, text: str, choices: list[str] | None = None) -> None:
        self.active          = True
        self.confirmed       = False
        self._full_text      = text
        self._char_index     = 0.0
        self._done_typing    = False
        self.text            = ""
        self.choices         = choices
        self.selected_index  = 0
        self.feedback        = None

    def close(self) -> None:
        self.active    = False
        self.confirmed = False

    def show_feedback(self, correct: bool) -> None:
        self.feedback       = "correct" if correct else "wrong"
        self.feedback_timer = 1.2

    # ── 更新 ─────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        if not self.active:
            return
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.feedback = None
                self.confirmed = True   # 反馈结束后自动确认
            return
        if not self._done_typing:
            self._char_index += self._char_speed * dt
            idx = min(int(self._char_index), len(self._full_text))
            self.text = self._full_text[:idx]
            if idx >= len(self._full_text):
                self._done_typing = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.active or self.feedback_timer > 0:
            return
        if event.type == pygame.KEYDOWN:
            if not self._done_typing:
                # 按任意键跳过打字机
                self._char_index  = float(len(self._full_text))
                self.text         = self._full_text
                self._done_typing = True
                return

            if self.choices:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_index = (self.selected_index - 1) % len(self.choices)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_index = (self.selected_index + 1) % len(self.choices)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                    self.confirmed = True
            else:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                    self.confirmed = True

    # ── 渲染 ─────────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        if not self.active:
            return

        # 背景
        overlay = pygame.Surface((self.box_rect.w, self.box_rect.h), pygame.SRCALPHA)
        overlay.fill((20, 20, 34, 210))
        pygame.draw.rect(overlay, (100, 100, 140, 180),
                         (0, 0, self.box_rect.w, self.box_rect.h),
                         width=2, border_radius=self.RADIUS)
        screen.blit(overlay, self.box_rect.topleft)

        # 反馈覆盖层
        if self.feedback:
            fc = self.cfg.COLOR_CORRECT if self.feedback == "correct" else self.cfg.COLOR_WRONG
            fb_surf = pygame.Surface((self.box_rect.w, self.box_rect.h), pygame.SRCALPHA)
            fb_surf.fill((*fc, 60))
            screen.blit(fb_surf, self.box_rect.topleft)
            msg = "[正确]" if self.feedback == "correct" else "[错误] 再试一次"
            fs  = self.font.render(msg, True, fc)
            screen.blit(fs, (self.box_rect.centerx - fs.get_width() // 2,
                             self.box_rect.centery - fs.get_height() // 2))
            return

        x0 = self.box_rect.x + self.PAD
        y0 = self.box_rect.y + self.PAD

        # 正文
        self._blit_wrapped(screen, self.text, self.font,
                           self.cfg.COLOR_TEXT, x0, y0,
                           self.box_rect.w - self.PAD * 2)

        # 选项
        if self.choices and self._done_typing:
            cy = self.box_rect.y + self.box_rect.h - self.PAD - len(self.choices) * 28
            for i, ch in enumerate(self.choices):
                selected = (i == self.selected_index)
                color = self.cfg.COLOR_GOLD if selected else self.cfg.COLOR_TEXT
                prefix = ">> " if selected else "   "
                s = self.small_font.render(prefix + ch, True, color)
                screen.blit(s, (x0 + 10, cy + i * 28))
        elif not self.choices and self._done_typing:
            hint = self.small_font.render("[ E / Space / Enter ] 继续", True, (120, 120, 160))
            screen.blit(hint, (self.box_rect.right - hint.get_width() - self.PAD,
                               self.box_rect.bottom - hint.get_height() - 8))

    # ── 工具 ─────────────────────────────────────────────────────────────
    @staticmethod
    def _blit_wrapped(surface: pygame.Surface, text: str,
                      font: pygame.font.Font, color: tuple,
                      x: int, y: int, max_w: int) -> None:
        words = text.split(" ")
        line  = ""
        dy    = 0
        for word in words:
            test = line + word + " "
            if font.size(test)[0] > max_w and line:
                surface.blit(font.render(line.rstrip(), True, color), (x, y + dy))
                dy  += font.get_linesize()
                line = word + " "
            else:
                line = test
        if line:
            surface.blit(font.render(line.rstrip(), True, color), (x, y + dy))
