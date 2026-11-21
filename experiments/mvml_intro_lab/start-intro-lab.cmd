@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul || (echo [FAIL] Python 3.9+ is not on PATH & exit /b 1)
python -c "import sys; assert sys.version_info >= (3,9); import PIL" || (echo [FAIL] Python 3.9+ and Pillow required & exit /b 1)
where ffmpeg >nul 2>nul || (echo [FAIL] FFmpeg not on PATH & exit /b 1)
where ffprobe >nul 2>nul || (echo [FAIL] ffprobe not on PATH & exit /b 1)
python intro_lab.py --compile >nul || (echo [FAIL] M-VML asset or reference validation failed & exit /b 1)
echo Open http://127.0.0.1:8769 in your browser after the server starts.
python intro_lab.py
endlocal
