@echo off
cd /d "%~dp0"
python run_netra.py --check
if errorlevel 1 (
  pause
  exit /b 1
)
echo Open http://127.0.0.1:8001 in your browser.
python run_netra.py
pause
