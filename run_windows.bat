@echo off
rem Double-click to play. First run sets everything up automatically
rem (private Python environment + modules); later runs start straight away.
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title Durhack2026

rem Prebuilt executable (from build_windows.bat or the GitHub Actions artifact)
if exist "dist\Durhack2026.exe" (
    start "" "dist\Durhack2026.exe"
    exit /b 0
)

set "VENV=%~dp0.venv"
set "PY=%VENV%\Scripts\python.exe"
if exist "%PY%" goto deps

rem pygame 2.6.1 only ships Windows wheels up to Python 3.13, numpy 2.5.4 from 3.12
echo Looking for Python 3.12 / 3.13...
set "BASE="
for %%V in (3.12 3.13) do (
    if not defined BASE (
        py -%%V -c "pass" >nul 2>&1 && set "BASE=py -%%V"
    )
)
if not defined BASE (
    python -c "import sys; sys.exit(sys.version_info[:2] not in ((3,12),(3,13)))" >nul 2>&1 && set "BASE=python"
)
if not defined BASE (
    for %%V in (312 313) do (
        if not defined BASE if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" set "BASE="%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe""
    )
)
if not defined BASE (
    echo Python 3.12 not found - installing it for this user with winget...
    winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "BASE="%LOCALAPPDATA%\Programs\Python\Python312\python.exe""
)
if not defined BASE (
    echo.
    echo Could not find or install Python 3.12.
    echo Install it from https://www.python.org/downloads/release/python-3120/ and run this file again.
    pause
    exit /b 1
)

echo Creating private environment in .venv ...
%BASE% -m venv "%VENV%"
if errorlevel 1 goto fail

:deps
echo Checking modules...
"%PY%" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto fail

rem The code imports itself as package "Durhack2026", so the folder must have that
rem name. If it doesn't (e.g. "Durhack2026-main" from a GitHub zip), expose it
rem under that name through a junction outside the repo.
for %%I in ("%~dp0.") do set "DIRNAME=%%~nxI"
if /i not "%DIRNAME%"=="Durhack2026" (
    set "LINKROOT=%LOCALAPPDATA%\Durhack2026-run"
    if not exist "!LINKROOT!" mkdir "!LINKROOT!"
    rmdir "!LINKROOT!\Durhack2026" >nul 2>&1
    mklink /J "!LINKROOT!\Durhack2026" "%~dp0." >nul
    if errorlevel 1 goto fail
    set "PYTHONPATH=!LINKROOT!"
)

echo Starting Durhack2026...
"%PY%" main.py
if errorlevel 1 goto fail
exit /b 0

:fail
echo.
echo Something went wrong - see the messages above.
pause
exit /b 1
