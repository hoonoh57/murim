@echo off
setlocal
cd /d "%~dp0"
python -m unittest -q tests.test_comfyui_proof
if errorlevel 1 (
    echo [FAIL] ComfyUI proof unit tests
    exit /b 1
)
python "%~dp0scripts\prove_comfyui.py" %*
exit /b %ERRORLEVEL%
