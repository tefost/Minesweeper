"""
ui/constants.py
Всі константи вигляду, розміри, кольори та шрифти.
Аналог enum / static constants у C# проекті.
"""

import pygame

pygame.init()
pygame.font.init()

# ── Розміри ──────────────────────────────────────────────────────────────────

CELL_SIZE  = 46       # розмір клітинки у пікселях
MENU_H     = 30       # висота рядка меню
STATUS_H   = 52       # висота статус-бару (міни + час)
MIN_WIN_W  = 520      # мінімальна ширина вікна

# ── Палітра ───────────────────────────────────────────────────────────────────

BG_COLOR      = (235, 235, 235)
MENU_BG       = (225, 225, 225)
MENU_HOVER    = (200, 210, 250)
MENU_BORDER   = (170, 170, 170)
TEXT_COLOR    = ( 20,  20,  20)
BTN_COLOR     = (205, 205, 205)
BTN_HOVER     = (185, 195, 235)
BTN_ACTIVE    = (160, 170, 215)
DIALOG_BG     = (248, 248, 248)
DIALOG_BORDER = ( 80,  80,  80)
DIALOG_TITLE  = ( 70, 105, 170)
INPUT_BG      = (255, 255, 255)
INPUT_BORDER  = ( 80, 105, 195)
INPUT_ACTIVE  = ( 50,  80, 200)
CELL_BORDER   = (120, 120, 120)
STATUS_BG     = (215, 215, 215)
STATUS_LINE   = (170, 170, 170)
ROW_ODD       = (230, 245, 230)
ROW_EVEN      = DIALOG_BG

# Кольори цифр на розкритих клітинках
NUMBER_COLORS: dict[int, tuple[int, int, int]] = {
    1: (  0,   0, 200),
    2: (  0, 130,   0),
    3: (200,   0,   0),
    4: (  0,   0, 120),
    5: (130,   0,   0),
    6: (  0, 120, 120),
    7: ( 20,  20,  20),
    8: (110, 110, 110),
}


# ── Шрифти ───────────────────────────────────────────────────────────────────

def _make_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Підбирає перший доступний системний шрифт із підтримкою кирилиці."""
    candidates = ["Segoe UI", "Arial", "DejaVu Sans", "FreeSans",
                  "Liberation Sans", "Ubuntu", "Noto Sans"]
    for name in candidates:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            # Перевіряємо відображення кирилиці
            f.render("АаБбВв", True, (0, 0, 0))
            return f
        except Exception:
            pass
    return pygame.font.Font(None, size + 4)


FONT_SM   = _make_font(14)
FONT_MD   = _make_font(16)
FONT_BOLD = _make_font(17, bold=True)
FONT_MENU = _make_font(15)
FONT_NUM  = _make_font(18, bold=True)
FONT_BIG  = _make_font(19, bold=True)
