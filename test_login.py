#!/usr/bin/env python3
"""
Script di test per verificare il login sulla dashboard iPratico
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from bot.config_manager import ConfigManager
from bot.auth import AuthManager


def test_login():
    """Test del processo di login"""

    print("\n" + "="*60)
    print("TEST LOGIN - iPratico Cloud")
    print("="*60 + "\n")

    # Carica configurazione
    print("Caricamento configurazione...")
    config = ConfigManager('config.json')
    auth = AuthManager()

    # Ottieni credenziali
    username, password = auth.get_credentials()

    # Setup driver Chrome
    print("\nInizializzo Chrome...")
    chrome_options = Options()

    # NON usiamo headless per vedere cosa succede
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    try:
        # Prova a scaricare/installare ChromeDriver con gestione errori migliorata
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.os_manager import ChromeType

        print("Download ChromeDriver in corso...")
        driver_path = ChromeDriverManager().install()
        print(f"ChromeDriver installato in: {driver_path}")
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Errore con webdriver-manager: {e}")
        print("\nProvo senza Service...")
        # Fallback: prova senza specificare il service
        driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        # Vai alla pagina di login
        dashboard_config = config.get_dashboard_config()
        selectors = config.get_selectors()
        login_url = dashboard_config.get('login_url')

        print(f"\nNavigazione a: {login_url}")
        driver.get(login_url)
        time.sleep(3)  # Aspetta che la pagina si carichi completamente

        # Prova a trovare il campo username
        print("\nCerco il campo username...")
        print(f"Selettore: {selectors.get('username_field')}")

        try:
            # Prima prova con il selettore fornito
            username_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors.get('username_field')))
            )
            print("✓ Campo username trovato!")
        except:
            print("✗ Campo username non trovato con il selettore fornito")
            print("Provo con selettori alternativi...")

            # Prova selettori alternativi
            alternative_selectors = [
                "input[type='text']",
                "input[name='username']",
                "input[id*='user']",
                "#loginForm input[type='text']"
            ]

            for alt_selector in alternative_selectors:
                try:
                    username_field = driver.find_element(By.CSS_SELECTOR, alt_selector)
                    print(f"✓ Campo username trovato con: {alt_selector}")
                    break
                except:
                    continue
            else:
                raise Exception("Impossibile trovare il campo username")

        # Inserisci username
        print(f"Inserisco username: {username}")
        username_field.clear()
        username_field.send_keys(username)
        time.sleep(1)

        # Cerca il campo password
        print("\nCerco il campo password...")
        print(f"Selettore: {selectors.get('password_field')}")

        try:
            password_field = driver.find_element(By.CSS_SELECTOR, selectors.get('password_field'))
            print("✓ Campo password trovato!")
        except:
            print("✗ Campo password non trovato con il selettore fornito")
            print("Provo con selettori alternativi...")

            alternative_selectors = [
                "input[type='password']",
                "input[name='password']",
                "#loginForm input[type='password']"
            ]

            for alt_selector in alternative_selectors:
                try:
                    password_field = driver.find_element(By.CSS_SELECTOR, alt_selector)
                    print(f"✓ Campo password trovato con: {alt_selector}")
                    break
                except:
                    continue
            else:
                raise Exception("Impossibile trovare il campo password")

        # Inserisci password
        print("Inserisco password...")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)

        # Cerca il pulsante di login
        print("\nCerco il pulsante di login...")
        print(f"Selettore: {selectors.get('login_button')}")

        try:
            login_button = driver.find_element(By.CSS_SELECTOR, selectors.get('login_button'))
            print("✓ Pulsante di login trovato!")
        except:
            print("✗ Pulsante di login non trovato con il selettore fornito")
            print("Provo con selettori alternativi...")

            alternative_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "#loginForm button",
                ".submit-row button"
            ]

            for alt_selector in alternative_selectors:
                try:
                    login_button = driver.find_element(By.CSS_SELECTOR, alt_selector)
                    print(f"✓ Pulsante di login trovato con: {alt_selector}")
                    break
                except:
                    continue
            else:
                raise Exception("Impossibile trovare il pulsante di login")

        # Click sul pulsante di login
        print("\nClick sul pulsante di login...")
        login_button.click()

        # Aspetta che la pagina cambi
        print("\nAttendo il completamento del login...")
        time.sleep(5)

        # Verifica l'URL corrente
        current_url = driver.current_url
        expected_url = dashboard_config.get('after_login_url')

        print(f"\nURL attuale: {current_url}")
        print(f"URL atteso: {expected_url}")

        if expected_url in current_url or "/locale" in current_url:
            print("\n" + "="*60)
            print("✓✓✓ LOGIN RIUSCITO! ✓✓✓")
            print("="*60)

            # TEST POPUP SEGRETO
            print("\n" + "="*60)
            print("TEST POPUP SEGRETO")
            print("="*60)

            try:
                # Clicca 3 volte sul footer
                print("\nCerco l'elemento footer per aprire il popup...")
                footer_element = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#wrapper > div.content-page > footer > div'))
                )
                print("✓ Footer trovato!")

                print("\nEseguo 3 click sul footer...")
                for i in range(3):
                    footer_element.click()
                    time.sleep(0.3)
                    print(f"  Click {i+1}/3 ✓")

                # Aspetta che il popup appaia
                print("\nAttendo apertura popup...")
                time.sleep(2)
                print("✓ Popup dovrebbe essere aperto!")

                # Cerca il campo del codice segreto
                print("\nCerco il campo per il codice segreto...")
                secret_field = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#modal-training > div.modal-dialog > div > div.modal-body > div input'))
                )
                print("✓ Campo codice segreto trovato!")

                # Inserisci il codice
                print("\nInserisco codice segreto: 123456")
                secret_field.clear()
                secret_field.send_keys('123456')
                time.sleep(1)
                print("✓ Codice inserito!")

                # Cerca il pulsante di conferma
                try:
                    print("\nCerco il pulsante di conferma...")
                    confirm_button = driver.find_element(By.CSS_SELECTOR, '#modal-training button[type="submit"]')
                    print("✓ Pulsante di conferma trovato!")
                    confirm_button.click()
                    print("✓ Pulsante cliccato!")
                    time.sleep(2)
                except:
                    print("⚠ Nessun pulsante di conferma trovato (potrebbe essere normale)")

                print("\n" + "="*60)
                print("✓✓✓ POPUP SEGRETO SBLOCCATO! ✓✓✓")
                print("="*60)

            except Exception as e:
                print(f"\n❌ ERRORE nel popup segreto: {e}")
                print("Il popup potrebbe non essere presente o i selettori potrebbero essere diversi")

        else:
            print("\n" + "="*60)
            print("⚠ LOGIN POTREBBE ESSERE FALLITO")
            print("Verifica manualmente nella finestra del browser")
            print("="*60)

        # Aspetta 10 secondi per permettere all'utente di vedere
        print("\nTengo la finestra aperta per 10 secondi...")
        print("Controlla se sei loggato correttamente nella finestra del browser")
        time.sleep(10)

    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

        # Tieni la finestra aperta anche in caso di errore
        print("\nTengo la finestra aperta per 15 secondi per permetterti di vedere l'errore...")
        time.sleep(15)

    finally:
        print("\nChiudo il browser...")
        driver.quit()
        print("Test completato!")


if __name__ == "__main__":
    test_login()
