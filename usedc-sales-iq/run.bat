@echo off
REM USEDC Sales IQ — double-click launcher for Windows.
REM Installs dependencies on first run, then starts the app in your browser.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo  Python is not installed on this computer.
    echo  1. Go to  https://www.python.org/downloads/  and download Python.
    echo  2. On the FIRST screen of the installer, tick "Add python.exe to PATH".
    echo  3. Finish the install, then double-click this file again.
    echo.
    pause
    exit /b 1
)

echo Installing dependencies (first run only, 1-2 minutes)...
python -m pip install --quiet -r requirements.txt

echo Starting USEDC Sales IQ... your browser will open automatically.
python -m streamlit run app.py

pause
