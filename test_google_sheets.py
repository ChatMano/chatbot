#!/usr/bin/env python3
"""
Script di test per verificare l'upload su Google Sheets
"""
import os
from bot.google_sheets import GoogleSheetsUploader

def test_google_sheets():
    """Test dell'upload su Google Sheets"""

    print("\n" + "="*60)
    print("TEST GOOGLE SHEETS UPLOAD")
    print("="*60 + "\n")

    # ID del tuo Google Sheet
    SHEET_ID = "1JDDcYoHkG5LTbB8w2tyMr8CcFc7l4ITsf9eYSVLwSNs"

    # Verifica che esista credentials.json
    if not os.path.exists('credentials.json'):
        print("❌ ERRORE: File credentials.json non trovato!")
        print("\nDevi copiare il file credentials.json nella root del progetto.")
        print("Il file dovrebbe trovarsi nella cartella Downloads.")
        print("\nPer copiarlo:")
        print("  Windows: copy Downloads\\credentials.json .")
        print("  Mac/Linux: cp ~/Downloads/credentials.json .")
        return

    print("✓ File credentials.json trovato\n")

    # Verifica che esista un file Excel di test
    # Cerca nella cartella Downloads dell'utente
    downloads_path = os.path.expanduser("~/Downloads")
    excel_files = []

    if os.path.exists(downloads_path):
        for file in os.listdir(downloads_path):
            if file.endswith(('.xlsx', '.xls')):
                excel_files.append(os.path.join(downloads_path, file))

    if not excel_files:
        print("❌ ERRORE: Nessun file Excel trovato nella cartella Downloads!")
        print("\nEsegui prima test_login.py per scaricare un file Excel.")
        return

    # Usa il file Excel più recente
    excel_file = max(excel_files, key=os.path.getmtime)
    print(f"📄 File Excel da caricare: {os.path.basename(excel_file)}\n")

    # Inizializza l'uploader
    uploader = GoogleSheetsUploader()

    # Autentica con Service Account
    print("Autenticazione con Google Sheets API...")
    if not uploader.authenticate_service_account():
        print("❌ Autenticazione fallita!")
        return

    print("✓ Autenticazione riuscita\n")

    # Carica i dati su Google Sheets
    print(f"Caricamento dati su Google Sheet: {SHEET_ID}")
    print("Worksheet: 'Dati iPratico'\n")

    if uploader.write_excel_to_sheet(
        excel_file=excel_file,
        sheet_id=SHEET_ID,
        worksheet_name="Dati iPratico",
        clear_existing=True
    ):
        print("\n" + "="*60)
        print("✓✓✓ UPLOAD COMPLETATO CON SUCCESSO! ✓✓✓")
        print("="*60)
        print(f"\nApri il foglio per vedere i dati:")
        print(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
    else:
        print("\n❌ Upload fallito!")

if __name__ == "__main__":
    test_google_sheets()
