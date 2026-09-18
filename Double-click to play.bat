@echo off
setlocal
cd /d "%~dp0"
title Stock Car Commissioner
call "%~dp0launch_office.cmd" %*
exit /b %ERRORLEVEL%
