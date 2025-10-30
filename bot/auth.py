"""
Modulo per la gestione dell'autenticazione multi-tenant
"""
import os
import getpass
from typing import Tuple, Optional


class AuthManager:
    """Gestisce l'autenticazione per diversi tenant"""

    def __init__(self):
        """Inizializza l'AuthManager"""
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    def get_credentials(self) -> Tuple[str, str]:
        """
        Ottiene le credenziali per l'accesso alla dashboard.
        Prima controlla le variabili d'ambiente, altrimenti chiede all'utente.

        Returns:
            Tupla (username, password)
        """
        # Controlla se le credenziali sono nelle variabili d'ambiente
        env_username = os.getenv('DASHBOARD_USERNAME')
        env_password = os.getenv('DASHBOARD_PASSWORD')

        if env_username and env_password:
            print("Usando credenziali dalle variabili d'ambiente")
            self.username = env_username
            self.password = env_password
        else:
            # Chiedi all'utente
            print("\n" + "="*50)
            print("AUTENTICAZIONE DASHBOARD")
            print("="*50)
            self.username = input("Username: ")
            self.password = getpass.getpass("Password: ")
            print("="*50 + "\n")

        return self.username, self.password

    def prompt_for_tenant_selection(self) -> str:
        """
        Chiede all'utente di selezionare un tenant (se applicabile)

        Returns:
            ID o nome del tenant selezionato
        """
        print("\n" + "="*50)
        print("SELEZIONE TENANT")
        print("="*50)
        tenant = input("Inserisci il nome o ID del tenant: ")
        print("="*50 + "\n")
        return tenant

    def clear_credentials(self):
        """Pulisce le credenziali memorizzate"""
        self.username = None
        self.password = None
