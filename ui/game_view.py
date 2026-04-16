"""
ui/game_view.py
Малювання ігрового поля та статус-бару.
Реалізує IMainView з C# (ShowBoard, ShowRevealed, ShowFlag тощо).
"""

import os
import pygame
from ui.constants import (
    CELL_SIZE, MENU_H, STATUS_H, MIN_WIN_W,
    BG_COLOR, STATUS_BG, STATUS_LINE, TEXT_COLOR,
    NUMBER_COLORS, FONT_BOLD, FONT_NUM,
)
from ui.helpers import draw_text
from core.settings import Settings


CellState = int | str   # int = кількість мін | 'unrevealed'|'revealed'|'mine'|'flag'


class GameView:
    """
    Відповідає IMainView + малювання (MainForm у C#).
    Зберігає cell_states і малює поле на екрані.
    """

    def __init__(self, screen: pygame.Surface, sett: Settings):
        self.screen        = screen
        self.sett          = sett
        self.rows:    int  = sett.rows
        self.columns: int  = sett.columns
        self.cell_states:  dict[tuple[int, int], CellState] = {}
        self._mine_img:    pygame.Surface | None = None
        self._flag_img:    pygame.Surface | None = None
        self.reload_images()

    # ── IMainView: ShowBoard() ────────────────────────────────────────────────

    def show_board(self, rows: int, columns: int):
        self.rows    = rows
        self.columns = columns
        self.cell_states = {(i, j): "unrevealed"
                            for i in range(rows)
                            for j in range(columns)}

    # ── IMainView: ShowRevealed() ─────────────────────────────────────────────

    def show_revealed(self, row: int, col: int, adjacent_mines: int):
        self.cell_states[(row, col)] = adjacent_mines if adjacent_mines > 0 else "revealed"

    # ── IMainView: ShowUnrevealed() ───────────────────────────────────────────

    def show_unrevealed(self, row: int, col: int):
        self.cell_states[(row, col)] = "unrevealed"

    # ── IMainView: ShowMine() ─────────────────────────────────────────────────

    def show_mine(self, row: int, col: int):
        self.cell_states[(row, col)] = "mine"

    # ── IMainView: ShowFlag() ─────────────────────────────────────────────────

    def show_flag(self, row: int, col: int, flagged: bool):
        self.cell_states[(row, col)] = "flag" if flagged else "unrevealed"

    # ── Зображення ────────────────────────────────────────────────────────────

    def reload_images(self):
        sz = CELL_SIZE - 6
        self._mine_img = self._load_img(self.sett.mine_image_path, sz)
        self._flag_img = self._load_img(self.sett.flag_image_path, sz)

    @staticmethod
    def _load_img(path: str, size: int) -> pygame.Surface | None:
        if path and os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, (size, size))
            except Exception:
                pass
        return None

    # ── Розмір вікна ──────────────────────────────────────────────────────────

    def window_size(self) -> tuple[int, int]:
        w = max(self.columns * CELL_SIZE + 2, MIN_WIN_W)
        h = MENU_H + STATUS_H + self.rows * CELL_SIZE + 2
        return w, h

    def get_cell_at(self, mx: int, my: int) -> tuple[int | None, int | None]:
        """Конвертує піксельні координати в (row, col) або (None, None)."""
        col = (mx) // CELL_SIZE
        row = (my - MENU_H - STATUS_H) // CELL_SIZE
        if 0 <= row < self.rows and 0 <= col < self.columns:
            return row, col
        return None, None

    # ── Малювання ────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface, elapsed_sec: int,
             remaining_mines: int, game_over: bool, won: bool):
        screen.fill(BG_COLOR)
        self._draw_board(screen)
        self._draw_status(screen, elapsed_sec, remaining_mines, game_over, won)

    def _draw_board(self, screen: pygame.Surface):
        for i in range(self.rows):
            for j in range(self.columns):
                self._draw_cell(screen, i, j)

    def _draw_cell(self, screen: pygame.Surface, i: int, j: int):
        x = j * CELL_SIZE
        y = MENU_H + STATUS_H + i * CELL_SIZE
        r = pygame.Rect(x, y, CELL_SIZE - 1, CELL_SIZE - 1)
        state = self.cell_states.get((i, j), "unrevealed")
        cs    = CELL_SIZE

        if state == "unrevealed":
            pygame.draw.rect(screen, self.sett.unrevealed_color, r, border_radius=2)
            # 3-D ефект (raised)
            pygame.draw.lines(screen, (255, 255, 255), False,
                              [(x, y + cs - 2), (x, y), (x + cs - 2, y)])
            pygame.draw.lines(screen, (80, 80, 80), False,
                              [(x + 1, y + cs - 2), (x + cs - 2, y + cs - 2),
                               (x + cs - 2, y + 1)])

        elif state == "revealed":
            pygame.draw.rect(screen, self.sett.revealed_color, r, border_radius=2)
            pygame.draw.rect(screen, (170, 170, 170), r, 1, border_radius=2)

        elif state == "mine":
            # Підсвічуємо червоним якщо підірвались на цій міні
            bg = (255, 60, 60) if self.sett.mine_color == (220, 50, 50) else self.sett.mine_color
            pygame.draw.rect(screen, bg, r, border_radius=2)
            self._draw_mine_icon(screen, x, y)

        elif state == "flag":
            pygame.draw.rect(screen, self.sett.unrevealed_color, r, border_radius=2)
            pygame.draw.lines(screen, (255, 255, 255), False,
                              [(x, y + cs - 2), (x, y), (x + cs - 2, y)])
            pygame.draw.lines(screen, (80, 80, 80), False,
                              [(x + 1, y + cs - 2), (x + cs - 2, y + cs - 2),
                               (x + cs - 2, y + 1)])
            self._draw_flag_icon(screen, x, y)

        elif isinstance(state, int):
            pygame.draw.rect(screen, self.sett.revealed_color, r, border_radius=2)
            pygame.draw.rect(screen, (170, 170, 170), r, 1, border_radius=2)
            col = NUMBER_COLORS.get(state, (10, 10, 10))
            draw_text(screen, str(state), FONT_NUM, col,
                      x + cs // 2 - 1, y + cs // 2, center=True)

    def _draw_mine_icon(self, screen: pygame.Surface, x: int, y: int):
        cs = CELL_SIZE
        if self._mine_img:
            screen.blit(self._mine_img, (x + 3, y + 3))
            return
        cx, cy = x + cs // 2 - 1, y + cs // 2
        ra     = cs // 5
        # Промені
        for dx, dy in [(ra+4,0),(-ra-4,0),(0,ra+4),(0,-ra-4),
                       (ra+3,ra+3),(-ra-3,-ra-3),(ra+3,-ra-3),(-ra-3,ra+3)]:
            pygame.draw.line(screen, (20, 20, 20),
                             (cx, cy), (cx + dx//2, cy + dy//2), 2)
        pygame.draw.circle(screen, (20, 20, 20),  (cx, cy), ra)
        pygame.draw.circle(screen, (230, 230, 230), (cx - ra//3, cy - ra//3), max(1, ra//3))

    def _draw_flag_icon(self, screen: pygame.Surface, x: int, y: int):
        cs = CELL_SIZE
        if self._flag_img:
            screen.blit(self._flag_img, (x + 3, y + 3))
            return
        fx     = x + cs // 2
        fy     = y + cs // 2
        top    = fy - cs // 3
        bottom = fy + cs // 3
        pygame.draw.line(screen, (40, 40, 40), (fx, top), (fx, bottom), 2)
        flag_pts = [
            (fx, top),
            (fx + cs // 3, top + (bottom - top) // 4),
            (fx, top + (bottom - top) // 2),
        ]
        pygame.draw.polygon(screen, self.sett.flag_color, flag_pts)

    def _draw_status(self, screen: pygame.Surface, elapsed_sec: int,
                     remaining_mines: int, game_over: bool, won: bool):
        sw = screen.get_width()
        pygame.draw.rect(screen, STATUS_BG, (0, MENU_H, sw, STATUS_H))
        pygame.draw.line(screen, STATUS_LINE,
                         (0, MENU_H + STATUS_H - 1), (sw, MENU_H + STATUS_H - 1))

        # Кількість мін зліва
        draw_text(screen, f"{remaining_mines}", FONT_BOLD, (180, 30, 30),
                  18, MENU_H + STATUS_H // 2, center=False)

        # Час справа
        draw_text(screen, f"{elapsed_sec} сек", FONT_BOLD, (30, 30, 170),
                  sw - 18, MENU_H + STATUS_H // 2, right=True)

        # Статус по центру
        if game_over:
            txt = "Перемога!  (F2 — нова гра)" if won else "Програш!  (F2 — нова гра)"
            col = (0, 140, 0) if won else (190, 0, 0)
            draw_text(screen, txt, FONT_BOLD, col,
                      sw // 2, MENU_H + STATUS_H // 2, center=True)
        else:
            draw_text(screen, "F2 — нова гра  |  ПКМ — прапор",
                      FONT_BOLD, (100, 100, 100),
                      sw // 2, MENU_H + STATUS_H // 2, center=True)
