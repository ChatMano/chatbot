#!/usr/bin/env python3
"""
Script principale per eseguire il bot iPratico automaticamente
Legge i locali configurati dal database e esegue il download per ognuno
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Aggiungi il path del backend
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from backend.models import db, Locale, LocaleLog
from backend.crypto import CryptoManager
from bot.config_manager import ConfigManager
from bot.scraper import DashboardScraper
from bot.google_sheets import GoogleSheetsUploader


def setup_database():
    """Setup del database SQLite"""
    from flask import Flask

    app = Flask(__name__)

    # Percorso assoluto al database
    db_path = Path(__file__).parent / 'data' / 'locali.db'
    db_path.parent.mkdir(exist_ok=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app


def process_locale(locale, config, crypto, credentials_file):
    """Processa un singolo locale"""

    print("\n" + "="*60)
    print(f"LOCALE: {locale.nome}")
    print("="*60)

    log_entry = LocaleLog(
        locale_id=locale.id,
        eseguito_at=datetime.utcnow(),
        successo=False
    )

    try:
        # Decifra le credenziali
        password = crypto.decrypt(locale.password_encrypted)
        pin = crypto.decrypt(locale.pin_encrypted) if locale.pin_encrypted else '123456'

        # Crea AuthManager custom per questo locale
        class LocaleAuthManager:
            def __init__(self, username, password):
                self.username = username
                self.password = password

            def get_credentials(self):
                return self.username, self.password

        auth = LocaleAuthManager(locale.username, password)

        # Step 1: Download
        print(f"\n[STEP 1/2] DOWNLOAD DA iPRATICO")
        print(f"Username: {locale.username}")
        print(f"Locale Selector: {locale.locale_selector or 'Default'}")
        print("-" * 60)

        scraper = DashboardScraper(config, auth)
        downloaded_file = scraper.run(pin=pin, locale_selector=locale.locale_selector)

        if not downloaded_file:
            log_entry.messaggio = "Download fallito"
            return log_entry

        log_entry.file_scaricato = downloaded_file
        print(f"\n✓ File scaricato: {downloaded_file}")

        # Step 2: Upload su Google Sheets
        print(f"\n[STEP 2/2] UPLOAD SU GOOGLE SHEETS")
        print(f"Sheet ID: {locale.google_sheet_id}")
        print("-" * 60)

        uploader = GoogleSheetsUploader()

        if not uploader.authenticate_service_account(credentials_file):
            log_entry.messaggio = "Autenticazione Google fallita"
            return log_entry

        success = uploader.write_excel_to_sheet(
            excel_file=downloaded_file,
            sheet_id=locale.google_sheet_id,
            worksheet_name="Dati iPratico",
            clear_existing=True
        )

        if not success:
            log_entry.messaggio = "Upload Google Sheets fallito"
            return log_entry

        log_entry.successo = True
        log_entry.sheet_aggiornato = True
        log_entry.messaggio = "Completato con successo"

        print("\n✓✓✓ LOCALE COMPLETATO CON SUCCESSO! ✓✓✓")

        return log_entry

    except Exception as e:
        log_entry.messaggio = f"Errore: {str(e)}"
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return log_entry


def main():
    """Esegue il processo completo per tutti i locali attivi"""

    print("\n" + "="*60)
    print("BOT iPratico - ESECUZIONE AUTOMATICA MULTI-LOCALE")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    # Setup
    app = setup_database()
    config = ConfigManager('config.json')
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

    # Verifica che esista il file credentials
    if not os.path.exists(credentials_file):
        print(f"❌ ERRORE: File {credentials_file} non trovato!")
        sys.exit(1)

    # Ottieni la chiave di cifratura
    encryption_key = os.getenv('ENCRYPTION_KEY')
    if not encryption_key:
        print("❌ ERRORE: ENCRYPTION_KEY non configurata!")
        print("   Imposta la variabile d'ambiente ENCRYPTION_KEY")
        sys.exit(1)

    crypto = CryptoManager(encryption_key)

    # Leggi i locali attivi dal database
    with app.app_context():
        locali_attivi = Locale.query.filter_by(attivo=True).all()

        if not locali_attivi:
            print("⚠ Nessun locale attivo trovato nel database")
            sys.exit(0)

        print(f"✓ Trovati {len(locali_attivi)} locali attivi da processare\n")

        # Processa ogni locale
        risultati = []
        for idx, locale in enumerate(locali_attivi, 1):
            print(f"\n{'='*60}")
            print(f"LOCALE {idx}/{len(locali_attivi)}")
            print(f"{'='*60}")

            log_entry = process_locale(locale, config, crypto, credentials_file)
            db.session.add(log_entry)
            db.session.commit()

            risultati.append((locale.nome, log_entry.successo))

        # Riepilogo finale
        print("\n\n" + "="*60)
        print("RIEPILOGO ESECUZIONE")
        print("="*60)

        successi = sum(1 for _, success in risultati if success)
        fallimenti = len(risultati) - successi

        for nome, success in risultati:
            status = "✓" if success else "✗"
            print(f"{status} {nome}")

        print(f"\nTotale: {successi} successi, {fallimenti} fallimenti")
        print("="*60 + "\n")

        # Exit code
        sys.exit(0 if fallimenti == 0 else 1)


if __name__ == "__main__":
    main()
