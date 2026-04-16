"""
core/highscores.py
Аналог HighscoreEntry.cs + логіка збереження/завантаження highscores.xml.
"""

import xml.etree.ElementTree as ET
import os
from datetime import datetime

HIGHSCORES_FILE = "highscores.xml"


class HighscoreEntry:
    """Аналог public class HighscoreEntry."""

    def __init__(self, name: str, time_seconds: int, date: datetime):
        self.name = name
        self.time = time_seconds
        self.date = date


def load_highscores() -> list[HighscoreEntry]:
    """Аналог LoadHighscores() у MainPresenter.cs — XmlSerializer.Deserialize."""
    entries: list[HighscoreEntry] = []
    if not os.path.exists(HIGHSCORES_FILE):
        return entries
    try:
        tree = ET.parse(HIGHSCORES_FILE)
        root = tree.getroot()
        for elem in root.findall("HighscoreEntry"):
            name     = elem.findtext("Name") or "Анонім"
            time_val = int(elem.findtext("Time") or 0)
            date_str = elem.findtext("Date") or ""
            try:
                date = datetime.fromisoformat(date_str)
            except Exception:
                date = datetime.now()
            entries.append(HighscoreEntry(name, time_val, date))
    except Exception:
        pass
    return entries


def save_highscores(entries: list[HighscoreEntry]):
    """Аналог SaveHighscores() у MainPresenter.cs — XmlSerializer.Serialize."""
    try:
        root = ET.Element("ArrayOfHighscoreEntry")
        for entry in entries:
            elem = ET.SubElement(root, "HighscoreEntry")
            ET.SubElement(elem, "Name").text = entry.name
            ET.SubElement(elem, "Time").text = str(entry.time)
            ET.SubElement(elem, "Date").text = entry.date.isoformat()
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(HIGHSCORES_FILE, encoding="utf-8", xml_declaration=True)
    except Exception:
        pass  # ігноруємо помилки збереження (як у C#)
