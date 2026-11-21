@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0preview-scail-sword-candidates.ps1"
if errorlevel 1 (
  echo [FAIL] Review logs\preview-sword-candidates.log
)
pause >nul
