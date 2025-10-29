"""
Modulo per il bot Selenium che naviga nella dashboard e scarica i file Excel
"""
import os
import time
import glob
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from .config_manager import ConfigManager
from .auth import AuthManager


class DashboardScraper:
    """Bot Selenium per navigare e scaricare file dalla dashboard"""

    def __init__(self, config_manager: ConfigManager, auth_manager: AuthManager):
        """
        Inizializza il scraper

        Args:
            config_manager: Gestore della configurazione
            auth_manager: Gestore dell'autenticazione
        """
        self.config = config_manager
        self.auth = auth_manager
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None

    def setup_driver(self):
        """Configura e inizializza il driver Selenium"""
        print("Inizializzazione del driver Chrome...")

        chrome_options = Options()

        # Configura il path per i download
        download_path = self.config.get_download_path()
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # Modalità headless se configurata
        if self.config.is_headless_mode():
            chrome_options.add_argument("--headless")
            print("Modalità headless attivata")

        # Opzioni aggiuntive per stabilità
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Inizializza il driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

        print("Driver Chrome inizializzato con successo")

    def login(self, username: str, password: str) -> bool:
        """
        Esegue il login nella dashboard

        Args:
            username: Username per il login
            password: Password per il login

        Returns:
            True se il login ha successo, False altrimenti
        """
        try:
            dashboard_config = self.config.get_dashboard_config()
            selectors = self.config.get_selectors()

            login_url = dashboard_config.get('login_url')
            print(f"Navigazione alla pagina di login: {login_url}")
            self.driver.get(login_url)

            # Attendi e compila il campo username
            print("Inserimento username...")
            username_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors.get('username_field')))
            )
            username_field.clear()
            username_field.send_keys(username)

            # Compila il campo password
            print("Inserimento password...")
            password_field = self.driver.find_element(By.CSS_SELECTOR, selectors.get('password_field'))
            password_field.clear()
            password_field.send_keys(password)

            # Click sul pulsante di login
            print("Click sul pulsante di login...")
            login_button = self.driver.find_element(By.CSS_SELECTOR, selectors.get('login_button'))
            login_button.click()

            # Attendi il completamento del login
            nav_config = self.config.get_navigation_config()
            wait_time = nav_config.get('wait_after_login', 3)
            time.sleep(wait_time)

            print("Login completato con successo")
            return True

        except TimeoutException:
            print("Errore: Timeout durante il login")
            return False
        except NoSuchElementException as e:
            print(f"Errore: Elemento non trovato durante il login - {e}")
            return False
        except Exception as e:
            print(f"Errore durante il login: {e}")
            return False

    def navigate_to_download_page(self) -> bool:
        """
        Naviga alla pagina di download

        Returns:
            True se la navigazione ha successo, False altrimenti
        """
        try:
            dashboard_config = self.config.get_dashboard_config()
            download_url = dashboard_config.get('download_page_url')

            print(f"Navigazione alla pagina di download: {download_url}")
            self.driver.get(download_url)
            time.sleep(2)

            return True

        except Exception as e:
            print(f"Errore durante la navigazione: {e}")
            return False

    def download_excel_file(self) -> Optional[str]:
        """
        Scarica il file Excel dalla dashboard

        Returns:
            Path del file scaricato se il download ha successo, None altrimenti
        """
        try:
            selectors = self.config.get_selectors()
            nav_config = self.config.get_navigation_config()

            # Conta i file esistenti nella directory di download
            download_path = self.config.get_download_path()
            before_files = set(glob.glob(os.path.join(download_path, "*")))

            # Clicca sul pulsante di download
            print("Click sul pulsante di download...")
            download_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.get('download_button')))
            )
            download_button.click()

            # Attendi il completamento del download
            wait_time = nav_config.get('wait_for_download', 10)
            print(f"Attesa completamento download ({wait_time} secondi)...")
            time.sleep(wait_time)

            # Trova il nuovo file scaricato
            after_files = set(glob.glob(os.path.join(download_path, "*")))
            new_files = after_files - before_files

            if new_files:
                downloaded_file = list(new_files)[0]
                print(f"File scaricato con successo: {downloaded_file}")
                return downloaded_file
            else:
                print("Errore: Nessun nuovo file trovato nella directory di download")
                return None

        except TimeoutException:
            print("Errore: Timeout durante il download del file")
            return None
        except Exception as e:
            print(f"Errore durante il download: {e}")
            return None

    def close(self):
        """Chiude il driver Selenium"""
        if self.driver:
            print("Chiusura del browser...")
            self.driver.quit()
            print("Browser chiuso")

    def run(self) -> Optional[str]:
        """
        Esegue l'intero processo: setup, login, navigazione e download

        Returns:
            Path del file scaricato se il processo ha successo, None altrimenti
        """
        try:
            # Setup del driver
            self.setup_driver()

            # Ottieni le credenziali
            username, password = self.auth.get_credentials()

            # Login
            if not self.login(username, password):
                print("Login fallito")
                return None

            # Naviga alla pagina di download
            if not self.navigate_to_download_page():
                print("Navigazione alla pagina di download fallita")
                return None

            # Scarica il file
            downloaded_file = self.download_excel_file()

            return downloaded_file

        except Exception as e:
            print(f"Errore durante l'esecuzione del bot: {e}")
            return None
        finally:
            self.close()
