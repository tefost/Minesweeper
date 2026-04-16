"""
presenter/main_presenter.py
Аналог MainPresenter.cs — вся ігрова логіка (без малювання).
"""

import pygame
from datetime import datetime

from core.board import Board, BoardState, Square
from core.settings import Settings
from core.highscores import HighscoreEntry, load_highscores, save_highscores
from serializers.game_serializer import GameState, SquareState, XmlGameSerializer
from ui.game_view import GameView
from ui.message_box import show_message
from ui.game_won_dialog import GameWonDialog
from ui.highscores_dialog import HighscoresDialog
from ui.settings_dialog import SettingsDialog
from ui.file_dialog import ask_save_path, ask_load_path


class MainPresenter:
    """
    Відповідає public class MainPresenter : IMainPresenter у C#.

    Зв'язує:
      - Board (логіка поля)
      - GameView (IMainView — відображення)
      - Highscores, Settings, Serializer
    """

    def __init__(self, screen: pygame.Surface, sett: Settings, view: GameView):
        self.screen = screen
        self.sett   = sett
        self.view   = view

        self.board:           Board | None          = None
        self.highscores:      list[HighscoreEntry]  = load_highscores()
        self._serializer:     XmlGameSerializer     = XmlGameSerializer()
        self._game_start:     datetime | None       = None
        self._elapsed_sec:    int                   = 0
        self.game_over:       bool                  = False
        self.won:             bool                  = False

    # ── public void NewGame() ─────────────────────────────────────────────────

    def new_game(self):
        rows    = self.sett.rows
        columns = self.sett.columns
        mines   = max(1, (rows * columns * self.sett.mine_probability) // 100)

        self.game_over     = False
        self.won           = False
        self._elapsed_sec  = 0
        self._game_start   = None

        self.view.show_board(rows, columns)
        self.board = Board(rows, columns, mines)

        self.board.on_square_revealed.append(self._on_square_revealed)
        self.board.on_square_flagged.append(self._on_square_flagged)
        self.board.on_game_lost.append(self._on_game_lost)
        self.board.on_game_won.append(self._on_game_won)

    # ── Events ────────────────────────────────────────────────────────────────

    def _on_square_revealed(self, row: int, col: int, adjacent_mines: int):
        self.view.show_revealed(row, col, adjacent_mines)

    def _on_square_flagged(self, row: int, col: int):
        flagged = self.board.squares[row][col].is_flagged
        self.view.show_flag(row, col, flagged)

    def _on_game_lost(self):
        if self.board:
            for i in range(self.board.rows):
                for j in range(self.board.columns):
                    if self.board.squares[i][j].is_mine:
                        self.view.show_mine(i, j)
        self.game_over = True
        self.won       = False
        self._render_and_flip()
        show_message(self.screen, "Ви програли!\nСпробуйте ще раз.", "Кінець гри")

    def _on_game_won(self):
        self.game_over = True
        self.won       = True
        elapsed = self._get_elapsed()
        self._render_and_flip()

        dlg    = GameWonDialog(self.screen, elapsed)
        result = dlg.run()

        if result and result[0] == "ok":
            name = result[1] or "Анонім"
            self.highscores.append(HighscoreEntry(name, elapsed, datetime.now()))
            save_highscores(self.highscores)

    # ── public void RevealSquare / FlagSquare ─────────────────────────────────

    def reveal_square(self, row: int, col: int):
        if self.board is None:
            return
        if self._game_start is None:
            self._game_start = datetime.now()
        self.board.reveal_square(row, col)

    def flag_square(self, row: int, col: int):
        if self.board is None:
            return
        if self._game_start is None:
            self._game_start = datetime.now()
        self.board.flag_square(row, col)

    # ── public void ShowHighscores / ShowSettings ─────────────────────────────

    def show_highscores(self):
        HighscoresDialog(self.screen, self.highscores).run()

    def show_settings(self) -> bool:
        dlg    = SettingsDialog(self.screen, self.sett)
        result = dlg.run()
        if result == "ok":
            self.view.reload_images()
            ans = show_message(
                self.screen,
                "Налаштування змінено.\nПочати нову гру, щоб застосувати зміни?",
                "Установки",
                ("Так", "Ні"),
            )
            return ans == "Так"
        return False

    # ── public void SaveGame() ────────────────────────────────────────────────

    def save_game(self):
        if self.board is None:
            show_message(self.screen, "Немає активної гри для збереження.", "Збереження")
            return

        # Системний діалог вибору файлу
        path = ask_save_path(initial_file="save_game.xml")
        if not path:
            return  # користувач скасував

        try:
            # Збираємо повний стан кожної клітинки
            sq_states = [
                [
                    SquareState(
                        is_mine        = self.board.squares[r][c].is_mine,
                        is_revealed    = self.board.squares[r][c].is_revealed,
                        is_flagged     = self.board.squares[r][c].is_flagged,
                        adjacent_mines = self.board.squares[r][c].adjacent_mines,
                    )
                    for c in range(self.board.columns)
                ]
                for r in range(self.board.rows)
            ]

            state = GameState(
                rows    = self.board.rows,
                columns = self.board.columns,
                mines   = self.board.mines,
                elapsed = self._get_elapsed(),
                squares = sq_states,
            )
            self._serializer.save(path, state)
            show_message(self.screen, "Гру збережено успішно!", "Збереження")

        except Exception as exc:
            show_message(self.screen, f"Помилка при збереженні гри!\n{exc}", "Помилка")

    # ── public void LoadGame() ────────────────────────────────────────────────

    def load_game(self):
        # Системний діалог вибору файлу
        path = ask_load_path()
        if not path:
            return  # користувач скасував

        try:
            state = self._serializer.load(path)
            if state is None:
                raise FileNotFoundError("Файл не знайдено або пошкоджено")

            # Оновлюємо налаштування
            self.sett.rows    = state.rows
            self.sett.columns = state.columns

            # Відновлюємо view
            self.view.show_board(state.rows, state.columns)

            # Відновлюємо Board без випадкової генерації
            self.board = Board.__new__(Board)
            self.board.rows    = state.rows
            self.board.columns = state.columns
            self.board.mines   = state.mines
            self.board.state   = BoardState.IN_PROGRESS
            self.board.on_square_revealed = [self._on_square_revealed]
            self.board.on_square_flagged  = [self._on_square_flagged]
            self.board.on_game_lost       = [self._on_game_lost]
            self.board.on_game_won        = [self._on_game_won]

            # Відновлюємо клітинки
            self.board.squares = []
            for r, row in enumerate(state.squares):
                sq_row = []
                for c, sq_st in enumerate(row):
                    sq = Square()
                    sq.is_mine        = sq_st.is_mine
                    sq.is_revealed    = sq_st.is_revealed
                    sq.is_flagged     = sq_st.is_flagged
                    sq.adjacent_mines = sq_st.adjacent_mines
                    sq_row.append(sq)

                    # Відновлюємо відображення у view
                    if sq.is_revealed:
                        self.view.show_revealed(r, c, sq.adjacent_mines)
                    if sq.is_flagged:
                        self.view.show_flag(r, c, True)

                self.board.squares.append(sq_row)

            # Відновлюємо таймер
            self._elapsed_sec = state.elapsed
            self._game_start  = None   # таймер продовжиться при наступному ході
            self.game_over    = False
            self.won          = False

            show_message(self.screen, "Гру завантажено успішно!", "Завантаження")

        except Exception as exc:
            show_message(self.screen, f"Помилка при завантаженні гри!\n{exc}", "Помилка")

    # ── Допоміжні ─────────────────────────────────────────────────────────────

    def _get_elapsed(self) -> int:
        if self._game_start:
            return int((datetime.now() - self._game_start).total_seconds())
        return self._elapsed_sec

    def tick_time(self):
        if self._game_start and not self.game_over:
            self._elapsed_sec = int(
                (datetime.now() - self._game_start).total_seconds())

    def get_elapsed(self) -> int:
        return self._elapsed_sec

    def get_remaining_mines(self) -> int:
        return self.board.get_remaining_mines() if self.board else 0

    def _render_and_flip(self):
        self.view.draw(
            self.screen,
            self._elapsed_sec,
            self.get_remaining_mines(),
            self.game_over,
            self.won,
        )
        pygame.display.flip()