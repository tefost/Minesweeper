"""
ui/color_picker.py
Вибір кольору — аналог ColorDialog у C# (Windows Forms).
"""

import pygame
from ui.dialog import Dialog
from ui.helpers import draw_text, draw_button
from ui.constants import TEXT_COLOR, CELL_BORDER, FONT_SM
from core.settings import COLOR_MAP


class ColorPickerDialog(Dialog):
    """Простий picker з фіксованою палітрою кольорів."""

    _COLS = 4
    _CW   = 64
    _CH   = 38
    _PAD  = 8

    def __init__(self, screen: pygame.Surface, current: tuple[int, int, int]):
        self._options = list(COLOR_MAP.items())
        rows  = -(-len(self._options) // self._COLS)
        width = self._COLS * (self._CW + self._PAD) - self._PAD + 36
        height = 46 + rows * (self._CH + self._PAD) + 54
        super().__init__(screen, width, height, "Оберіть колір")
        self.current = current

    def _cells(self):
        ox = (self.width - (self._COLS * (self._CW + self._PAD) - self._PAD)) // 2
        cells = []
        for i, (name, color) in enumerate(self._options):
            cx = ox + (i % self._COLS) * (self._CW + self._PAD)
            cy = 46 + (i // self._COLS) * (self._CH + self._PAD)
            cells.append((name, color, pygame.Rect(cx, cy, self._CW, self._CH)))
        return cells

    def draw_content(self):
        mx, my = self._local_mouse()
        for name, color, rect in self._cells():
            is_current = color == self.current
            pygame.draw.rect(self.surface, color, rect, border_radius=5)
            border = (0, 0, 0) if rect.collidepoint(mx, my) or is_current else CELL_BORDER
            width  = 3 if is_current else (2 if rect.collidepoint(mx, my) else 1)
            pygame.draw.rect(self.surface, border, rect, width, border_radius=5)
            # Назва кольору (білий або чорний залежно від яскравості)
            brightness = sum(color)
            lc = (0, 0, 0) if brightness > 380 else (255, 255, 255)
            draw_text(self.surface, name, FONT_SM, lc,
                      rect.centerx, rect.centery, center=True)

        cancel_r = pygame.Rect(self.width // 2 - 60, self.height - 46, 120, 34)
        draw_button(self.surface, "Скасувати", FONT_SM, cancel_r,
                    hover=cancel_r.collidepoint(mx, my))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = self._local_mouse()
            for _, color, rect in self._cells():
                if rect.collidepoint(mx, my):
                    self.result  = color
                    self.running = False
                    return
            cancel_r = pygame.Rect(self.width // 2 - 60, self.height - 46, 120, 34)
            if cancel_r.collidepoint(mx, my):
                self.running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False
