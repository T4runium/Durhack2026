https://devpost.com/software/1550452/joins/-oovUBqLqzD4U3ve1nXUvg

## Running on Windows

Double-click `run_windows.bat`. On first run it finds (or installs via winget)
Python 3.12, creates a private `.venv` with the required modules, then starts
the game. Later runs start straight away.

## Windows executable

The GitHub Actions workflow builds a standalone Windows executable with the
Python runtime, dependencies, and game assets included. Download and extract
the `Durhack2026-Windows` artifact from the latest successful
**Build Windows executable** workflow run, then launch `Durhack2026.exe`.

To build it locally on Windows, install Python 3.12 and run `build_windows.bat`.