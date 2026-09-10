@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 prototype\run_season.py %*
  goto :eof
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
  python prototype\run_season.py %*
  goto :eof
)

echo Python 3.10+ is required to play Stock Car Commissioner.
echo Install it from https://www.python.org/downloads/ then double-click play.bat again.
echo Git is not required.
pause
