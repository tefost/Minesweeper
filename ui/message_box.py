"""
ui/message_box.py
Аналог MessageBox.Show() у C# (Windows Forms).
"""

import pygame
from ui.dialog import Dialog
from ui.helpers import draw_text, draw_button
from ui.constants import TEXT_COLOR, FONT_MD


class MessageBox(Dialog):
    """
    MessageBox.Show(text, caption, buttons) → вибрана кнопка (str).
    """

    def __init__(
        self,
        screen: pygame.Surface,
        message: str,
        title: str = "Повідомлення",
        buttons: tuple[str, ...] = ("OK",),
    ):
        lines  = message.split("\n")
        max_tw = max(FONT_MD.size(line)[0] for line in lines)
        width  = max(360, max_tw + 80)
        height = 50 + len(lines) * 28 + 70

        super().__init__(screen, width, height, title)
        self.lines   = lines
        self.buttons = list(buttons)

    # ── Кнопки ───────────────────────────────────────────────────────────────

    def _btn_rects(self) -> list[pygame.Rect]:
        bw     = 120
        gap    = 14
        total  = len(self.buttons) * bw + (len(self.buttons) - 1) * gap
        start  = (self.width - total) // 2
        y      = self.height - 54
        return [pygame.Rect(start + i * (bw + gap), y, bw, 36)
                for i in range(len(self.buttons))]

    # ── draw_content ─────────────────────────────────────────────────────────

    def draw_content(self):
        mx, my = self._local_mouse()
        for i, line in enumerate(self.lines):
            draw_text(self.surface, line, FONT_MD, TEXT_COLOR,
                      self.width // 2, 52 + i * 28, center=True)
        for btn, rect in zip(self.buttons, self._btn_rects()):
            draw_button(self.surface, btn, FONT_MD, rect,
                        hover=rect.collidepoint(mx, my))

    # ── handle_event ─────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = self._local_mouse()
            for i, rect in enumerate(self._btn_rects()):
                if rect.collidepoint(mx, my):
                    self.result  = self.buttons[i]
                    self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.result  = self.buttons[0]
                self.running = False
            elif event.key == pygame.K_ESCAPE and len(self.buttons) > 1:
                self.result  = self.buttons[-1]
                self.running = False


def show_message(
    screen: pygame.Surface,
    message: str,
    title: str = "Повідомлення",
    buttons: tuple[str, ...] = ("OK",),
) -> str:
    """Зручна обгортка — аналог static MessageBox.Show(...)."""
    return MessageBox(screen, message, title, buttons).run()
