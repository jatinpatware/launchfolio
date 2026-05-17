@echo off
:: LaunchFolio — one-command setup for Windows
echo.
echo   LaunchFolio - Setup
echo   -----------------------------------------
echo.

:: 1. Check Python
python --version >nul 2>&1
if errorlevel 1 (
  echo   ERROR: Python is not installed.
  echo.
  echo   Download from https://www.python.org/downloads/
  echo   Important: tick "Add Python to PATH" during install.
  echo.
  pause
  exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo   Python: %%v

:: 2. Install dependencies
echo   Installing dependencies...
pip install -r backend\requirements.txt --quiet
if errorlevel 1 (
  echo.
  echo   pip failed. Trying python -m pip...
  python -m pip install -r backend\requirements.txt --quiet
)

echo   Dependencies installed.
echo.
echo   -----------------------------------------
echo   Starting LaunchFolio at http://localhost:5000
echo   Press Ctrl+C to stop.
echo   -----------------------------------------
echo.

:: 3. Start the server
python backend\generate.py --serve
pause
