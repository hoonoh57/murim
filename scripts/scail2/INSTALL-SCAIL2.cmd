@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-scail2.ps1"
if errorlevel 1 (
  echo [FAIL] See logs\install-scail2.log
  pause
  exit /b 1
)
