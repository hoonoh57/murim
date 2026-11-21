@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-scail2.ps1"
if errorlevel 1 (
  echo [FAIL] SCAIL-2 installation stopped. See logs\install-scail2.log
) else (
  echo [READY] SCAIL-2 setup finished.
)
pause
