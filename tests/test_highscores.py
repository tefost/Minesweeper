"""
tests/test_highscores.py
Unit-тести для core/highscores.py
"""

import pytest
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

from core.highscores import HighscoreEntry, load_highscores, save_highscores


# ─────────────────────────── FIXTURES ───────────────────────────────────────

@pytest.fixture
def sample_entries():
    return [
        HighscoreEntry("Alice", 42, datetime(2024, 1, 15, 10, 0, 0)),
        HighscoreEntry("Bob",   99, datetime(2024, 3, 20, 12, 30, 0)),
    ]


@pytest.fixture
def tmp_highscores(tmp_path, sample_entries):
    """Зберігає приклад у тимчасовий файл і повертає шлях."""
    file_path = tmp_path / "highscores.xml"
    import core.highscores as hs_module
    original = hs_module.HIGHSCORES_FILE
    hs_module.HIGHSCORES_FILE = str(file_path)
    save_highscores(sample_entries)
    yield file_path
    hs_module.HIGHSCORES_FILE = original


# ═══════════════════════════ HighscoreEntry ══════════════════════════════════

class TestHighscoreEntry:

    def test_stores_name(self):
        e = HighscoreEntry("Test", 10, datetime.now())
        assert e.name == "Test"

    def test_stores_time(self):
        e = HighscoreEntry("Test", 55, datetime.now())
        assert e.time == 55

    def test_stores_date(self):
        d = datetime(2024, 6, 1)
        e = HighscoreEntry("Test", 0, d)
        assert e.date == d


# ═══════════════════════════ load_highscores ════════════════════════════════

class TestLoadHighscores:

    def test_returns_empty_list_if_no_file(self, tmp_path):
        import core.highscores as hs_module
        original = hs_module.HIGHSCORES_FILE
        hs_module.HIGHSCORES_FILE = str(tmp_path / "nonexistent.xml")
        result = load_highscores()
        hs_module.HIGHSCORES_FILE = original
        assert result == []

    def test_loads_correct_count(self, tmp_highscores):
        entries = load_highscores()
        assert len(entries) == 2

    def test_loads_name(self, tmp_highscores):
        entries = load_highscores()
        names = [e.name for e in entries]
        assert "Alice" in names

    def test_loads_time(self, tmp_highscores):
        entries = load_highscores()
        times = {e.name: e.time for e in entries}
        assert times["Alice"] == 42

    def test_loads_date(self, tmp_highscores):
        entries = load_highscores()
        alice = next(e for e in entries if e.name == "Alice")
        assert alice.date.year == 2024

    def test_fallback_date_on_invalid_xml(self, tmp_path):
        """Пошкоджена дата у XML → datetime.now() використовується."""
        file_path = tmp_path / "highscores.xml"
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<ArrayOfHighscoreEntry>
  <HighscoreEntry>
    <Name>Charlie</Name>
    <Time>30</Time>
    <Date>INVALID_DATE</Date>
  </HighscoreEntry>
</ArrayOfHighscoreEntry>"""
        file_path.write_text(xml_content, encoding="utf-8")
        import core.highscores as hs_module
        original = hs_module.HIGHSCORES_FILE
        hs_module.HIGHSCORES_FILE = str(file_path)
        entries = load_highscores()
        hs_module.HIGHSCORES_FILE = original
        assert len(entries) == 1
        assert entries[0].name == "Charlie"


# ═══════════════════════════ save_highscores ════════════════════════════════

class TestSaveHighscores:

    def test_file_created(self, tmp_path, sample_entries):
        file_path = tmp_path / "hs.xml"
        import core.highscores as hs_module
        original = hs_module.HIGHSCORES_FILE
        hs_module.HIGHSCORES_FILE = str(file_path)
        save_highscores(sample_entries)
        hs_module.HIGHSCORES_FILE = original
        assert file_path.exists()

    def test_save_and_reload_roundtrip(self, tmp_highscores):
        entries = load_highscores()
        assert len(entries) == 2
        names = {e.name for e in entries}
        assert names == {"Alice", "Bob"}

    @pytest.mark.parametrize("name,time_s", [
        ("Zara", 5),
        ("Анонім", 120),
        ("Player1", 999),
    ])
    def test_save_various_entries(self, tmp_path, name, time_s):
        file_path = tmp_path / "hs.xml"
        import core.highscores as hs_module
        original = hs_module.HIGHSCORES_FILE
        hs_module.HIGHSCORES_FILE = str(file_path)
        entries = [HighscoreEntry(name, time_s, datetime(2024, 1, 1))]
        save_highscores(entries)
        loaded = load_highscores()
        hs_module.HIGHSCORES_FILE = original
        assert loaded[0].name == name
        assert loaded[0].time == time_s
