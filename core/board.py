"""
core/board.py
Відповідає Board.cs та Square (вкладений клас) з оригінального C# проекту.
Вся логіка методів збережена без змін — тільки синтаксис.
"""

import random
from enum import Enum


class BoardState(Enum):
    IN_PROGRESS = "InProgress"
    WON         = "Won"
    LOST        = "Lost"


class Square:
    """Одна клітинка поля (аналог класу Square у C#)."""

    def __init__(self):
        self.is_mine:       bool = False
        self.is_revealed:   bool = False
        self.is_flagged:    bool = False
        self.adjacent_mines: int = 0


class Board:
    """
    Ігрова логіка поля (аналог Board.cs).

    Events (замість C# EventHandler):
        on_square_revealed : list[Callable[[int, int, int], None]]
        on_square_flagged  : list[Callable[[int, int], None]]
        on_game_lost       : list[Callable[[], None]]
        on_game_won        : list[Callable[[], None]]
    """

    def __init__(self, rows: int, columns: int, mines: int):
        self.rows    = rows
        self.columns = columns
        self.mines   = mines
        self.state   = BoardState.IN_PROGRESS

        # Squares[row][col] — аналог Square[,] у C#
        self.squares: list[list[Square]] = []

        # Events
        self.on_square_revealed: list = []
        self.on_square_flagged:  list = []
        self.on_game_lost:       list = []
        self.on_game_won:        list = []

        self._initialize_board()
        self._place_mines()
        self._count_adjacent_mines()

    # ── private void InitializeBoard() ──────────────────────────────────────

    def _initialize_board(self):
        self.squares = [[Square() for _ in range(self.columns)]
                        for _ in range(self.rows)]

    # ── private void PlaceMines() ───────────────────────────────────────────

    def _place_mines(self):
        mines_placed = 0
        while mines_placed < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.columns - 1)
            if not self.squares[row][col].is_mine:
                self.squares[row][col].is_mine = True
                mines_placed += 1

    # ── private void CountAdjacentMines() ───────────────────────────────────

    def _count_adjacent_mines(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if not self.squares[i][j].is_mine:
                    adj = self._get_adjacent_squares(i, j)
                    self.squares[i][j].adjacent_mines = sum(
                        1 for s in adj if s.is_mine)

    # ── private IEnumerable<Square> GetAdjacentSquares(int row, int col) ────

    def _get_adjacent_squares(self, row: int, col: int) -> list[Square]:
        result = []
        for i in range(max(0, row - 1), min(self.rows - 1, row + 1) + 1):
            for j in range(max(0, col - 1), min(self.columns - 1, col + 1) + 1):
                if i != row or j != col:
                    result.append(self.squares[i][j])
        return result

    # ── public void RevealSquare(int row, int col) ───────────────────────────

    def reveal_square(self, row: int, col: int):
        if self.state != BoardState.IN_PROGRESS:
            return
        square = self.squares[row][col]
        if square.is_revealed or square.is_flagged:
            return

        self.squares[row][col].is_revealed = True
        for cb in self.on_square_revealed:
            cb(row, col, self.squares[row][col].adjacent_mines)

        if self.squares[row][col].is_mine:
            self.state = BoardState.LOST
            for cb in self.on_game_lost:
                cb()
            return

        if self.squares[row][col].adjacent_mines == 0:
            self._reveal_empty_squares(row, col)

        self._check_for_win()

    # ── private void RevealEmptySquares(int row, int col) ───────────────────

    def _reveal_empty_squares(self, row: int, col: int):
        for i in range(max(0, row - 1), min(self.rows - 1, row + 1) + 1):
            for j in range(max(0, col - 1), min(self.columns - 1, col + 1) + 1):
                sq = self.squares[i][j]
                if not sq.is_revealed and not sq.is_flagged:
                    self.reveal_square(i, j)

    # ── public void FlagSquare(int row, int col) ─────────────────────────────

    def flag_square(self, row: int, col: int):
        if self.state != BoardState.IN_PROGRESS:
            return
        if self.squares[row][col].is_revealed:
            return
        self.squares[row][col].is_flagged = not self.squares[row][col].is_flagged
        for cb in self.on_square_flagged:
            cb(row, col)

    # ── private void CheckForWin() ───────────────────────────────────────────

    def _check_for_win(self):
        if self.state != BoardState.IN_PROGRESS:
            return
        revealed = sum(
            1 for i in range(self.rows)
            for j in range(self.columns)
            if self.squares[i][j].is_revealed)
        if revealed == (self.rows * self.columns) - self.mines:
            self.state = BoardState.WON
            for cb in self.on_game_won:
                cb()

    # ── public int GetRemainingMines() ──────────────────────────────────────

    def get_remaining_mines(self) -> int:
        flagged = sum(
            1 for i in range(self.rows)
            for j in range(self.columns)
            if self.squares[i][j].is_flagged)
        return self.mines - flagged
