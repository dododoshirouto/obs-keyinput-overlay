: _build.bat
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
  --icon %ICON% ^
  --name %NAME% ^
  --windowed ^
  --noconsole ^
  %ENTRYPOINT%

echo [INFO] Copying config files and public assets...
xcopy config.json dist\ /Y >nul
xcopy keymaps.json dist\ /Y >nul
xcopy /E /I /Y public dist\public >nul

echo [INFO] Build complete. Executable is in /dist/%NAME%.exe
pause
