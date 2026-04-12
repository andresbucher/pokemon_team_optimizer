@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
  echo ERROR: Expected Python virtual environment at .venv\Scripts\python.exe
  echo Create it first, then install dependencies from requirements.txt.
  exit /b 1
)

REM Build a Windows executable with bundled data assets.
"%PYTHON_EXE%" -m PyInstaller ^
  --noconfirm ^
  --windowed ^
  --name PokemonTeamOptimizer ^
  --add-data "data;data" ^
  Main.py

if errorlevel 1 (
  echo.
  echo Build failed.
  exit /b 1
)

echo.
echo Build complete. Check the dist\PokemonTeamOptimizer folder.
endlocal
