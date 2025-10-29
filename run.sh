#!/bin/bash
# Script di avvio rapido per il bot

# Attiva il virtual environment se esiste
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Esegui il bot
python main.py "$@"
