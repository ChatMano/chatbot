"""
Sistema di cifratura per le credenziali dei locali
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class CryptoManager:
    """Gestisce la cifratura e decifratura delle credenziali"""

    def __init__(self, secret_key: str = None):
        """
        Inizializza il CryptoManager

        Args:
            secret_key: Chiave segreta per la cifratura. Se None, usa variabile d'ambiente
        """
        if secret_key is None:
            secret_key = os.getenv('SECRET_KEY', 'default-secret-key-change-me')

        # Genera una chiave Fernet dalla secret key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'pratico-salt',  # In produzione usare un salt unico
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        self.fernet = Fernet(key)

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
