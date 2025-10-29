"""
Modulo per scrivere dati su Google Sheets
"""
import os
from datetime import datetime
from typing import Optional, List
import gspread
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd


# Scopes necessari per l'accesso a Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]


class GoogleSheetsUploader:
    """Gestisce la scrittura di dati su Google Sheets"""

    def __init__(self):
        """Inizializza l'uploader di Google Sheets"""
        self.client = None
        self.credentials = None

    def authenticate_service_account(self, credentials_file: str = 'credentials.json') -> bool:
        """
        Autentica usando un Service Account (consigliato per automazione)

        Args:
            credentials_file: Path al file JSON del service account

        Returns:
            True se l'autenticazione ha successo, False altrimenti
        """
        try:
            if not os.path.exists(credentials_file):
                print(f"File {credentials_file} non trovato")
                return False

            credentials = Credentials.from_service_account_file(
                credentials_file,
                scopes=SCOPES
            )

            self.client = gspread.authorize(credentials)
            print("Autenticazione Service Account completata")
            return True

        except Exception as e:
            print(f"Errore durante l'autenticazione Service Account: {e}")
            return False

    def authenticate_oauth(self) -> bool:
        """
        Autentica usando OAuth2 (per uso locale/interattivo)

        Returns:
            True se l'autenticazione ha successo, False altrimenti
        """
        try:
            # Il file token.json memorizza i token di accesso e refresh dell'utente
            if os.path.exists('token.json'):
                self.credentials = UserCredentials.from_authorized_user_file('token.json', SCOPES)

            # Se non ci sono credenziali valide disponibili, chiedi all'utente di effettuare il login
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    print("Aggiornamento credenziali Google...")
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists('credentials.json'):
                        print("\nERRORE: File credentials.json non trovato!")
                        print("Per utilizzare Google Sheets API con OAuth:")
                        print("1. Vai su https://console.cloud.google.com/")
                        print("2. Crea un nuovo progetto o seleziona uno esistente")
                        print("3. Abilita Google Sheets API")
                        print("4. Crea credenziali OAuth 2.0 per applicazione desktop")
                        print("5. Scarica il file JSON e salvalo come 'credentials.json'")
                        return False

                    print("Autenticazione con Google...")
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    self.credentials = flow.run_local_server(port=0)

                # Salva le credenziali per il prossimo utilizzo
                with open('token.json', 'w') as token:
                    token.write(self.credentials.to_json())

            # Crea il client gspread
            self.client = gspread.authorize(self.credentials)
            print("Autenticazione OAuth completata")
            return True

        except Exception as e:
            print(f"Errore durante l'autenticazione OAuth: {e}")
            return False

    def authenticate(self, use_service_account: bool = True) -> bool:
        """
        Autentica con il metodo specificato

        Args:
            use_service_account: Se True usa service account, altrimenti OAuth

        Returns:
            True se l'autenticazione ha successo
        """
        if use_service_account:
            return self.authenticate_service_account()
        else:
            return self.authenticate_oauth()

    def write_excel_to_sheet(
        self,
        excel_file: str,
        sheet_id: str,
        worksheet_name: str = None,
        clear_existing: bool = True
    ) -> bool:
        """
        Scrive i dati di un file Excel su Google Sheets

        Args:
            excel_file: Path al file Excel
            sheet_id: ID del Google Sheet
            worksheet_name: Nome del foglio (se None, usa il primo)
            clear_existing: Se True, cancella i dati esistenti prima di scrivere

        Returns:
            True se la scrittura ha successo, False altrimenti
        """
        try:
            if not self.client:
                print("Client non autenticato")
                return False

            if not os.path.exists(excel_file):
                print(f"File Excel {excel_file} non trovato")
                return False

            # Leggi il file Excel
            print(f"Lettura file Excel: {excel_file}")

            # Determina l'engine corretto in base all'estensione
            file_ext = os.path.splitext(excel_file)[1].lower()
            if file_ext == '.xls':
                # Vecchio formato Excel (97-2003) richiede xlrd
                df = pd.read_excel(excel_file, sheet_name=0, engine='xlrd')
            elif file_ext == '.xlsx':
                # Nuovo formato Excel richiede openpyxl
                df = pd.read_excel(excel_file, sheet_name=0, engine='openpyxl')
            else:
                # Prova senza specificare l'engine
                df = pd.read_excel(excel_file, sheet_name=0)

            # Apri il Google Sheet
            print(f"Apertura Google Sheet: {sheet_id}")
            spreadsheet = self.client.open_by_key(sheet_id)

            # Seleziona o crea il worksheet
            if worksheet_name:
                try:
                    worksheet = spreadsheet.worksheet(worksheet_name)
                except gspread.exceptions.WorksheetNotFound:
                    print(f"Foglio '{worksheet_name}' non trovato, lo creo...")
                    worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=26)
            else:
                worksheet = spreadsheet.sheet1

            # Cancella dati esistenti se richiesto
            if clear_existing:
                print("Cancellazione dati esistenti...")
                worksheet.clear()

            # Prepara i dati per Google Sheets
            # Includi l'header
            data = [df.columns.tolist()] + df.values.tolist()

            # Converti eventuali NaN in stringhe vuote
            data = [['' if pd.isna(cell) else cell for cell in row] for row in data]

            # Scrivi i dati
            print(f"Scrittura di {len(data)} righe su Google Sheets...")
            worksheet.update('A1', data)

            # Aggiungi un timestamp nella prima riga
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note = f'Aggiornato: {timestamp}'
            # Scrivi il timestamp in una cella separata (ad esempio ultima colonna)
            last_col = len(data[0]) + 1 if data else 1
            worksheet.update_acell(f'{chr(64 + last_col)}1', note)

            print(f"✓ Dati scritti con successo su Google Sheets!")
            print(f"  Righe: {len(data)}")
            print(f"  Colonne: {len(data[0]) if data else 0}")

            return True

        except Exception as e:
            print(f"Errore durante la scrittura su Google Sheets: {e}")
            import traceback
            traceback.print_exc()
            return False
