# minesweeper.spec
# Збірка .exe через PyInstaller
#
# Встановлення:  pip install pygame pyinstaller
# Збірка:        pyinstaller minesweeper.spec
# Результат:     dist/Minesweeper.exe

import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pygame', 'pygame.font', 'pygame.display',
        'pygame.event', 'pygame.image', 'pygame.mixer',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'numpy', 'matplotlib'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Minesweeper',
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # без консольного вікна (WinExe у C#)
    # icon='assets/minesweeper.ico',   # розкоментуйте за наявності .ico
)
