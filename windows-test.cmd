@echo off
setlocal
rem The PowerShell script resolves the workspace from its own PSScriptRoot.
rem Do not pass %%~dp0 as a quoted -Workspace argument: it ends in a backslash.
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0scripts\windows-sync-test.ps1" %*
exit /b %ERRORLEVEL%
