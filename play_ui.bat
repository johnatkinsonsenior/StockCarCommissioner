@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 prototype\run_ui.py %*
  goto :eof
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
  python prototype\run_ui.py %*
  goto :eof
)

echo Python 3.10+ is required for the commissioner office.
echo Install it from https://www.python.org/downloads/ then double-click play_ui.bat again.
echo Optional: install Godot 4.4 and put it on PATH, or set GODOT_BIN.
echo Git is not required.
pause
