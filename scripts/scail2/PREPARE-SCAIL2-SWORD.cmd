@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0prepare-scail2-sword.ps1"
if errorlevel 1 (
 echo [FAIL] See logs\prepare-scail2-sword.log
 pause
 exit /b 1
)
