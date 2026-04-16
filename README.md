# Minesweeper — Python / pygame

Повний порт гри **Minesweeper** з C# (Windows Forms) на Python 3 + pygame.  
Вся логіка методів збережена без змін — лише синтаксис адаптовано.

---

## Структура проекту

```
minesweeper/
├── main.py                         # Точка входу (аналог Program.cs)
├── minesweeper.spec                # Конфіг PyInstaller для збірки .exe
│
├── core/                           # Бізнес-логіка
│   ├── board.py                    # Square, Board, BoardState  ← Board.cs
│   ├── settings.py                 # Settings (JSON)            ← Properties/Settings
│   └── highscores.py               # HighscoreEntry, load/save  ← HighscoreEntry.cs
│
├── serializers/                    # Серіалізатори стану гри
│   └── game_serializer.py          # GameState, XmlGameSerializer ← GameState.cs
│
├── ui/                             # Весь UI (pygame)
│   ├── constants.py                # Кольори, шрифти, розміри
│   ├── helpers.py                  # draw_text, draw_button
│   ├── dialog.py                   # Базовий Dialog (Form.ShowDialog)
│   ├── message_box.py              # MessageBox              ← MessageBox.Show()
│   ├── game_won_dialog.py          # GameWonDialog           ← GameWonForm.cs
│   ├── highscores_dialog.py        # HighscoresDialog        ← HighscoresForm.cs
│   ├── color_picker.py             # ColorPickerDialog       ← ColorDialog
│   ├── settings_dialog.py          # SettingsDialog          ← SettingsForm.cs
│   ├── file_dialog.py              # FileNameDialog          ← SaveFileDialog / OpenFileDialog
│   ├── menu_bar.py                 # MenuBar                 ← MenuStrip
│   └── game_view.py                # GameView (IMainView)    ← MainForm (відображення)
│
└── presenter/                      # Presenter (MVP-патерн)
    └── main_presenter.py           # MainPresenter           ← MainPresenter.cs
```

---

## Відповідність C# → Python

| C# клас / концепт              | Python модуль / клас                  |
|-------------------------------|---------------------------------------|
| `Square`                      | `core/board.py → Square`             |
| `Board`, `BoardState`         | `core/board.py → Board, BoardState`  |
| `Properties.Settings`         | `core/settings.py → Settings`        |
| `HighscoreEntry`              | `core/highscores.py → HighscoreEntry`|
| `IGameSerializer`, `GameState`| `serializers/game_serializer.py`     |
| `IMainView`                   | `ui/game_view.py → GameView`         |
| `MainForm` (малювання)        | `ui/game_view.py → GameView.draw()`  |
| `MainPresenter`               | `presenter/main_presenter.py`        |
| `GameWonForm`                 | `ui/game_won_dialog.py`              |
| `HighscoresForm`              | `ui/highscores_dialog.py`            |
| `SettingsForm`                | `ui/settings_dialog.py`              |
| `MessageBox.Show`             | `ui/message_box.py → show_message`   |
| `SaveFileDialog/OpenFileDialog`| `ui/file_dialog.py`                 |
| `MenuStrip`                   | `ui/menu_bar.py → MenuBar`           |
| `Program.cs / Application.Run`| `main.py → main()`                  |

---

## Управління

| Дія              | Клавіша / кнопка     |
|-----------------|----------------------|
| Відкрити клітинку | **ЛКМ**            |
| Поставити прапор  | **ПКМ**            |
| Нова гра          | **F2**             |
| Закрити меню      | **Esc**            |
| Меню              | клік на «Гра»      |

---

## Встановлення та запуск

```bash
pip install pygame
python main.py
```

## Збірка .exe (Windows)

```bash
pip install pygame pyinstaller
pyinstaller minesweeper.spec
```

Готовий `dist/Minesweeper.exe` не потребує Python на комп'ютері.

Або одною командою:

```bash
pyinstaller --onefile --noconsole --name Minesweeper main.py
```

---

## Збережені файли

| Файл                        | Призначення              |
|----------------------------|--------------------------|
| `minesweeper_settings.json` | Налаштування (колір, розмір поля, вірогідність) |
| `highscores.xml`            | Таблиця рекордів (сумісний формат з C# версією) |
