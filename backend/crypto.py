"""
Sistema di cifratura per le credenziali dei locali
"""
import os
import base64
from cryptography.fernet import Fernet


class CryptoManager:
    """Gestisce la cifratura e decifratura delle credenziali"""

    def __init__(self, encryption_key: str = None):
        """
        Inizializza il CryptoManager

        Args:
            encryption_key: Chiave Fernet per la cifratura. Se None, usa ENCRYPTION_KEY da variabile d'ambiente
        """
        if encryption_key is None:
            encryption_key = os.getenv('ENCRYPTION_KEY')
            if not encryption_key:
                raise ValueError("ENCRYPTION_KEY non trovata nelle variabili d'ambiente!")

        # Usa direttamente la chiave Fernet fornita
        self.fernet = Fernet(encryption_key.encode())

    def encrypt(self, text: str) -> str:
        """
        Cifra un testo

        Args:
            text: Testo da cifrare

        Returns:
            Testo cifrato in base64
        """
        encrypted_bytes = self.fernet.encrypt(text.encode())
        return base64.urlsafe_b64encode(encrypted_bytes).decode()

    def decrypt(self, encrypted_text: str) -> str:
        """
        Decifra un testo

        Args:
            encrypted_text: Testo cifrato in base64

        Returns:
            Testo in chiaro
        """
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
        decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()
