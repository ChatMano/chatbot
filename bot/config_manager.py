"""
Modulo per la gestione della configurazione del bot
"""
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigManager:
    """Gestisce la configurazione del bot e le variabili d'ambiente"""

    def __init__(self, config_file: str = "config.json"):
        """
        Inizializza il ConfigManager

        Args:
            config_file: Path al file di configurazione JSON
        """
        self.config_file = config_file
        self.config = self._load_config()
        load_dotenv()

    def _load_config(self) -> Dict[str, Any]:
        """Carica la configurazione dal file JSON"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"File di configurazione {self.config_file} non trovato. "
                f"Copia config.json.example in config.json e configuralo."
            )

        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_dashboard_config(self) -> Dict[str, Any]:
        """Restituisce la configurazione della dashboard"""
        return self.config.get('dashboard', {})

    def get_selectors(self) -> Dict[str, str]:
        """Restituisce i selettori CSS per la navigazione"""
        return self.config.get('selectors', {})

    def get_navigation_config(self) -> Dict[str, Any]:
        """Restituisce la configurazione di navigazione"""
        return self.config.get('navigation', {})

    def get_google_drive_config(self) -> Dict[str, Any]:
        """Restituisce la configurazione di Google Drive"""
        return self.config.get('google_drive', {})

    def get_env_variable(self, key: str, default: Any = None) -> Any:
        """
        Ottiene una variabile d'ambiente

        Args:
            key: Nome della variabile
            default: Valore di default se non trovata

        Returns:
            Valore della variabile d'ambiente
        """
        return os.getenv(key, default)

    def get_download_path(self) -> str:
        """Restituisce il path per i download"""
        path = self.get_env_variable('DOWNLOAD_PATH', './downloads')
        os.makedirs(path, exist_ok=True)
        return os.path.abspath(path)

    def is_headless_mode(self) -> bool:
        """Verifica se il browser deve essere eseguito in modalità headless"""
        return self.get_env_variable('HEADLESS_MODE', 'false').lower() == 'true'
