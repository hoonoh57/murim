@echo off
setlocal
set "REPO_DIR=%~dp0"
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%REPO_DIR%scripts\windows-sync-test.ps1" -Workspace "%REPO_DIR%" %*
exit /b %ERRORLEVEL%
