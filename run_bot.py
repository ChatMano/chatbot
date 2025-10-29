#!/usr/bin/env python3
"""
Script principale per eseguire il bot iPratico automaticamente
"""
import os
import sys
from datetime import datetime
from bot.config_manager import ConfigManager
from bot.auth import AuthManager
from bot.scraper import DashboardScraper
from bot.google_sheets import GoogleSheetsUploader


def main():
    """Esegue il processo completo di download e upload"""

    print("\n" + "="*60)
    print("BOT iPratico - ESECUZIONE AUTOMATICA")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    # Configurazione
    config = ConfigManager('config.json')
    auth = AuthManager()

    # Parametri da variabili d'ambiente o default
    pin = os.getenv('IPRATICO_PIN', '123456')
    locale_selector = os.getenv('IPRATICO_LOCALE_SELECTOR')
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

    if not sheet_id:
        print("❌ ERRORE: GOOGLE_SHEET_ID non configurato!")
        print("   Imposta la variabile d'ambiente GOOGLE_SHEET_ID")
        sys.exit(1)

    # Step 1: Download file da iPratico
    print("\n[STEP 1/2] DOWNLOAD DA iPRATICO")
    print("-" * 60)

    scraper = DashboardScraper(config, auth)
    downloaded_file = None

    try:
        downloaded_file = scraper.run(pin=pin, locale_selector=locale_selector)

        if not downloaded_file:
            print("\n❌ Download fallito!")
            sys.exit(1)

        print(f"\n✓ File scaricato: {downloaded_file}")

    except Exception as e:
        print(f"\n❌ ERRORE durante il download: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 2: Upload su Google Sheets
    print("\n[STEP 2/2] UPLOAD SU GOOGLE SHEETS")
    print("-" * 60)

    uploader = GoogleSheetsUploader()

    try:
        # Autentica
        if not uploader.authenticate_service_account(credentials_file):
            print("\n❌ Autenticazione Google fallita!")
            sys.exit(1)

        # Upload
        success = uploader.write_excel_to_sheet(
            excel_file=downloaded_file,
            sheet_id=sheet_id,
            worksheet_name="Dati iPratico",
            clear_existing=True
        )

        if not success:
            print("\n❌ Upload su Google Sheets fallito!")
            sys.exit(1)

        print("\n" + "="*60)
        print("✓✓✓ PROCESSO COMPLETATO CON SUCCESSO! ✓✓✓")
        print("="*60)
        print(f"\nVisualizza i dati: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

    except Exception as e:
        print(f"\n❌ ERRORE durante l'upload: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
