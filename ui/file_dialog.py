"""
ui/file_dialog.py
Системні діалоги відкриття/збереження через tkinter.
Аналог SaveFileDialog / OpenFileDialog у C# (Windows Forms).
"""

import os
import tkinter as tk
from tkinter import filedialog


def _make_root() -> tk.Tk:
    """Створює приховане tkinter-вікно поверх усіх вікон."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()
    return root


def ask_save_path(initial_file: str = "save_game.xml") -> str | None:
    """
    Показує системний діалог «Зберегти як».
    Повертає повний шлях або None якщо скасовано.
    """
    root = _make_root()
    path = filedialog.asksaveasfilename(
        parent=root,
        title="Зберегти гру",
        initialdir=os.path.expanduser("~"),
        initialfile=initial_file,
        defaultextension=".xml",
        filetypes=[("XML файли збереження", "*.xml"), ("Усі файли", "*.*")],
    )
    root.destroy()
    return path if path else None


def ask_load_path() -> str | None:
    """
    Показує системний діалог «Відкрити файл».
    Повертає повний шлях або None якщо скасовано.
    """
    root = _make_root()
    path = filedialog.askopenfilename(
        parent=root,
        title="Завантажити гру",
        initialdir=os.path.expanduser("~"),
        filetypes=[("XML файли збереження", "*.xml"), ("Усі файли", "*.*")],
    )
    root.destroy()
    return path if path else None