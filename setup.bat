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
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r backend\requirements.txt --quiet
if errorlevel 1 (
  echo.
  echo   pip failed. Trying python -m pip...
  python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r backend\requirements.txt --quiet
)

echo   Dependencies installed.

:: 3. Optional: Ollama (free local AI — no API key needed)
echo.
echo   -----------------------------------------
echo   Optional: Ollama (free local AI, no API key needed)
echo.
where ollama >nul 2>&1
if %errorlevel%==0 (
  echo   Ollama is already installed and ready to use.
) else (
  echo   Ollama lets you run AI parsing 100%% locally with no API key.
  echo.
  echo   To install on Windows:
  echo     1. Go to https://ollama.com/download
  echo     2. Download and run the Windows installer
  echo     3. Open a new Command Prompt and run: ollama pull llama3.2
  echo.
  echo   Then rerun this setup — it will detect Ollama automatically.
)

echo.
echo   -----------------------------------------
echo   Starting LaunchFolio at http://localhost:5000
echo   Press Ctrl+C to stop.
echo   -----------------------------------------
echo.

:: 4. Start the server
python backend\generate.py --serve
pause
