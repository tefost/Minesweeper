"""
core/settings.py
Аналог Properties/Settings.settings у C# (ApplicationSettingsBase).
Зберігає налаштування у JSON-файл замість app.config.
"""

import json
import os

SETTINGS_FILE = "minesweeper_settings.json"

# Іменовані кольори (як у System.Drawing.Color у C#)
COLOR_MAP: dict[str, tuple[int, int, int]] = {
    "Red":       (220,  50,  50),
    "Green":     ( 34, 139,  34),
    "LightGray": (211, 211, 211),
    "Gray":      (128, 128, 128),
    "Blue":      (  0,   0, 200),
    "DarkBlue":  (  0,   0, 139),
    "DarkRed":   (139,   0,   0),
    "Teal":      (  0, 128, 128),
    "White":     (255, 255, 255),
    "Black":     ( 20,  20,  20),
    "Yellow":    (255, 215,   0),
    "Orange":    (255, 165,   0),
    "Purple":    (128,   0, 128),
    "Cyan":      (  0, 180, 180),
    "Navy":      (  0,  50, 100),
}


class Settings:
    """
    Зберігає всі налаштування гри (аналог internal sealed partial class Settings).

    DefaultSettingValue відповідає значенням за замовчуванням нижче.
    """

    def __init__(self):
        # [DefaultSettingValue("5")]
        self.rows:             int                    = 8
        # [DefaultSettingValue("5")]
        self.columns:          int                    = 8
        # [DefaultSettingValue("40")]
        self.mine_probability: int                    = 20
        # [DefaultSettingValue("Red")]
        self.mine_color:       tuple[int, int, int]   = COLOR_MAP["Red"]
        # [DefaultSettingValue("Green")]
        self.flag_color:       tuple[int, int, int]   = COLOR_MAP["Green"]
        # [DefaultSettingValue("LightGray")]
        self.revealed_color:   tuple[int, int, int]   = COLOR_MAP["LightGray"]
        # [DefaultSettingValue("Gray")]
        self.unrevealed_color: tuple[int, int, int]   = COLOR_MAP["Gray"]
        # [DefaultSettingValue("")]
        self.mine_image_path:  str                    = ""
        # [DefaultSettingValue("")]
        self.flag_image_path:  str                    = ""

        self.load()

    # ── Аналог ApplicationSettingsBase.Save() ───────────────────────────────

    def save(self):
        try:
            data = {
                "rows":             self.rows,
                "columns":          self.columns,
                "mine_probability": self.mine_probability,
                "mine_color":       list(self.mine_color),
                "flag_color":       list(self.flag_color),
                "revealed_color":   list(self.revealed_color),
                "unrevealed_color": list(self.unrevealed_color),
                "mine_image_path":  self.mine_image_path,
                "flag_image_path":  self.flag_image_path,
            }
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # ігноруємо помилки збереження (як у C#)

    # ── Завантаження при старті ──────────────────────────────────────────────

    def load(self):
        if not os.path.exists(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            self.rows             = d.get("rows",             self.rows)
            self.columns          = d.get("columns",          self.columns)
            self.mine_probability = d.get("mine_probability", self.mine_probability)
            self.mine_color       = tuple(d.get("mine_color",       list(self.mine_color)))
            self.flag_color       = tuple(d.get("flag_color",       list(self.flag_color)))
            self.revealed_color   = tuple(d.get("revealed_color",   list(self.revealed_color)))
            self.unrevealed_color = tuple(d.get("unrevealed_color", list(self.unrevealed_color)))
            self.mine_image_path  = d.get("mine_image_path",  "")
            self.flag_image_path  = d.get("flag_image_path",  "")
        except Exception:
            pass
