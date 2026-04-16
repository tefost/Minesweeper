"""
ui/menu_bar.py
Аналог MenuStrip у C# (Windows Forms) — рядок меню з випадаючими пунктами.
"""

import pygame
from ui.constants import (
    MENU_H, MENU_BG, MENU_HOVER, MENU_BORDER, TEXT_COLOR, FONT_MENU
)


class MenuBar:
    """
    Горизонтальне меню з одним рівнем вкладеності (як MenuStrip у C#).

    Структура:
        ITEMS = [
            ("Заголовок", ["Пункт 1", "---", "Пункт 2"]),
            ...
        ]
    "---" = роздільник (ToolStripSeparator у C#).
    """

    ITEMS: list[tuple[str, list[str]]] = [
        ("Гра", [
            "Нова гра",
            "---",
            "Зберегти гру",
            "Завантажити гру",
            "---",
            "Таблиця рекордів",
            "---",
            "Налаштування",
            "---",
            "Вихід",
        ]),
    ]

    def __init__(self):
        self.open_menu: int | None = None

    # ── Малювання ────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, mx: int, my: int):
        """Малює рядок меню та, якщо відкрито, dropdown."""
        # Фон рядка
        surface.fill(MENU_BG, (0, 0, surface.get_width(), MENU_H))
        pygame.draw.line(surface, MENU_BORDER,
                         (0, MENU_H - 1), (surface.get_width(), MENU_H - 1))

        x = 4
        for i, (label, _) in enumerate(self.ITEMS):
            w    = FONT_MENU.size(label)[0] + 20
            rect = pygame.Rect(x, 2, w, MENU_H - 4)
            if rect.collidepoint(mx, my) or self.open_menu == i:
                pygame.draw.rect(surface, MENU_HOVER, rect, border_radius=3)
            surface.blit(FONT_MENU.render(label, True, TEXT_COLOR), (x + 10, 7))
            x += w + 2

        # Dropdown
        if self.open_menu is not None:
            self._draw_dropdown(surface, mx, my)

    def _dropdown_rect(self, index: int) -> tuple[int, list[str], int, int]:
        """Повертає (sx, items, max_w, sub_h) для підменю з індексом index."""
        _, items = self.ITEMS[index]
        sx = 4
        for k in range(index):
            sx += FONT_MENU.size(self.ITEMS[k][0])[0] + 20 + 2
        max_w = max(
            (FONT_MENU.size(it)[0] for it in items if it != "---"),
            default=80) + 30
        sub_h = sum(24 if it != "---" else 10 for it in items) + 8
        return sx, items, max_w, sub_h

    def _draw_dropdown(self, surface: pygame.Surface, mx: int, my: int):
        sx, items, max_w, sub_h = self._dropdown_rect(self.open_menu)
        bg_r = pygame.Rect(sx, MENU_H, max_w, sub_h)
        pygame.draw.rect(surface, MENU_BG, bg_r)
        pygame.draw.rect(surface, MENU_BORDER, bg_r, 1)

        y = MENU_H + 4
        for item in items:
            if item == "---":
                pygame.draw.line(surface, MENU_BORDER,
                                 (sx + 6, y + 4), (sx + max_w - 6, y + 4))
                y += 10
            else:
                ir = pygame.Rect(sx + 2, y, max_w - 4, 24)
                if ir.collidepoint(mx, my):
                    pygame.draw.rect(surface, MENU_HOVER, ir, border_radius=3)
                surface.blit(FONT_MENU.render(item, True, TEXT_COLOR), (sx + 12, y + 4))
                y += 24

    # ── Клік ─────────────────────────────────────────────────────────────────

    def click(self, mx: int, my: int) -> str | None:
        """
        Обробляє клік. Повертає назву вибраного пункту або None.
        Аналог ToolStripMenuItem.Click.
        """
        # Клік на заголовок меню
        x = 4
        for i, (label, _) in enumerate(self.ITEMS):
            w    = FONT_MENU.size(label)[0] + 20
            rect = pygame.Rect(x, 2, w, MENU_H - 4)
            if rect.collidepoint(mx, my):
                self.open_menu = i if self.open_menu != i else None
                return None
            x += w + 2

        # Клік у dropdown
        if self.open_menu is not None:
            sx, items, max_w, sub_h = self._dropdown_rect(self.open_menu)
            y = MENU_H + 4
            for item in items:
                if item == "---":
                    y += 10
                else:
                    ir = pygame.Rect(sx + 2, y, max_w - 4, 24)
                    if ir.collidepoint(mx, my):
                        self.open_menu = None
                        return item
                    y += 24
            self.open_menu = None   # клік поза підменю — закрити

        return None

    def covers(self, mx: int, my: int) -> bool:
        """Перевіряє, чи знаходиться точка під меню/dropdown (не передавати кліки на поле)."""
        if my < MENU_H:
            return True
        if self.open_menu is not None:
            sx, items, max_w, sub_h = self._dropdown_rect(self.open_menu)
            if pygame.Rect(sx, MENU_H, max_w, sub_h).collidepoint(mx, my):
                return True
        return False
