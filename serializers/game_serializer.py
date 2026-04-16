"""
serializers/game_serializer.py
Аналог IGameSerializer.cs, GameState.cs, XmlGameSerializer.cs.
Зберігає ПОВНИЙ стан поля: міни, відкриті клітинки, прапорці, час.
"""

import xml.etree.ElementTree as ET
import os


class SquareState:
    """Стан однієї клітинки для серіалізації."""
    def __init__(self, is_mine: bool, is_revealed: bool,
                 is_flagged: bool, adjacent_mines: int):
        self.is_mine       = is_mine
        self.is_revealed   = is_revealed
        self.is_flagged    = is_flagged
        self.adjacent_mines = adjacent_mines


class GameState:
    """Повний стан гри для збереження."""

    def __init__(self, rows: int = 8, columns: int = 8, mines: int = 0,
                 elapsed: int = 0,
                 squares: list[list[SquareState]] | None = None):
        self.rows    = rows
        self.columns = columns
        self.mines   = mines
        self.elapsed = elapsed          # секунди таймера
        self.squares = squares or []    # список списків SquareState


class XmlGameSerializer:
    """
    Аналог XmlGameSerializer (IGameSerializer).
    Зберігає повний стан поля у XML.
    """

    def save(self, file_path: str, state: GameState):
        """Зберегти гру у XML файл."""
        root = ET.Element("GameState")
        ET.SubElement(root, "Rows").text    = str(state.rows)
        ET.SubElement(root, "Columns").text = str(state.columns)
        ET.SubElement(root, "Mines").text   = str(state.mines)
        ET.SubElement(root, "Elapsed").text = str(state.elapsed)

        board_el = ET.SubElement(root, "Board")
        for row in state.squares:
            row_el = ET.SubElement(board_el, "Row")
            for sq in row:
                sq_el = ET.SubElement(row_el, "Square")
                sq_el.set("mine",     "1" if sq.is_mine     else "0")
                sq_el.set("revealed", "1" if sq.is_revealed else "0")
                sq_el.set("flagged",  "1" if sq.is_flagged  else "0")
                sq_el.set("adj",      str(sq.adjacent_mines))

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(file_path, encoding="utf-8", xml_declaration=True)

    def load(self, file_path: str) -> GameState | None:
        """Завантажити гру з XML файлу."""
        if not os.path.exists(file_path):
            return None

        tree = ET.parse(file_path)
        root = tree.getroot()

        rows    = int(root.findtext("Rows")    or 8)
        columns = int(root.findtext("Columns") or 8)
        mines   = int(root.findtext("Mines")   or 0)
        elapsed = int(root.findtext("Elapsed") or 0)

        squares: list[list[SquareState]] = []
        board_el = root.find("Board")
        if board_el is not None:
            for row_el in board_el.findall("Row"):
                row = []
                for sq_el in row_el.findall("Square"):
                    row.append(SquareState(
                        is_mine       = sq_el.get("mine",     "0") == "1",
                        is_revealed   = sq_el.get("revealed", "0") == "1",
                        is_flagged    = sq_el.get("flagged",  "0") == "1",
                        adjacent_mines= int(sq_el.get("adj",  "0")),
                    ))
                squares.append(row)

        return GameState(rows, columns, mines, elapsed, squares)