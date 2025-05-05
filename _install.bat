: _install.bat for obs-keyinput-overlay
@echo off
setlocal

: check python
python --version >nul
if not %errorlevel%==0 (
    echo python not found
    goto :eof
)

: check venv
if not exist venv\Scripts (
    python -m venv venv
)

: install modules
venv\Scripts\pip install -r requirements.txt

:eof
endlocal