"""
Utility per retry automatico delle operazioni Selenium con exponential backoff

Questo modulo fornisce:
- Decorator @retry_selenium per aggiungere retry automatico a operazioni Selenium
- Exponential backoff (2s, 4s, 8s)
- Logging dettagliato dei tentativi
- Gestione intelligente di TimeoutException e NoSuchElementException
"""

import time
import functools
from typing import Callable, Any
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException
)


def retry_selenium(
    max_retries: int = 3,
    initial_delay: float = 2.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple = (
        TimeoutException,
        NoSuchElementException,
        StaleElementReferenceException,
        ElementClickInterceptedException,
    )
):
    """
    Decorator per aggiungere retry automatico alle operazioni Selenium

    Args:
        max_retries: Numero massimo di tentativi (default: 3)
        initial_delay: Delay iniziale in secondi (default: 2.0)
        backoff_factor: Fattore moltiplicativo per exponential backoff (default: 2.0)
        retryable_exceptions: Tuple di eccezioni che attivano il retry

    Returns:
        Decorated function con retry logic

    Example:
        @retry_selenium(max_retries=3, initial_delay=2.0)
        def login(self, username, password):
            # operazioni selenium...
            return True
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    # Esegui la funzione
                    result = func(*args, **kwargs)

                    # Successo!
                    if attempt > 1:
                        print(f"✓ Operazione '{func.__name__}' riuscita al tentativo {attempt}/{max_retries}")
                    return result

                except retryable_exceptions as e:
                    last_exception = e
                    error_msg = f"{type(e).__name__}: {str(e)}"
                    print(f"⚠ Tentativo {attempt}/{max_retries} per '{func.__name__}' fallito: {error_msg}")

                    if attempt < max_retries:
                        delay = initial_delay * (backoff_factor ** (attempt - 1))
                        print(f"🔄 Riprovo tra {delay} secondi...")
                        time.sleep(delay)
                    else:
                        print(f"❌ Operazione '{func.__name__}' fallita dopo {max_retries} tentativi")
                        # Ritorna False invece di lanciare eccezione per mantenere compatibilità
                        return False

                except WebDriverException as e:
                    # WebDriverException generico: retry
                    last_exception = e
                    error_msg = f"WebDriverException: {str(e)}"
                    print(f"⚠ Tentativo {attempt}/{max_retries} per '{func.__name__}' fallito: {error_msg}")

                    if attempt < max_retries:
                        delay = initial_delay * (backoff_factor ** (attempt - 1))
                        print(f"🔄 Riprovo tra {delay} secondi...")
                        time.sleep(delay)
                    else:
                        print(f"❌ Operazione '{func.__name__}' fallita dopo {max_retries} tentativi")
                        return False

                except Exception as e:
                    # Eccezioni non ritentabili: fallisci immediatamente
                    print(f"❌ Errore non ritentabile in '{func.__name__}': {type(e).__name__}: {str(e)}")
                    raise

            # Se arriviamo qui, tutti i tentativi sono falliti
            return False

        return wrapper
    return decorator


def retry_selenium_operation(operation: Callable, max_retries: int = 3, initial_delay: float = 2.0) -> Any:
    """
    Esegue un'operazione Selenium con retry automatico

    Questa è una versione funzionale (non decorator) per wrappare singole operazioni inline.

    Args:
        operation: Callable da eseguire (lambda o funzione)
        max_retries: Numero massimo di tentativi (default: 3)
        initial_delay: Delay iniziale in secondi (default: 2.0)

    Returns:
        Risultato dell'operazione se successo, None se fallisce

    Example:
        element = retry_selenium_operation(
            lambda: driver.find_element(By.ID, "my-id"),
            max_retries=3
        )
    """
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            result = operation()
            if attempt > 1:
                print(f"✓ Operazione riuscita al tentativo {attempt}/{max_retries}")
            return result

        except (
            TimeoutException,
            NoSuchElementException,
            StaleElementReferenceException,
            ElementClickInterceptedException,
            WebDriverException
        ) as e:
            last_exception = e
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"⚠ Tentativo {attempt}/{max_retries} fallito: {error_msg}")

            if attempt < max_retries:
                delay = initial_delay * (2.0 ** (attempt - 1))
                print(f"🔄 Riprovo tra {delay} secondi...")
                time.sleep(delay)
            else:
                print(f"❌ Operazione fallita dopo {max_retries} tentativi")
                return None

        except Exception as e:
            print(f"❌ Errore non ritentabile: {type(e).__name__}: {str(e)}")
            raise

    return None
