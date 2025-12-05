@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\pythonw.exe" "pos_app.py"
) else (
    echo Virtual environment not found!
    echo Please ensure .venv exists.
    pause
)
