@echo off
setlocal
cd /d "%~dp0"
python -m py_compile src\studio\editorial.py src\studio\workspace.py src\studio\render.py src\studio\voice.py src\studio\web.py src\studio\comfy.py scripts\studio_sovits_worker.py
if errorlevel 1 exit /b 1
python web_ui.py
exit /b %ERRORLEVEL%
