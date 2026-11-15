@echo off
setlocal
cd /d "%~dp0"

py -3.12 -m pip install -r requirements-build.txt
if errorlevel 1 exit /b 1

py -3.12 -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name Durhack2026 ^
    --runtime-hook packaging\pyi_rth_paths.py ^
    --add-data "graphics;graphics" ^
    --add-data "sounds;sounds" ^
    --paths . --paths .. ^
    --hidden-import Durhack2026.dhtypes.soundTypes ^
    --hidden-import Durhack2026.sounds.sound_effect_dict ^
    --hidden-import Durhack2026.functions.SoundEngine ^
    --collect-all pygame ^
    --collect-all pymunk ^
    main.py
if errorlevel 1 exit /b 1

echo Built dist\Durhack2026.exe
