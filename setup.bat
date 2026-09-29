@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher ^(py^) was not found.
  echo Install Python 3.11+ from python.org and run this file again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -m venv .venv
  if errorlevel 1 goto :error
)

echo Installing/updating dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error

if not exist ".env" copy /Y ".env.example" ".env" >nul
if not exist "results" mkdir results
if not exist "sessions" mkdir sessions

echo.
echo Setup complete.
echo Run run.bat to start the program.
pause
exit /b 0

:error
echo.
echo Setup failed. Read the error above.
pause
exit /b 1
