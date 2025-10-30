"""
Modulo per il bot Selenium che naviga nella dashboard e scarica i file Excel
"""
import os
import time
import glob
from datetime import datetime, timedelta
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pytz

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

        # Modalità headless - usa la nuova modalità su GitHub Actions
        if os.getenv('GITHUB_ACTIONS'):
            chrome_options.add_argument("--headless=new")
            print("Modalità headless (new) attivata per GitHub Actions")
        elif self.config.is_headless_mode():
            chrome_options.add_argument("--headless")
            print("Modalità headless attivata")

        # Opzioni aggiuntive per stabilità
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Opzioni aggiuntive per GitHub Actions
        if os.getenv('GITHUB_ACTIONS'):
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-breakpad")
            chrome_options.add_argument("--disable-component-extensions-with-background-pages")
            chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")

        # Inizializza il driver
        if os.getenv('GITHUB_ACTIONS'):
            # Su GitHub Actions, usa Chrome e ChromeDriver dal PATH (installati da setup-chrome action)
            self.driver = webdriver.Chrome(options=chrome_options)
        else:
            # In locale, usa ChromeDriverManager
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

    def unlock_secret_popup(self, pin: str = '123456') -> bool:
        """
        Apre il popup segreto e inserisce il codice PIN

        Args:
            pin: Il codice PIN da inserire (default: 123456)

        Returns:
            True se il popup viene sbloccato con successo, False altrimenti
        """
        try:
            selectors = self.config.get_selectors()
            nav_config = self.config.get_navigation_config()

            # Clicca N volte sul footer per aprire il popup segreto
            clicks = nav_config.get('secret_popup_clicks', 3)
            print(f"Apertura popup segreto ({clicks} click sul footer)...")
            footer_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors.get('secret_popup_trigger')))
            )

            # Esegui i click usando JavaScript (più affidabile in headless mode)
            for i in range(clicks):
                self.driver.execute_script("arguments[0].click();", footer_element)
                time.sleep(0.3)
                print(f"Click {i+1}/{clicks}")

            # Attendi che il popup appaia
            time.sleep(1)
            print("Popup aperto!")

            # Inserisci il PIN
            print(f"Inserimento PIN: {pin}...")
            secret_pin_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors.get('secret_pin_field')))
            )
            secret_pin_field.clear()
            secret_pin_field.send_keys(pin)
            time.sleep(0.5)
            print("PIN inserito!")

            # Click sul pulsante di conferma
            print("Click sul pulsante di conferma...")
            confirm_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.get('secret_pin_confirm')))
            )
            confirm_button.click()

            wait_time = nav_config.get('wait_after_pin', 2)
            time.sleep(wait_time)
            print("Popup confermato e sbloccato!")

            return True

        except TimeoutException:
            print("Errore: Timeout durante l'apertura del popup segreto")
            return False
        except Exception as e:
            print(f"Errore durante l'apertura del popup segreto: {e}")
            return False

    def navigate_to_reports_page(self) -> bool:
        """
        Naviga alla pagina dei report tramite i menu

        Returns:
            True se la navigazione ha successo, False altrimenti
        """
        try:
            selectors = self.config.get_selectors()
            nav_config = self.config.get_navigation_config()

            # Click sul menu principale
            print("Click sul menu principale...")
            menu_main = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.get('menu_main')))
            )
            menu_main.click()
            time.sleep(nav_config.get('wait_after_menu_click', 2))
            print("✓ Menu principale aperto")

            # Click sul sottomenu
            print("Click sul sottomenu...")
            menu_submenu = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.get('menu_submenu')))
            )
            menu_submenu.click()
            time.sleep(nav_config.get('wait_after_menu_click', 2))
            print("✓ Sottomenu aperto - pagina report caricata")

            return True

        except TimeoutException:
            print("Errore: Timeout durante la navigazione ai menu")
            return False
        except Exception as e:
            print(f"Errore durante la navigazione: {e}")
            return False

    def select_locale(self, locale_selector: Optional[str] = None) -> bool:
        """
        Seleziona un locale specifico se presente

        Args:
            locale_selector: Selettore CSS per il locale specifico (opzionale)

        Returns:
            True se la selezione ha successo o non è necessaria, False altrimenti
        """
        try:
            selectors = self.config.get_selectors()
            nav_config = self.config.get_navigation_config()

            if not locale_selector:
                print("⚠ Nessun selettore locale specificato - uso locale di default")
                return True

            # Click sul dropdown per aprire la lista locali
            print("Apertura dropdown selezione locale...")
            locale_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.get('locale_dropdown_button')))
            )
            locale_dropdown.click()
            time.sleep(1)
            print("✓ Dropdown locale aperto")

            # Click sul locale specifico
            print(f"Selezione locale con selettore: {locale_selector}")
            locale_option = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, locale_selector))
            )
            locale_option.click()
            time.sleep(1)
            print("✓ Locale selezionato")

            # Chiudi il dropdown per evitare che copra altri elementi
            print("Chiusura dropdown...")
            locale_dropdown.click()
            time.sleep(nav_config.get('wait_after_locale_select', 2))
            print("✓ Dropdown chiuso")

            return True

        except TimeoutException:
            print("Errore: Timeout durante la selezione del locale")
            print("Continuo con il locale di default...")
            return True  # Non fallisce, continua con default
        except Exception as e:
            print(f"Errore durante la selezione del locale: {e}")
            print("Continuo con il locale di default...")
            return True  # Non fallisce, continua con default

    def set_date_filter(self) -> bool:
        """
        Imposta il filtro data al giorno precedente (formato DD/MM/YYYY, timezone Roma)

        Returns:
            True se l'impostazione ha successo, False altrimenti
        """
        try:
            selectors = self.config.get_selectors()
            nav_config = self.config.get_navigation_config()

            # Calcola la data di ieri nel timezone di Roma
            rome_tz = pytz.timezone('Europe/Rome')
            now_rome = datetime.now(rome_tz)
            yesterday = now_rome - timedelta(days=1)
            date_str = yesterday.strftime('%d/%m/%Y')

            print(f"Impostazione filtro data a: {date_str}...")

            # Click sul filtro data per aprire il date picker
            print("Apertura date picker...")
            date_filter = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.get('date_filter_trigger')))
            )
            date_filter.click()
            time.sleep(1)
            print("✓ Date picker aperto")

            # Imposta la data di inizio
            print(f"Impostazione data inizio: {date_str}...")
            date_start_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors.get('date_start_input')))
            )
            date_start_input.clear()
            date_start_input.send_keys(date_str)
            time.sleep(0.5)
            print("✓ Data inizio impostata")

            # Imposta la data di fine (stesso giorno)
            print(f"Impostazione data fine: {date_str}...")
            date_end_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors.get('date_end_input')))
            )
            date_end_input.clear()
            date_end_input.send_keys(date_str)
            time.sleep(0.5)
            print("✓ Data fine impostata")

            # Click sul pulsante Applica
            print("Conferma selezione date...")
            apply_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.get('date_apply_button')))
            )
            apply_button.click()

            wait_time = nav_config.get('wait_after_date_select', 2)
            time.sleep(wait_time)
            print("✓ Filtro data applicato")

            return True

        except TimeoutException:
            print("Errore: Timeout durante l'impostazione del filtro data")
            return False
        except Exception as e:
            print(f"Errore durante l'impostazione del filtro data: {e}")
            return False

    def trigger_data_update(self) -> bool:
        """
        Clicca sul pulsante di aggiornamento dati

        Returns:
            True se il click ha successo, False altrimenti
        """
        try:
            selectors = self.config.get_selectors()
            nav_config = self.config.get_navigation_config()

            print("Click su 'Aggiornamento dati'...")
            aggiornamento_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.get('aggiornamento_dati_button')))
            )
            aggiornamento_button.click()
            time.sleep(nav_config.get('wait_after_aggiornamento', 3))
            print("✓ Aggiornamento dati completato")

            return True

        except TimeoutException:
            print("Errore: Timeout durante l'aggiornamento dati")
            return False
        except Exception as e:
            print(f"Errore durante l'aggiornamento dati: {e}")
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

            # Trova il pulsante di download XLSX
            print("Ricerca pulsante di download XLSX...")
            download_button = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors.get('download_xlsx_button')))
            )
            print("✓ Pulsante trovato")

            # Scrolla fino all'elemento per renderlo visibile
            print("Scroll fino al pulsante...")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", download_button)
            time.sleep(1)
            print("✓ Elemento visibile")

            # Attendi che sia cliccabile e clicca
            print("Click sul pulsante di download XLSX...")
            download_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.get('download_xlsx_button')))
            )
            download_button.click()
            print("✓ Click effettuato sul download")

            # Attendi che il file inizi a scaricarsi
            print("Attesa inizio download...")
            max_wait_start = 10  # Massimo 10 secondi per iniziare
            downloaded_file = None

            for i in range(max_wait_start):
                time.sleep(1)
                after_files = set(glob.glob(os.path.join(download_path, "*")))
                new_files = after_files - before_files
                if new_files:
                    downloaded_file = list(new_files)[0]
                    print(f"✓ File trovato: {os.path.basename(downloaded_file)}")
                    break

            if not downloaded_file:
                print("Errore: Nessun nuovo file trovato nella directory di download")
                return None

            # Aspetta che il file sia completamente scaricato
            print("Attesa completamento download...")
            max_wait_complete = 30  # Massimo 30 secondi per completare
            last_size = -1
            stable_count = 0

            for i in range(max_wait_complete):
                time.sleep(1)
                try:
                    current_size = os.path.getsize(downloaded_file)
                    if current_size == last_size:
                        stable_count += 1
                        if stable_count >= 3:  # 3 secondi senza cambiamenti
                            print(f"✓ Download completato ({current_size} bytes)")
                            break
                    else:
                        stable_count = 0
                        last_size = current_size
                        print(f"  Download in corso... ({current_size} bytes)")
                except:
                    pass

            # Verifica che il file HTML sia completo (se è HTML)
            try:
                with open(downloaded_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if content.startswith('<html') or content.startswith('<!DOCTYPE'):
                        if not content.rstrip().endswith('</html>'):
                            print(f"⚠ ATTENZIONE: File HTML incompleto!")
                            print(f"   Il file termina con: {content[-50:]}")
                            print(f"   Prova ad aumentare il tempo di attesa.")
                            return None
                        else:
                            print(f"✓ File HTML completo e valido")
            except Exception as e:
                print(f"Avviso: impossibile verificare completezza file: {e}")

            print(f"✓ File scaricato con successo: {downloaded_file}")
            return downloaded_file

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

    def run(self, pin: str = '123456', locale_selector: Optional[str] = None) -> Optional[str]:
        """
        Esegue l'intero processo: setup, login, navigazione e download

        Args:
            pin: PIN per sbloccare il popup segreto (default: 123456)
            locale_selector: Selettore CSS per il locale specifico (opzionale)

        Returns:
            Path del file scaricato se il processo ha successo, None altrimenti
        """
        try:
            print("\n" + "="*60)
            print("AVVIO BOT - PROCESSO COMPLETO")
            print("="*60 + "\n")

            # Setup del driver
            self.setup_driver()

            # Ottieni le credenziali
            username, password = self.auth.get_credentials()

            # 1. Login
            print("\n[1/8] LOGIN")
            if not self.login(username, password):
                print("❌ Login fallito")
                return None

            # 2. Sblocca il popup segreto con PIN
            print("\n[2/8] SBLOCCO POPUP SEGRETO")
            if not self.unlock_secret_popup(pin):
                print("❌ Sblocco popup segreto fallito")
                return None

            # 3. Naviga ai menu
            print("\n[3/8] NAVIGAZIONE MENU")
            if not self.navigate_to_reports_page():
                print("❌ Navigazione menu fallita")
                return None

            # 4. Seleziona locale (opzionale)
            print("\n[4/8] SELEZIONE LOCALE")
            if not self.select_locale(locale_selector):
                print("❌ Selezione locale fallita")
                return None

            # 5. Imposta filtro data
            print("\n[5/8] IMPOSTAZIONE FILTRO DATA")
            if not self.set_date_filter():
                print("❌ Impostazione filtro data fallita")
                return None

            # 6. Click aggiornamento dati
            print("\n[6/8] AGGIORNAMENTO DATI")
            if not self.trigger_data_update():
                print("❌ Aggiornamento dati fallito")
                return None

            # 7. Download file XLSX
            print("\n[7/8] DOWNLOAD FILE EXCEL")
            downloaded_file = self.download_excel_file()
            if not downloaded_file:
                print("❌ Download fallito")
                return None

            print("\n[8/8] COMPLETATO!")
            print("\n" + "="*60)
            print("✓✓✓ PROCESSO COMPLETATO CON SUCCESSO ✓✓✓")
            print("="*60 + "\n")

            return downloaded_file

        except Exception as e:
            print(f"\n❌ ERRORE durante l'esecuzione del bot: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            self.close()
