@echo off
REM Double-click to import a pro forma into the IC Go/No-Go dashboard.
REM Or drag a spreadsheet onto this icon to import that file directly.
cd /d "%~dp0\.."
python -m deal_agent.ic.desktop %*
if errorlevel 1 pause
