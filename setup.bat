@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher "py" was not found. Install Python 3.12 from python.org and enable the launcher.
    pause
    exit /b 1
)

py -3.12 --version
if errorlevel 1 (
    echo Python 3.12 was not found. Install Python 3.12 first.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    py -3.12 -m venv .venv
    if errorlevel 1 goto :error
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 goto :error
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo Setup complete. Start the assistant with run.bat
pause
exit /b 0

:error
echo.
echo Setup failed. Read the error above.
pause
exit /b 1
