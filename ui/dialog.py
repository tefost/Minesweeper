"""
ui/dialog.py
Базовий клас модального діалогу — аналог Form.ShowDialog() у C#.
"""

import pygame
import sys
from ui.constants import (
    DIALOG_BG, DIALOG_BORDER, DIALOG_TITLE, FONT_MD
)


class Dialog:
    """
    Базовий модальний діалог (аналог Form із ShowDialog()).

    Підкласи повинні перевизначити:
        draw_content(self)       — малювання вмісту поверх шапки
        handle_event(self, event) — обробка подій
    """

    def __init__(
        self,
        screen: pygame.Surface,
        width: int,
        height: int,
        title: str,
    ):
        self.screen  = screen
        self.width   = width
        self.height  = height
        self.title   = title
        self.result  = None
        self.running = True

        sw, sh = screen.get_size()
        self.x = max(0, (sw - width)  // 2)
        self.y = max(0, (sh - height) // 2)

        # Власна поверхня діалогу
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # ── Внутрішня шапка (title bar) ──────────────────────────────────────────

    def _draw_chrome(self):
        """Малює фон діалогу та смугу заголовку."""
        self.surface.fill(DIALOG_BG)
        pygame.draw.rect(self.surface, DIALOG_BORDER,
                         (0, 0, self.width, self.height), 2, border_radius=7)
        # Title bar
        pygame.draw.rect(self.surface, DIALOG_TITLE,
                         (1, 1, self.width - 2, 34), border_radius=7)
        pygame.draw.rect(self.surface, DIALOG_TITLE,
                         (1, 18, self.width - 2, 18))
        ts = FONT_MD.render(self.title, True, (255, 255, 255))
        self.surface.blit(ts, (12, 9))

    # ── Головний цикл діалогу (ShowDialog()) ─────────────────────────────────

    def run(self):
        """
        Запускає модальний цикл (аналог form.ShowDialog()).
        Повертає self.result після закриття.
        """
        clock   = pygame.time.Clock()
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        bg_snap = self.screen.copy()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_event(event)

            self.screen.blit(bg_snap, (0, 0))
            self.screen.blit(overlay, (0, 0))

            self._draw_chrome()
            self.draw_content()
            self.screen.blit(self.surface, (self.x, self.y))

            pygame.display.flip()
            clock.tick(60)

        return self.result

    # ── Абстрактні методи ────────────────────────────────────────────────────

    def draw_content(self):
        """Перевизначте у підкласі."""

    def handle_event(self, event: pygame.event.Event):
        """Перевизначте у підкласі."""

    # ── Допоміжні координати ─────────────────────────────────────────────────

    def _local_mouse(self) -> tuple[int, int]:
        """Повертає позицію миші відносно поверхні діалогу."""
        mx, my = pygame.mouse.get_pos()
        return mx - self.x, my - self.y
