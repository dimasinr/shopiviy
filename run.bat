@echo off
SETLOCAL

REM Nama folder virtual environment
set VENV_DIR=venv

REM Cek apakah venv sudah ada
if exist %VENV_DIR% (
    echo [INFO] Virtual environment sudah ada.
) else (
    echo [INFO] Membuat virtual environment...
    python -m venv %VENV_DIR%
)

REM Aktifkan virtual environment
call %VENV_DIR%\Scripts\activate

REM Upgrade pip
echo [INFO] Upgrade pip...
python -m pip install --upgrade pip

REM Install requirements jika ada
if exist requirements.txt (
    echo [INFO] Install dependencies dari requirements.txt...
    pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt tidak ditemukan.
)

REM Cek apakah manage.py ada
if exist manage.py (
    echo [INFO] Menjalankan Django server...
    python manage.py runserver
) else (
    echo [ERROR] manage.py tidak ditemukan. Pastikan ini project Django.
)

ENDLOCAL
pause