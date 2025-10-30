#!/usr/bin/env python3
"""
Script principale per eseguire il bot iPratico automaticamente
Legge i locali configurati dal database e esegue il download per ognuno
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pytz

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


def should_run_locale(locale, app) -> bool:
    """
    Verifica se un locale deve essere eseguito in base all'orario impostato o al flag esegui_ora

    Args:
        locale: Oggetto Locale dal database
        app: Flask app context

    Returns:
        True se il locale deve essere eseguito ora, False altrimenti
    """
    # Se è impostato il flag esegui_ora, esegui sempre
    if locale.esegui_ora:
        print(f"  🚀 Esecuzione manuale richiesta!")
        return True

    # Ottieni l'ora corrente italiana
    italy_tz = pytz.timezone('Europe/Rome')
    now_italy = datetime.now(italy_tz)
    current_hour = now_italy.strftime('%H:%M')

    # Controlla se l'orario corrisponde (con tolleranza di 1 ora)
    locale_time = locale.orario_esecuzione  # Formato: "03:00"
    locale_hour = int(locale_time.split(':')[0])
    current_hour_int = now_italy.hour

    # Il locale deve girare in questa fascia oraria?
    if locale_hour != current_hour_int:
        return False

    # Verifica se è già stato eseguito oggi con successo
    with app.app_context():
        today_start = now_italy.replace(hour=0, minute=0, second=0, microsecond=0)
        last_log = LocaleLog.query.filter(
            LocaleLog.locale_id == locale.id,
            LocaleLog.eseguito_at >= today_start.replace(tzinfo=None),
            LocaleLog.successo == True
        ).first()

        if last_log:
            print(f"  ⏭️  Locale già eseguito oggi alle {last_log.eseguito_at.strftime('%H:%M')}")
            return False

    return True


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

    # Ottieni l'ora corrente italiana
    italy_tz = pytz.timezone('Europe/Rome')
    now_italy = datetime.now(italy_tz)

    print("\n" + "="*60)
    print("BOT iPratico - ESECUZIONE AUTOMATICA MULTI-LOCALE")
    print(f"Data: {now_italy.strftime('%Y-%m-%d %H:%M:%S')} (ora italiana)")
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

    # Controlla se è stata richiesta l'esecuzione di un locale specifico
    locale_id_richiesto = os.getenv('LOCALE_ID')

    # Leggi i locali attivi dal database
    with app.app_context():
        if locale_id_richiesto:
            # Esecuzione manuale di un locale specifico via API GitHub
            try:
                locale_id = int(locale_id_richiesto)
                locale = Locale.query.get(locale_id)
                if not locale:
                    print(f"❌ ERRORE: Locale con ID {locale_id} non trovato!")
                    sys.exit(1)
                if not locale.attivo:
                    print(f"❌ ERRORE: Locale {locale.nome} non è attivo!")
                    sys.exit(1)

                print(f"🚀 ESECUZIONE MANUALE RICHIESTA")
                print(f"   Locale: {locale.nome}")
                print(f"   Richiesta da: GitHub Actions API\n")
                locali_attivi = [locale]
            except ValueError:
                print(f"❌ ERRORE: LOCALE_ID deve essere un numero intero!")
                sys.exit(1)
        else:
            # Esecuzione automatica programmata: processa tutti i locali attivi
            locali_attivi = Locale.query.filter_by(attivo=True).all()

        if not locali_attivi:
            print("⚠ Nessun locale attivo trovato nel database")
            sys.exit(0)

        print(f"✓ Trovati {len(locali_attivi)} locali attivi nel database\n")

        # Filtra i locali che devono essere eseguiti ora
        if locale_id_richiesto:
            # Esecuzione manuale: esegui subito il locale richiesto
            locali_da_processare = locali_attivi
        else:
            # Esecuzione automatica: filtra in base all'orario
            locali_da_processare = []
            for locale in locali_attivi:
                print(f"🔍 Controllo {locale.nome} (orario: {locale.orario_esecuzione})...")
                if should_run_locale(locale, app):
                    print(f"  ✅ Da processare ora")
                    locali_da_processare.append(locale)
                else:
                    if locale.orario_esecuzione.split(':')[0] != str(now_italy.hour).zfill(2):
                        print(f"  ⏭️  Orario non corrispondente (atteso: {locale.orario_esecuzione}, corrente: {now_italy.strftime('%H:%M')})")

            if not locali_da_processare:
                print(f"\n⏰ Nessun locale da processare alle {now_italy.strftime('%H:%M')}")
                print("   I locali verranno eseguiti ai loro orari programmati")
                sys.exit(0)

        print(f"\n{'='*60}")
        print(f"✓ {len(locali_da_processare)} locale/i da processare alle {now_italy.strftime('%H:%M')}")
        print(f"{'='*60}\n")

        # Processa ogni locale
        risultati = []
        for idx, locale in enumerate(locali_da_processare, 1):
            print(f"\n{'='*60}")
            print(f"LOCALE {idx}/{len(locali_da_processare)}")
            print(f"{'='*60}")

            log_entry = process_locale(locale, config, crypto, credentials_file)
            db.session.add(log_entry)

            # Resetta il flag esegui_ora dopo l'esecuzione
            if locale.esegui_ora:
                locale.esegui_ora = False
                print(f"  ✓ Flag esecuzione manuale resettato")

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
