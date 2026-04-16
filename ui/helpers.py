"""
ui/helpers.py
Допоміжні функції малювання — draw_text, draw_button.
"""

import pygame
from ui.constants import TEXT_COLOR, BTN_COLOR, BTN_HOVER, BTN_ACTIVE, CELL_BORDER


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple,
    x: int,
    y: int,
    *,
    center: bool = False,
    right: bool = False,
    top: bool = False,
) -> pygame.Rect:
    """
    Малює текст на поверхні.
    center=True  → x,y — центр
    right=True   → x — права межа, y — вертикальний центр
    top=True     → y — верхній край (інакше вертикально центрований відносно y)
    """
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.centerx, rect.centery = x, y
    elif right:
        rect.right, rect.centery = x, y
    elif top:
        rect.x, rect.y = x, y
    else:
        rect.x = x
        rect.y = y - rect.height // 2
    surface.blit(surf, rect)
    return rect


def draw_button(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    rect: pygame.Rect,
    *,
    hover: bool = False,
    active: bool = False,
    bg: tuple | None = None,
    text_color: tuple = TEXT_COLOR,
) -> None:
    """Малює кнопку з заокругленими кутами та підсвіткою при наведенні."""
    if bg:
        color = bg
    elif active:
        color = BTN_ACTIVE
    elif hover:
        color = BTN_HOVER
    else:
        color = BTN_COLOR

    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, CELL_BORDER, rect, 1, border_radius=5)
    ts = font.render(text, True, text_color)
    surface.blit(ts, ts.get_rect(center=rect.center))
