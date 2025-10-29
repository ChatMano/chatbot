@echo off
REM Script di avvio rapido per il bot (Windows)

REM Attiva il virtual environment se esiste
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Esegui il bot
python main.py %*
