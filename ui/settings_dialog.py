"""
ui/settings_dialog.py
Аналог SettingsForm.cs — налаштування гри (рядки, стовпці, кольори тощо).
"""

import pygame
from ui.dialog import Dialog
from ui.helpers import draw_text, draw_button
from ui.constants import (
    TEXT_COLOR, INPUT_BG, INPUT_BORDER, CELL_BORDER,
    FONT_SM, FONT_MD, FONT_BOLD
)
from ui.color_picker import ColorPickerDialog
from core.settings import Settings


class SettingsDialog(Dialog):
    """
    Аналог SettingsForm — містить:
      rowsUpDown, columnsUpDown      → spinner-кнопки
      probabilityTrackBar            → слайдер
      mineColorButton, flagColorButton,
      revealedColorButton, unrevealedColorButton → ColorPickerDialog
      mineImageButton, flagImageButton           → текстові поля шляху
      saveSettingsButton             → зберегти та закрити
    """

    def __init__(self, screen: pygame.Surface, sett: Settings):
        super().__init__(screen, 450, 470, "Налаштування")
        self.sett = sett
        # Копіюємо поточні значення (щоб Cancel не зберігав змін)
        self.rows             = sett.rows
        self.columns          = sett.columns
        self.mine_probability = sett.mine_probability
        self.mine_color       = sett.mine_color
        self.flag_color       = sett.flag_color
        self.revealed_color   = sett.revealed_color
        self.unrevealed_color = sett.unrevealed_color
        self._mine_img_text   = sett.mine_image_path
        self._flag_img_text   = sett.flag_image_path
        self._active_input    = None    # 'mine_img' | 'flag_img' | None
        self._slider_drag     = False
        self._cursor_tick     = 0

    # ── Координати рядків (TableLayoutPanel у C#) ─────────────────────────────

    _LX = 18   # label x
    _CX = 230  # control x
    _CW = 195  # control width

    _Y_ROWS   = 48
    _Y_COLS   = 90
    _Y_PROB   = 132
    _Y_MINE_C = 180
    _Y_FLAG_C = 218
    _Y_REV_C  = 256
    _Y_UNREV  = 294
    _Y_MINE_I = 340
    _Y_FLAG_I = 380
    _Y_SAVE   = 420

    # ── Spinner (NumericUpDown у C#) ─────────────────────────────────────────

    def _draw_spinner(self, label: str, y: int, value: int) -> tuple:
        draw_text(self.surface, label, FONT_MD, TEXT_COLOR, self._LX, y + 14, center=False)
        dec_r = pygame.Rect(self._CX,            y + 2, 36, 30)
        val_r = pygame.Rect(self._CX + 40,       y + 2, 80, 30)
        inc_r = pygame.Rect(self._CX + 124,      y + 2, 36, 30)
        mx, my = self._local_mouse()
        draw_button(self.surface, "−", FONT_BOLD, dec_r, hover=dec_r.collidepoint(mx, my))
        pygame.draw.rect(self.surface, INPUT_BG,     val_r, border_radius=4)
        pygame.draw.rect(self.surface, CELL_BORDER,  val_r, 1, border_radius=4)
        draw_text(self.surface, str(value), FONT_BOLD, TEXT_COLOR,
                  val_r.centerx, val_r.centery, center=True)
        draw_button(self.surface, "+", FONT_BOLD, inc_r, hover=inc_r.collidepoint(mx, my))
        return dec_r, inc_r

    # ── Слайдер (TrackBar у C#) ──────────────────────────────────────────────

    def _draw_slider(self, y: int) -> pygame.Rect:
        label = f"Вірогідність бомби:  {self.mine_probability}%"
        draw_text(self.surface, label, FONT_MD, TEXT_COLOR, self._LX, y + 14, center=False)
        track = pygame.Rect(self._CX, y + 10, self._CW, 12)
        pygame.draw.rect(self.surface, (185, 185, 185), track, border_radius=5)
        prog = (self.mine_probability - 5) / (60 - 5)
        hx   = int(track.x + prog * track.width)
        # Заповнена частина
        if hx > track.x:
            pygame.draw.rect(self.surface, (100, 130, 210),
                             (track.x, track.y, hx - track.x, track.height), border_radius=5)
        pygame.draw.circle(self.surface, (70, 105, 200), (hx, track.centery), 11)
        pygame.draw.circle(self.surface, (255, 255, 255), (hx, track.centery), 5)
        return track

    # ── Рядок кольору ────────────────────────────────────────────────────────

    def _draw_color_row(self, label: str, y: int, color: tuple) -> pygame.Rect:
        draw_text(self.surface, label, FONT_SM, TEXT_COLOR, self._LX, y + 12, center=False)
        swatch = pygame.Rect(self._CX, y + 2, 28, 26)
        pygame.draw.rect(self.surface, color,        swatch, border_radius=4)
        pygame.draw.rect(self.surface, CELL_BORDER,  swatch, 1, border_radius=4)
        btn_r = pygame.Rect(self._CX + 34, y + 2, 120, 26)
        mx, my = self._local_mouse()
        draw_button(self.surface, "Змінити", FONT_SM, btn_r,
                    hover=btn_r.collidepoint(mx, my))
        return btn_r

    # ── Поле вводу шляху до зображення ──────────────────────────────────────

    def _draw_img_row(self, label: str, y: int, text: str, key: str) -> pygame.Rect:
        draw_text(self.surface, label, FONT_SM, TEXT_COLOR, self._LX, y + 12, center=False)
        inp = pygame.Rect(self._CX, y + 2, self._CW, 26)
        active = self._active_input == key
        pygame.draw.rect(self.surface, INPUT_BG, inp, border_radius=4)
        pygame.draw.rect(self.surface,
                         INPUT_BORDER if active else CELL_BORDER, inp, 2, border_radius=4)
        disp = text[-24:] if len(text) > 24 else text
        draw_text(self.surface, disp, FONT_SM, TEXT_COLOR,
                  inp.x + 5, inp.centery, center=False)
        if active and (self._cursor_tick // 30) % 2 == 0:
            px = inp.x + 5 + FONT_SM.size(disp)[0]
            pygame.draw.line(self.surface, TEXT_COLOR,
                             (px, inp.y + 3), (px, inp.bottom - 3), 2)
        return inp

    # ── draw_content ─────────────────────────────────────────────────────────

    def draw_content(self):
        self._cursor_tick += 1
        mx, my = self._local_mouse()

        self._dec_rows, self._inc_rows = self._draw_spinner(
            "Рядки (4–16):", self._Y_ROWS, self.rows)
        self._dec_cols, self._inc_cols = self._draw_spinner(
            "Стовпці (4–16):", self._Y_COLS, self.columns)

        self._track = self._draw_slider(self._Y_PROB)

        self._mine_c_btn  = self._draw_color_row("Колір бомби:",         self._Y_MINE_C, self.mine_color)
        self._flag_c_btn  = self._draw_color_row("Колір прапора:",        self._Y_FLAG_C, self.flag_color)
        self._rev_c_btn   = self._draw_color_row("Колір відкритих клітинок:",  self._Y_REV_C,  self.revealed_color)
        self._unrev_c_btn = self._draw_color_row("Колір закритих клітинок:", self._Y_UNREV, self.unrevealed_color)

        self._mine_i_inp  = self._draw_img_row("Зображ. бомби:", self._Y_MINE_I, self._mine_img_text, "mine_img")
        self._flag_i_inp  = self._draw_img_row("Зображ. прапора:", self._Y_FLAG_I, self._flag_img_text, "flag_img")

        save_r  = pygame.Rect(self.width // 2 - 75, self._Y_SAVE, 150, 38)
        draw_button(self.surface, "Зберегти", FONT_BOLD, save_r,
                    hover=save_r.collidepoint(mx, my))
        self._save_r = save_r

    # ── handle_event ─────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._on_click()
        elif event.type == pygame.MOUSEBUTTONUP:
            self._slider_drag = False
        elif event.type == pygame.MOUSEMOTION and self._slider_drag:
            mx = pygame.mouse.get_pos()[0] - self.x
            self._update_slider(mx)
        elif event.type == pygame.KEYDOWN:
            self._on_key(event)

    def _on_click(self):
        mx, my = self._local_mouse()

        # Spinners
        if self._dec_rows.collidepoint(mx, my): self.rows    = max(4,  self.rows    - 1)
        elif self._inc_rows.collidepoint(mx, my): self.rows  = min(16, self.rows    + 1)
        if self._dec_cols.collidepoint(mx, my): self.columns = max(4,  self.columns - 1)
        elif self._inc_cols.collidepoint(mx, my): self.columns= min(16, self.columns + 1)

        # Slider
        if self._track.inflate(0, 20).collidepoint(mx, my):
            self._slider_drag = True
            self._update_slider(mx + self.x)

        # Color buttons
        color_map = [
            (self._mine_c_btn,  "mine_color"),
            (self._flag_c_btn,  "flag_color"),
            (self._rev_c_btn,   "revealed_color"),
            (self._unrev_c_btn, "unrevealed_color"),
        ]
        for btn, attr in color_map:
            if btn.collidepoint(mx, my):
                dlg = ColorPickerDialog(self.screen, getattr(self, attr))
                col = dlg.run()
                if col is not None:
                    setattr(self, attr, col)
                return

        # Image inputs
        if self._mine_i_inp.collidepoint(mx, my):
            self._active_input = "mine_img"
        elif self._flag_i_inp.collidepoint(mx, my):
            self._active_input = "flag_img"
        else:
            self._active_input = None

        # Save button
        if self._save_r.collidepoint(mx, my):
            self._do_save()

    def _update_slider(self, screen_mx: int):
        track_abs_x = self.x + self._track.x
        prog = max(0.0, min(1.0, (screen_mx - track_abs_x) / self._track.width))
        self.mine_probability = int(5 + prog * (60 - 5))

    def _on_key(self, event: pygame.event.Event):
        if self._active_input == "mine_img":
            self._edit_text(event, "_mine_img_text")
        elif self._active_input == "flag_img":
            self._edit_text(event, "_flag_img_text")
        elif event.key == pygame.K_RETURN:
            self._do_save()
        elif event.key == pygame.K_ESCAPE:
            self.result  = "cancel"
            self.running = False

    def _edit_text(self, event: pygame.event.Event, attr: str):
        if event.key == pygame.K_BACKSPACE:
            setattr(self, attr, getattr(self, attr)[:-1])
        elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
            self._active_input = None
        elif event.unicode.isprintable() and len(getattr(self, attr)) < 260:
            setattr(self, attr, getattr(self, attr) + event.unicode)

    # ── saveSettingsButton_Click ──────────────────────────────────────────────

    def _do_save(self):
        """Аналог saveSettingsButton_Click у C#."""
        self.sett.rows             = self.rows
        self.sett.columns          = self.columns
        self.sett.mine_probability = self.mine_probability
        self.sett.mine_color       = self.mine_color
        self.sett.flag_color       = self.flag_color
        self.sett.revealed_color   = self.revealed_color
        self.sett.unrevealed_color = self.unrevealed_color
        self.sett.mine_image_path  = self._mine_img_text
        self.sett.flag_image_path  = self._flag_img_text
        self.sett.save()
        self.result  = "ok"
        self.running = False
