"""
tests/test_game_serializer.py
Unit-тести для serializers/game_serializer.py
"""

import pytest
import os
from serializers.game_serializer import (
    XmlGameSerializer, GameState, SquareState
)


# ─────────────────────────── FIXTURES ───────────────────────────────────────

@pytest.fixture
def serializer():
    return XmlGameSerializer()


@pytest.fixture
def simple_state():
    """2x2 стан гри: міна в [0][0], решта — безпечні."""
    squares = [
        [
            SquareState(is_mine=True,  is_revealed=False, is_flagged=False, adjacent_mines=0),
            SquareState(is_mine=False, is_revealed=True,  is_flagged=False, adjacent_mines=1),
        ],
        [
            SquareState(is_mine=False, is_revealed=False, is_flagged=True,  adjacent_mines=1),
            SquareState(is_mine=False, is_revealed=True,  is_flagged=False, adjacent_mines=1),
        ],
    ]
    return GameState(rows=2, columns=2, mines=1, elapsed=42, squares=squares)


@pytest.fixture
def saved_file(tmp_path, serializer, simple_state):
    path = str(tmp_path / "game.xml")
    serializer.save(path, simple_state)
    return path


# ═══════════════════════════ SquareState ════════════════════════════════════

class TestSquareState:

    def test_fields_set(self):
        sq = SquareState(True, False, True, 3)
        assert sq.is_mine is True
        assert sq.is_revealed is False
        assert sq.is_flagged is True
        assert sq.adjacent_mines == 3


# ═══════════════════════════ GameState ══════════════════════════════════════

class TestGameState:

    def test_defaults(self):
        gs = GameState()
        assert gs.rows == 8
        assert gs.columns == 8
        assert gs.mines == 0
        assert gs.elapsed == 0
        assert gs.squares == []

    def test_custom_values(self, simple_state):
        assert simple_state.rows == 2
        assert simple_state.mines == 1
        assert simple_state.elapsed == 42


# ═══════════════════════════ XmlGameSerializer.save ═════════════════════════

class TestXmlGameSerializerSave:

    def test_file_created(self, saved_file):
        assert os.path.exists(saved_file)

    def test_file_not_empty(self, saved_file):
        assert os.path.getsize(saved_file) > 0

    def test_xml_has_rows_tag(self, saved_file):
        import xml.etree.ElementTree as ET
        root = ET.parse(saved_file).getroot()
        assert root.findtext("Rows") == "2"

    def test_xml_has_mines_tag(self, saved_file):
        import xml.etree.ElementTree as ET
        root = ET.parse(saved_file).getroot()
        assert root.findtext("Mines") == "1"

    def test_xml_has_elapsed_tag(self, saved_file):
        import xml.etree.ElementTree as ET
        root = ET.parse(saved_file).getroot()
        assert root.findtext("Elapsed") == "42"


# ═══════════════════════════ XmlGameSerializer.load ═════════════════════════

class TestXmlGameSerializerLoad:

    def test_returns_none_if_no_file(self, serializer, tmp_path):
        result = serializer.load(str(tmp_path / "missing.xml"))
        assert result is None

    def test_roundtrip_rows(self, serializer, saved_file):
        gs = serializer.load(saved_file)
        assert gs.rows == 2

    def test_roundtrip_columns(self, serializer, saved_file):
        gs = serializer.load(saved_file)
        assert gs.columns == 2

    def test_roundtrip_mines(self, serializer, saved_file):
        gs = serializer.load(saved_file)
        assert gs.mines == 1

    def test_roundtrip_elapsed(self, serializer, saved_file):
        gs = serializer.load(saved_file)
        assert gs.elapsed == 42

    def test_roundtrip_square_mine(self, serializer, saved_file):
        gs = serializer.load(saved_file)
        assert gs.squares[0][0].is_mine is True

    def test_roundtrip_square_revealed(self, serializer, saved_file):
        gs = serializer.load(saved_file)
        assert gs.squares[0][1].is_revealed is True

    def test_roundtrip_square_flagged(self, serializer, saved_file):
        gs = serializer.load(saved_file)
        assert gs.squares[1][0].is_flagged is True

    def test_roundtrip_adjacent_mines(self, serializer, saved_file):
        gs = serializer.load(saved_file)
        assert gs.squares[0][1].adjacent_mines == 1

    @pytest.mark.parametrize("rows,cols,mines", [
        (5, 5, 5),
        (8, 8, 10),
        (16, 30, 99),
    ])
    def test_various_board_sizes(self, serializer, tmp_path, rows, cols, mines):
        squares = [
            [SquareState(False, False, False, 0) for _ in range(cols)]
            for _ in range(rows)
        ]
        state = GameState(rows, cols, mines, 0, squares)
        path = str(tmp_path / f"game_{rows}x{cols}.xml")
        serializer.save(path, state)
        loaded = serializer.load(path)
        assert loaded.rows == rows
        assert loaded.columns == cols
        assert loaded.mines == mines
