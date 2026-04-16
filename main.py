import sys
import pygame

from core.settings import Settings
from ui.constants  import MENU_H, STATUS_H, CELL_SIZE, MIN_WIN_W
from ui.menu_bar   import MenuBar
from ui.game_view  import GameView
from presenter.main_presenter import MainPresenter


def make_screen(view: GameView) -> pygame.Surface:
    w, h = view.window_size()
    return pygame.display.set_mode((w, h))


def main():
    pygame.init()
    pygame.display.set_caption("Minesweeper")

    sett   = Settings()

    # Початковий розмір вікна
    init_w = max(sett.columns * CELL_SIZE + 2, MIN_WIN_W)
    init_h = MENU_H + STATUS_H + sett.rows * CELL_SIZE + 2
    screen = pygame.display.set_mode((init_w, init_h))

    view      = GameView(screen, sett)
    presenter = MainPresenter(screen, sett, view)
    menu      = MenuBar()

    # Нова гра одразу після старту
    presenter.new_game()

    clock = pygame.time.Clock()

    while True:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():

            # ── Закриття вікна ────────────────────────────────────────────────
            if event.type == pygame.QUIT:
                sett.save()
                pygame.quit()
                sys.exit()

            # ── Клавіші ───────────────────────────────────────────────────────
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2:
                    presenter.new_game()
                    # Оновлюємо розмір вікна якщо змінились налаштування
                    w, h = view.window_size()
                    screen = pygame.display.set_mode((w, h))
                    presenter.screen = screen
                    view.screen      = screen
                elif event.key == pygame.K_ESCAPE:
                    menu.open_menu = None

            # ── Миша ─────────────────────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:                           # ЛКМ
                    action = menu.click(mx, my)
                    if action:
                        _handle_action(action, presenter, menu,
                                       screen, sett, view)
                    elif not menu.covers(mx, my):
                        row, col = view.get_cell_at(mx, my)
                        if row is not None:
                            presenter.reveal_square(row, col)

                elif event.button == 3:                         # ПКМ
                    if not menu.covers(mx, my):
                        row, col = view.get_cell_at(mx, my)
                        if row is not None:
                            presenter.flag_square(row, col)

        # ── Таймер ────────────────────────────────────────────────────────────
        presenter.tick_time()

        # ── Малювання ─────────────────────────────────────────────────────────
        view.draw(
            screen,
            presenter.get_elapsed(),
            presenter.get_remaining_mines(),
            presenter.game_over,
            presenter.won,
        )
        menu.draw(screen, mx, my)
        pygame.display.flip()
        clock.tick(60)


def _handle_action(
    action: str,
    presenter: MainPresenter,
    menu: MenuBar,
    screen: pygame.Surface,
    sett: Settings,
    view: GameView,
):
    """Обробник пунктів меню (аналог ToolStripMenuItem.Click handlers у C#)."""
    if action == "Нова гра":
        presenter.new_game()
        w, h = view.window_size()
        new_screen = pygame.display.set_mode((w, h))
        presenter.screen = new_screen
        view.screen      = new_screen

    elif action == "Зберегти гру":
        presenter.save_game()

    elif action == "Завантажити гру":
        presenter.load_game()

    elif action == "Таблиця рекордів":
        presenter.show_highscores()

    elif action == "Налаштування":
        if presenter.show_settings():
            presenter.new_game()
            w, h = view.window_size()
            new_screen = pygame.display.set_mode((w, h))
            presenter.screen = new_screen
            view.screen      = new_screen

    elif action == "Вихід":
        sett.save()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
