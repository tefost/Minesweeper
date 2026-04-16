"""
ui/highscores_dialog.py
Аналог HighscoresForm.cs — таблиця рекордів (топ-10).
"""

import pygame
from ui.dialog import Dialog
from ui.helpers import draw_text, draw_button
from ui.constants import (
    TEXT_COLOR, MENU_BORDER, FONT_SM, FONT_MD, FONT_BOLD,
    ROW_ODD, ROW_EVEN, DIALOG_BG
)
from core.highscores import HighscoreEntry


class HighscoresDialog(Dialog):
    """
    Показує відсортовану таблицю рекордів (топ-10 за часом).
    Аналог HighscoresForm + form.AddHighscoreToView().
    """

    # Ширини стовпців: #, Ім'я, Час, Дата
    _COL_X     = [18, 52, 310, 400]
    _COL_HEADS = ["#", "Ім'я гравця", "Час (сек)", "Дата"]

    def __init__(self, screen: pygame.Surface, highscores: list[HighscoreEntry]):
        # Сортуємо за часом (найшвидші перші) і беремо топ-10
        # — аналог highscores.OrderBy(h => h.Time).Take(10) у MainPresenter
        entries = sorted(highscores, key=lambda h: h.time)[:10]
        super().__init__(screen, 600, 430, "Таблиця рекордів")
        self.entries = entries

    def draw_content(self):
        mx, my = self._local_mouse()

        # ── Заголовки таблиці ────────────────────────────────────────────────
        y_head = 44
        for head, cx in zip(self._COL_HEADS, self._COL_X):
            draw_text(self.surface, head, FONT_BOLD, TEXT_COLOR, cx, y_head, top=True)
        pygame.draw.line(self.surface, MENU_BORDER,
                         (12, y_head + 22), (self.width - 12, y_head + 22), 2)

        # ── Рядки ────────────────────────────────────────────────────────────
        if not self.entries:
            draw_text(self.surface, "Ще немає рекордів — виграйте першу гру!",
                      FONT_MD, (140, 140, 140),
                      self.width // 2, 240, center=True)
        else:
            for i, entry in enumerate(self.entries):
                row_y = y_head + 28 + i * 30
                row_bg = ROW_ODD if i % 2 == 0 else ROW_EVEN
                pygame.draw.rect(self.surface, row_bg,
                                 (12, row_y - 2, self.width - 24, 28),
                                 border_radius=3)

                # Медальки для топ-3
                medal_map = {0: " ", 1: " ", 2: " "}
                num_label = medal_map.get(i, str(i + 1))

                cols_data = [
                    (num_label,                            self._COL_X[0]),
                    (entry.name[:28],                      self._COL_X[1]),
                    (str(entry.time),                      self._COL_X[2]),
                    (entry.date.strftime("%d.%m.%y %H:%M"), self._COL_X[3]),
                ]
                for text, cx in cols_data:
                    draw_text(self.surface, text, FONT_MD, TEXT_COLOR,
                              cx, row_y + 12, center=False)

        # ── Кнопка Закрити ───────────────────────────────────────────────────
        close_r = pygame.Rect(self.width // 2 - 65, self.height - 54, 130, 38)
        draw_button(self.surface, "Закрити", FONT_MD, close_r,
                    hover=close_r.collidepoint(mx, my))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = self._local_mouse()
            close_r = pygame.Rect(self.width // 2 - 65, self.height - 54, 130, 38)
            if close_r.collidepoint(mx, my):
                self.running = False
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.running = False
