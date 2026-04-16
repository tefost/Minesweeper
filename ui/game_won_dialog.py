"""
ui/game_won_dialog.py
Аналог GameWonForm.cs — діалог перемоги з введенням імені.
"""

import pygame
from ui.dialog import Dialog
from ui.helpers import draw_text, draw_button
from ui.constants import TEXT_COLOR, INPUT_BG, INPUT_BORDER, FONT_MD, FONT_BOLD


class GameWonDialog(Dialog):
    """
    Показує час гри та пропонує ввести ім'я для таблиці рекордів.
    result: ('ok', player_name) | ('cancel', None)
    """

    def __init__(self, screen: pygame.Surface, time_elapsed: int):
        super().__init__(screen, 420, 230, "Перемога!")
        self.time_elapsed = time_elapsed
        self.player_name  = ""
        self._cursor_tick = 0

    def draw_content(self):
        self._cursor_tick = (self._cursor_tick + 1) % 60
        mx, my = self._local_mouse()

        msg = f"Вітаємо! Ви виграли за {self.time_elapsed} сек.!"
        draw_text(self.surface, msg, FONT_BOLD, (40, 130, 40),
                  self.width // 2, 58, center=True)
        draw_text(self.surface, "Введіть ваше ім'я для таблиці рекордів:",
                  FONT_MD, TEXT_COLOR, self.width // 2, 90, center=True)

        # Input field
        inp = pygame.Rect(40, 108, self.width - 80, 34)
        pygame.draw.rect(self.surface, INPUT_BG, inp, border_radius=5)
        pygame.draw.rect(self.surface, INPUT_BORDER, inp, 2, border_radius=5)
        draw_text(self.surface, self.player_name, FONT_MD, TEXT_COLOR,
                  inp.x + 8, inp.centery, center=False)
        # Text cursor
        if self._cursor_tick < 30:
            cx = inp.x + 8 + FONT_MD.size(self.player_name)[0]
            pygame.draw.line(self.surface, TEXT_COLOR,
                             (cx, inp.y + 5), (cx, inp.bottom - 5), 2)

        # Buttons
        ok_r  = pygame.Rect(self.width // 2 - 130, 162, 115, 38)
        can_r = pygame.Rect(self.width // 2 +  15, 162, 115, 38)
        draw_button(self.surface, "OK",         FONT_MD, ok_r,  hover=ok_r.collidepoint(mx, my))
        draw_button(self.surface, "Скасувати",  FONT_MD, can_r, hover=can_r.collidepoint(mx, my))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = self._local_mouse()
            ok_r  = pygame.Rect(self.width // 2 - 130, 162, 115, 38)
            can_r = pygame.Rect(self.width // 2 +  15, 162, 115, 38)
            if ok_r.collidepoint(mx, my):
                self.result  = ("ok", self.player_name or "Анонім")
                self.running = False
            elif can_r.collidepoint(mx, my):
                self.result  = ("cancel", None)
                self.running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.result  = ("ok", self.player_name or "Анонім")
                self.running = False
            elif event.key == pygame.K_ESCAPE:
                self.result  = ("cancel", None)
                self.running = False
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.unicode.isprintable() and len(self.player_name) < 40:
                self.player_name += event.unicode
