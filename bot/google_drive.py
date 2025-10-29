"""
Modulo per l'upload di file su Google Drive
"""
import os
from typing import Optional
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from .config_manager import ConfigManager


# Scopes necessari per l'accesso a Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveUploader:
    """Gestisce l'upload di file su Google Drive"""

    def __init__(self, config_manager: ConfigManager):
        """
        Inizializza l'uploader di Google Drive

        Args:
            config_manager: Gestore della configurazione
        """
        self.config = config_manager
        self.service = None
        self.credentials = None

    def authenticate(self) -> bool:
        """
        Autentica l'utente con Google Drive usando OAuth2

        Returns:
            True se l'autenticazione ha successo, False altrimenti
        """
        try:
            # Il file token.json memorizza i token di accesso e refresh dell'utente
            if os.path.exists('token.json'):
                self.credentials = Credentials.from_authorized_user_file('token.json', SCOPES)

            # Se non ci sono credenziali valide disponibili, chiedi all'utente di effettuare il login
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    print("Aggiornamento credenziali Google Drive...")
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists('credentials.json'):
                        print("\nERRORE: File credentials.json non trovato!")
                        print("Per utilizzare Google Drive API:")
                        print("1. Vai su https://console.cloud.google.com/")
                        print("2. Crea un nuovo progetto o seleziona uno esistente")
                        print("3. Abilita Google Drive API")
                        print("4. Crea credenziali OAuth 2.0 per applicazione desktop")
                        print("5. Scarica il file JSON e salvalo come 'credentials.json'")
                        return False

                    print("Autenticazione con Google Drive...")
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    self.credentials = flow.run_local_server(port=0)

                # Salva le credenziali per il prossimo utilizzo
                with open('token.json', 'w') as token:
                    token.write(self.credentials.to_json())

            # Crea il servizio Google Drive
            self.service = build('drive', 'v3', credentials=self.credentials)
            print("Autenticazione Google Drive completata")
            return True

        except Exception as e:
            print(f"Errore durante l'autenticazione Google Drive: {e}")
            return False

    def find_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """
        Trova o crea una cartella in Google Drive

        Args:
            folder_name: Nome della cartella
            parent_id: ID della cartella parent (opzionale)

        Returns:
            ID della cartella se trovata/creata, None altrimenti
        """
        try:
            # Cerca la cartella esistente
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            files = results.get('files', [])

            if files:
                print(f"Cartella '{folder_name}' trovata")
                return files[0]['id']
            else:
                # Crea la cartella
                print(f"Creazione cartella '{folder_name}'...")
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                if parent_id:
                    file_metadata['parents'] = [parent_id]

                folder = self.service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()

                print(f"Cartella '{folder_name}' creata con ID: {folder.get('id')}")
                return folder.get('id')

        except HttpError as error:
            print(f"Errore durante la gestione della cartella: {error}")
            return None

    def upload_file(self, file_path: str, folder_id: Optional[str] = None) -> Optional[str]:
        """
        Carica un file su Google Drive

        Args:
            file_path: Path del file da caricare
            folder_id: ID della cartella di destinazione (opzionale)

        Returns:
            ID del file caricato se il caricamento ha successo, None altrimenti
        """
        try:
            if not os.path.exists(file_path):
                print(f"Errore: File {file_path} non trovato")
                return None

            # Ottieni il nome del file e aggiungi un timestamp
            original_filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            drive_config = self.config.get_google_drive_config()
            file_prefix = drive_config.get('file_prefix', 'report_')
            filename = f"{file_prefix}{timestamp}_{original_filename}"

            # Metadata del file
            file_metadata = {'name': filename}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            # Determina il MIME type
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            if file_path.endswith('.xls'):
                mime_type = 'application/vnd.ms-excel'

            print(f"Caricamento file '{filename}' su Google Drive...")
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            file_id = file.get('id')
            web_link = file.get('webViewLink')

            print(f"File caricato con successo!")
            print(f"ID: {file_id}")
            print(f"Link: {web_link}")

            return file_id

        except HttpError as error:
            print(f"Errore durante l'upload del file: {error}")
            return None
        except Exception as e:
            print(f"Errore durante l'upload: {e}")
            return None

    def upload_to_folder(self, file_path: str) -> Optional[str]:
        """
        Carica un file nella cartella configurata di Google Drive

        Args:
            file_path: Path del file da caricare

        Returns:
            ID del file caricato se il caricamento ha successo, None altrimenti
        """
        try:
            # Autentica se necessario
            if not self.service:
                if not self.authenticate():
                    return None

            # Ottieni la configurazione della cartella
            drive_config = self.config.get_google_drive_config()
            folder_name = drive_config.get('folder_name', 'Dashboard Reports')

            # Ottieni l'ID della cartella dalle variabili d'ambiente o crea la cartella
            folder_id = self.config.get_env_variable('GOOGLE_DRIVE_FOLDER_ID')

            if not folder_id:
                # Trova o crea la cartella
                folder_id = self.find_or_create_folder(folder_name)
                if not folder_id:
                    print("Impossibile creare o trovare la cartella")
                    return None

            # Carica il file
            file_id = self.upload_file(file_path, folder_id)

            return file_id

        except Exception as e:
            print(f"Errore durante l'upload su Google Drive: {e}")
            return None
