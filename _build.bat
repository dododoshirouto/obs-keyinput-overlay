@echo off
setlocal

REM ===== パスと設定 =====
set PYTHON=venv\Scripts\python.exe
set ENTRYPOINT=server.py
set ICON=public\tray.png
set NAME="OBS-KeyInput-Overlay"

REM ===== ビルド開始 =====
echo [INFO] Building executable...
%PYTHON% -m pip install --upgrade pyinstaller
%PYTHON% -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --icon %ICON% ^
  --name %NAME% ^
  %ENTRYPOINT%

echo [INFO] Build complete. Executable is in /dist/%NAME%.exe
pause
