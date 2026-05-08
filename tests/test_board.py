"""
tests/test_board.py
Unit-тести для core/board.py
Використовує: fixtures, parametrize, mocking, markers
"""

import pytest
from unittest.mock import MagicMock, patch
from core.board import Board, BoardState, Square


# ─────────────────────────── FIXTURES ───────────────────────────────────────

@pytest.fixture
def small_board():
    """3x3 дошка з 1 міною (патч random, щоб міна завжди в [0][0])."""
    with patch("core.board.random.randint", side_effect=[0, 0]):
        board = Board(rows=3, columns=3, mines=1)
    return board


@pytest.fixture
def safe_board():
    """5x5 дошка без мін — зручна для тестів відкриття."""
    with patch("core.board.random.randint", return_value=0):
        # Перший виклик кладе міну в [0][0]; далі всі клітинки вже зайняті
        # тому створимо дошку з 0 мін
        board = Board(rows=5, columns=5, mines=0)
    return board


@pytest.fixture
def board_with_callbacks():
    """Дошка 3x3 з 1 міною + заглушки для всіх подій."""
    with patch("core.board.random.randint", side_effect=[0, 0]):
        board = Board(rows=3, columns=3, mines=1)

    board.on_square_revealed = [MagicMock()]
    board.on_square_flagged  = [MagicMock()]
    board.on_game_lost       = [MagicMock()]
    board.on_game_won        = [MagicMock()]
    return board


# ─────────────────────── МАРКЕРИ ────────────────────────────────────────────

smoke    = pytest.mark.smoke
slow     = pytest.mark.slow
unit     = pytest.mark.unit


# ═══════════════════════════ Square ═════════════════════════════════════════

class TestSquare:

    @unit
    def test_default_values(self):
        sq = Square()
        assert sq.is_mine is False
        assert sq.is_revealed is False
        assert sq.is_flagged is False
        assert sq.adjacent_mines == 0


# ═══════════════════════════ Board.__init__ ══════════════════════════════════

class TestBoardInit:

    @smoke
    def test_board_dimensions(self, small_board):
        assert small_board.rows == 3
        assert small_board.columns == 3

    @unit
    def test_mine_count(self, small_board):
        mine_count = sum(
            1 for i in range(3) for j in range(3)
            if small_board.squares[i][j].is_mine
        )
        assert mine_count == 1

    @unit
    def test_initial_state_in_progress(self, small_board):
        assert small_board.state == BoardState.IN_PROGRESS

    @unit
    def test_squares_not_revealed_initially(self, small_board):
        for row in small_board.squares:
            for sq in row:
                assert sq.is_revealed is False

    @unit
    def test_adjacent_mines_counted(self, small_board):
        """Клітинки навколо [0][0] (де міна) мають adjacent_mines >= 1."""
        # [0][1] і [1][0] і [1][1] — сусіди [0][0]
        neighbors = [(0, 1), (1, 0), (1, 1)]
        for r, c in neighbors:
            assert small_board.squares[r][c].adjacent_mines == 1


# ═══════════════════════════ Board._get_adjacent_squares ════════════════════

class TestGetAdjacentSquares:

    @pytest.mark.parametrize("row,col,expected_count", [
        (0, 0, 3),   # кут → 3 сусіди
        (0, 1, 5),   # край → 5 сусідів
        (1, 1, 8),   # центр → 8 сусідів
    ])
    @unit
    def test_adjacent_count(self, small_board, row, col, expected_count):
        adj = small_board._get_adjacent_squares(row, col)
        assert len(adj) == expected_count

    @unit
    def test_center_of_larger_board(self):
        with patch("core.board.random.randint", return_value=0):
            board = Board(5, 5, 0)
        adj = board._get_adjacent_squares(2, 2)
        assert len(adj) == 8


# ═══════════════════════════ Board.reveal_square ════════════════════════════

class TestRevealSquare:

    @smoke
    def test_reveal_safe_square(self, small_board):
        """Відкриття безпечної клітинки змінює is_revealed."""
        small_board.reveal_square(0, 2)
        assert small_board.squares[0][2].is_revealed is True

    @unit
    def test_reveal_mine_sets_lost(self, small_board):
        small_board.reveal_square(0, 0)  # міна тут
        assert small_board.state == BoardState.LOST

    @unit
    def test_reveal_mine_fires_game_lost(self, board_with_callbacks):
        board_with_callbacks.reveal_square(0, 0)
        board_with_callbacks.on_game_lost[0].assert_called_once()

    @unit
    def test_reveal_fires_on_square_revealed(self, board_with_callbacks):
        board_with_callbacks.reveal_square(0, 2)
        board_with_callbacks.on_square_revealed[0].assert_called()

    @unit
    def test_reveal_flagged_square_ignored(self, small_board):
        small_board.flag_square(0, 2)
        small_board.reveal_square(0, 2)
        assert small_board.squares[0][2].is_revealed is False

    @unit
    def test_reveal_already_revealed_ignored(self, small_board):
        """Повторне відкриття вже відкритої клітинки не змінює її стан."""
        small_board.reveal_square(0, 2)
        was_revealed = small_board.squares[0][2].is_revealed
        small_board.reveal_square(0, 2)   # вдруге — без ефекту
        # клітинка залишається відкритою (не закривається знову)
        assert small_board.squares[0][2].is_revealed == was_revealed

    @unit
    def test_reveal_after_game_over_ignored(self, small_board):
        small_board.reveal_square(0, 0)   # програш
        small_board.reveal_square(0, 2)   # після програшу
        assert small_board.squares[0][2].is_revealed is False

    @unit
    def test_reveal_empty_square_cascades(self, safe_board):
        """На дошці без мін відкриття будь-якої клітинки відкриває всі."""
        safe_board.reveal_square(2, 2)
        total = safe_board.rows * safe_board.columns
        revealed = sum(
            1 for i in range(safe_board.rows)
            for j in range(safe_board.columns)
            if safe_board.squares[i][j].is_revealed
        )
        assert revealed == total


# ═══════════════════════════ Board.flag_square ══════════════════════════════

class TestFlagSquare:

    @smoke
    def test_flag_unflagged_square(self, small_board):
        small_board.flag_square(1, 1)
        assert small_board.squares[1][1].is_flagged is True

    @unit
    def test_unflag_flagged_square(self, small_board):
        small_board.flag_square(1, 1)
        small_board.flag_square(1, 1)
        assert small_board.squares[1][1].is_flagged is False

    @unit
    def test_flag_fires_callback(self, board_with_callbacks):
        board_with_callbacks.flag_square(1, 2)
        board_with_callbacks.on_square_flagged[0].assert_called_once_with(1, 2)

    @unit
    def test_flag_revealed_square_ignored(self, small_board):
        small_board.reveal_square(0, 2)
        small_board.flag_square(0, 2)
        assert small_board.squares[0][2].is_flagged is False

    @unit
    def test_flag_after_game_over_ignored(self, small_board):
        small_board.reveal_square(0, 0)   # програш
        small_board.flag_square(1, 1)
        assert small_board.squares[1][1].is_flagged is False

    @pytest.mark.parametrize("row,col", [(0, 1), (1, 0), (2, 2)])
    @unit
    def test_flag_various_cells(self, small_board, row, col):
        small_board.flag_square(row, col)
        assert small_board.squares[row][col].is_flagged is True


# ═══════════════════════════ Board.get_remaining_mines ══════════════════════

class TestGetRemainingMines:

    @smoke
    def test_no_flags_returns_total_mines(self, small_board):
        assert small_board.get_remaining_mines() == 1

    @unit
    def test_one_flag_decreases_remaining(self, small_board):
        small_board.flag_square(1, 1)
        assert small_board.get_remaining_mines() == 0

    @unit
    def test_two_flags_can_go_negative(self, small_board):
        small_board.flag_square(1, 1)
        small_board.flag_square(1, 2)
        assert small_board.get_remaining_mines() == -1

    @pytest.mark.parametrize("flags,expected", [
        (0, 3),
        (1, 2),
        (2, 1),
        (3, 0),
    ])
    @unit
    def test_remaining_with_multiple_flags(self, flags, expected):
        with patch("core.board.random.randint", side_effect=[0, 0, 0, 1, 0, 2]):
            board = Board(4, 4, 3)
        safe_cells = [(r, c) for r in range(4) for c in range(4)
                      if not board.squares[r][c].is_mine]
        for i in range(flags):
            r, c = safe_cells[i]
            board.flag_square(r, c)
        assert board.get_remaining_mines() == expected


# ═══════════════════════════ Win condition ═══════════════════════════════════

class TestWinCondition:

    @unit
    def test_win_fires_callback(self, board_with_callbacks):
        """Відкриття всіх безпечних клітинок викликає on_game_won."""
        board = board_with_callbacks
        for r in range(3):
            for c in range(3):
                if not board.squares[r][c].is_mine:
                    board.reveal_square(r, c)
        board.on_game_won[0].assert_called()

    @unit
    def test_win_state_set(self, small_board):
        for r in range(3):
            for c in range(3):
                if not small_board.squares[r][c].is_mine:
                    small_board.reveal_square(r, c)
        assert small_board.state == BoardState.WON


# ═══════════════════════════ Mock: random ════════════════════════════════════

class TestMocking:

    @unit
    def test_mines_placed_at_mocked_positions(self):
        """Перевіряє, що патч random.randint точно контролює розміщення мін."""
        with patch("core.board.random.randint", side_effect=[1, 2]):
            board = Board(3, 3, 1)
        assert board.squares[1][2].is_mine is True

    @unit
    def test_multiple_callbacks_all_called(self):
        """Усі обробники події викликаються при відкритті міни."""
        cb1, cb2 = MagicMock(), MagicMock()
        with patch("core.board.random.randint", side_effect=[0, 0]):
            board = Board(3, 3, 1)
        board.on_game_lost = [cb1, cb2]
        board.reveal_square(0, 0)
        cb1.assert_called_once()
        cb2.assert_called_once()
