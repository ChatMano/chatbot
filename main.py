#!/usr/bin/env python3
"""
Bot Multi-Tenant per il Download Automatico di File Excel da Dashboard
e Upload su Google Drive

Autore: Claude
Versione: 1.0.0
"""
import os
import sys
import argparse
from bot.config_manager import ConfigManager
from bot.auth import AuthManager
from bot.scraper import DashboardScraper
from bot.google_drive import GoogleDriveUploader


def print_banner():
    """Stampa il banner iniziale"""
    banner = """
    ╔════════════════════════════════════════════════════════════╗
    ║        Bot Download Excel & Upload Google Drive            ║
    ║                    Versione 1.0.0                          ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Funzione principale"""
    # Parse degli argomenti
    parser = argparse.ArgumentParser(
        description='Bot per il download automatico di file Excel e upload su Google Drive'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path al file di configurazione (default: config.json)'
    )
    parser.add_argument(
        '--no-upload',
        action='store_true',
        help='Scarica il file senza caricarlo su Google Drive'
    )
    parser.add_argument(
        '--keep-file',
        action='store_true',
        help='Mantieni il file locale dopo l\'upload su Google Drive'
    )

    args = parser.parse_args()

    # Stampa il banner
    print_banner()

    try:
        # Inizializza i manager
        print("Inizializzazione...")
        config_manager = ConfigManager(args.config)
        auth_manager = AuthManager()

        # Crea lo scraper
        scraper = DashboardScraper(config_manager, auth_manager)

        # Esegui il download
        print("\n" + "="*60)
        print("FASE 1: DOWNLOAD FILE DALLA DASHBOARD")
        print("="*60 + "\n")

        downloaded_file = scraper.run()

        if not downloaded_file:
            print("\n❌ Errore: Download del file fallito")
            sys.exit(1)

        print(f"\n✓ File scaricato con successo: {downloaded_file}")

        # Upload su Google Drive (se non disabilitato)
        if not args.no_upload:
            print("\n" + "="*60)
            print("FASE 2: UPLOAD SU GOOGLE DRIVE")
            print("="*60 + "\n")

            uploader = GoogleDriveUploader(config_manager)

            if uploader.authenticate():
                file_id = uploader.upload_to_folder(downloaded_file)

                if file_id:
                    print(f"\n✓ File caricato con successo su Google Drive (ID: {file_id})")

                    # Elimina il file locale se non richiesto di mantenerlo
                    if not args.keep_file:
                        try:
                            os.remove(downloaded_file)
                            print(f"✓ File locale eliminato: {downloaded_file}")
                        except Exception as e:
                            print(f"⚠ Avviso: Impossibile eliminare il file locale: {e}")
                else:
                    print("\n❌ Errore: Upload su Google Drive fallito")
                    sys.exit(1)
            else:
                print("\n❌ Errore: Autenticazione Google Drive fallita")
                sys.exit(1)
        else:
            print("\n⚠ Upload su Google Drive saltato (--no-upload)")

        # Successo
        print("\n" + "="*60)
        print("✓ PROCESSO COMPLETATO CON SUCCESSO")
        print("="*60 + "\n")

    except FileNotFoundError as e:
        print(f"\n❌ Errore: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠ Processo interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore imprevisto: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
