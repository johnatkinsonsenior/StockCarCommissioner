@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title Stock Car Commissioner
color 0F
echo.
echo  ============================================================
echo   STOCK CAR COMMISSIONER
echo   Commissioner office  -  double-click to play
echo  ============================================================
echo.
echo  You run the league. You do not drive. You do not own a team.
echo.

set "ROOT=%~dp0"
if not exist "%ROOT%prototype\run_ui.py" (
  echo.
  echo This launcher has to stay inside the Stock Car Commissioner folder.
  echo Unzip the whole folder, then double-click StockCarCommissioner.exe.
  echo.
  pause
  exit /b 1
)
set "PYHOME=%ROOT%tools\python"
set "GODOT_HOME=%ROOT%tools\godot"
set "GODOT_EXE=%GODOT_HOME%\Godot_v4.4-stable_win64.exe"
set "PY_ZIP=%ROOT%tools\python-embed.zip"
set "PY_URL=https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip"
set "PYLAUNCH="

if exist "%GODOT_EXE%" set "GODOT_BIN=%GODOT_EXE%"

call :resolve_python
if not defined PYLAUNCH (
  call :install_python
)
if not defined PYLAUNCH goto :fail_python

echo Starting the commissioner office...
echo If tools\python and tools\godot are missing, first launch downloads them once.
echo.
if /i "%PYLAUNCH%"=="py -3" (
  py -3 "%ROOT%prototype\run_ui.py" %*
) else (
  "%PYLAUNCH%" "%ROOT%prototype\run_ui.py" %*
)
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" goto :fail_launch
echo.
echo Office closed.
goto :eof

:resolve_python
set "PYLAUNCH="
if exist "%PYHOME%\python.exe" (
  set "PYLAUNCH=%PYHOME%\python.exe"
  goto :eof
)
where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
  if not errorlevel 1 (
    set "PYLAUNCH=py -3"
    goto :eof
  )
)
for /f "delims=" %%P in ('where python 2^>nul') do (
  echo %%P | findstr /i /c:"WindowsApps" >nul
  if errorlevel 1 (
    "%%P" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if not errorlevel 1 (
      set "PYLAUNCH=%%P"
      goto :eof
    )
  )
)
goto :eof

:install_python
echo Python was not found ^(the Microsoft Store shortcut does not count^).
echo Downloading a private Python 3.12 into tools\python. One time.
echo.
mkdir "%PYHOME%" >nul 2>&1
call :download "%PY_URL%" "%PY_ZIP%"
if not exist "%PY_ZIP%" goto :eof
tar -xf "%PY_ZIP%" -C "%PYHOME%" 2>nul
if not exist "%PYHOME%\python.exe" (
  powershell -NoProfile -Command "Expand-Archive -LiteralPath '%PY_ZIP%' -DestinationPath '%PYHOME%' -Force" >nul 2>&1
)
if not exist "%PYHOME%\python.exe" goto :eof
del /f /q "%PY_ZIP%" >nul 2>&1
"%PYHOME%\python.exe" "%ROOT%prototype\enable_embed_python.py" "%PYHOME%"
set "PYLAUNCH=%PYHOME%\python.exe"
echo Python is ready.
echo.
goto :eof

:download
set "DL_URL=%~1"
set "DL_OUT=%~2"
if exist "%DL_OUT%" del /f /q "%DL_OUT%" >nul 2>&1
curl.exe -L --retry 3 --retry-delay 2 -o "%DL_OUT%" "%DL_URL%" 2>nul
if exist "%DL_OUT%" goto :eof
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '%DL_URL%' -OutFile '%DL_OUT%' } catch { exit 1 }"
goto :eof

:fail_python
echo.
echo Could not start. This launcher installs its own Python into tools\python
echo if the Microsoft Store python.exe is the only one on PATH.
echo Need an internet connection the first time, or install Python 3.10+ from
echo https://www.python.org/downloads/ and check "Add python.exe to PATH".
echo.
pause
exit /b 1

:fail_launch
echo.
echo The office window did not stay open.
echo First launch needs internet once so Godot 4.4 can download into tools\godot.
echo If a firewall blocked it, install Godot 4.4 from https://godotengine.org/download
echo and double-click this file again.
echo.
pause
exit /b %ERR%
