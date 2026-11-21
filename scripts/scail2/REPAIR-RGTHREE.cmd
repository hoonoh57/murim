@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0repair-rgthree.ps1"
if errorlevel 1 (
  echo [FAIL] See logs\repair-rgthree.log
  pause
  exit /b 1
)
