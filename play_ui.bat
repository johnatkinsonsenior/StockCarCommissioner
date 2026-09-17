@echo off
setlocal
cd /d "%~dp0"

set "PYLAUNCH="
where py >nul 2>&1
if %ERRORLEVEL%==0 set "PYLAUNCH=py -3"
if not defined PYLAUNCH (
  where python >nul 2>&1
  if %ERRORLEVEL%==0 set "PYLAUNCH=python"
)

if not defined PYLAUNCH (
  echo.
  echo Python 3.10+ is required for the commissioner office.
  echo Install it from https://www.python.org/downloads/
  echo Check "Add python.exe to PATH" during setup, then double-click play_ui.bat again.
  echo.
  echo You also need Godot 4.4: https://godotengine.org/download
  echo Git is not required.
  echo.
  pause
  exit /b 1
)

echo Starting the commissioner office...
%PYLAUNCH% prototype\run_ui.py %*
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
  echo.
  echo The office window did not stay open.
  echo Need Python 3.10+ and Godot 4.4.
  echo If Godot is installed, set GODOT_BIN to the .exe, for example:
  echo   set GODOT_BIN=%USERPROFILE%\Downloads\Godot_v4.4-stable_win64.exe
  echo then run play_ui.bat again.
  echo.
  echo Terminal career without Godot: double-click play.bat
  echo.
  pause
)
exit /b %ERR%
