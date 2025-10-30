"""
Utility per retry automatico delle chiamate HTTP con exponential backoff

Questo modulo fornisce:
- Decorator @retry_request per aggiungere retry automatico a funzioni
- Exponential backoff (2s, 4s, 8s)
- Logging dettagliato dei tentativi
- Gestione intelligente degli errori di rete e timeout
"""

import time
import functools
from typing import Callable, Any
import requests


def retry_request(
    max_retries: int = 3,
    initial_delay: float = 2.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple = (
        requests.exceptions.RequestException,
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
    )
):
    """
    Decorator per aggiungere retry automatico alle chiamate HTTP

    Args:
        max_retries: Numero massimo di tentativi (default: 3)
        initial_delay: Delay iniziale in secondi (default: 2.0)
        backoff_factor: Fattore moltiplicativo per exponential backoff (default: 2.0)
        retryable_exceptions: Tuple di eccezioni che attivano il retry

    Returns:
        Decorated function con retry logic

    Example:
        @retry_request(max_retries=3, initial_delay=2.0)
        def call_github_api():
            response = requests.post(url, json=data)
            return response
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    # Esegui la funzione
                    result = func(*args, **kwargs)

                    # Se è una response requests, verifica lo status code
                    if hasattr(result, 'status_code'):
                        # Status 5xx: retry
                        if 500 <= result.status_code <= 599:
                            error_msg = f"Server error {result.status_code}"
                            print(f"⚠ Tentativo {attempt}/{max_retries} fallito: {error_msg}")

                            if attempt < max_retries:
                                delay = initial_delay * (backoff_factor ** (attempt - 1))
                                print(f"🔄 Riprovo tra {delay} secondi...")
                                time.sleep(delay)
                                last_exception = Exception(error_msg)
                                continue
                            else:
                                print(f"❌ Fallito dopo {max_retries} tentativi")
                                return result  # Ritorna comunque la response

                        # Status 429: Too Many Requests - retry con backoff
                        elif result.status_code == 429:
                            error_msg = "Rate limit exceeded (429)"
                            print(f"⚠ Tentativo {attempt}/{max_retries} fallito: {error_msg}")

                            if attempt < max_retries:
                                # Per 429, usa un delay maggiore
                                delay = initial_delay * (backoff_factor ** attempt)
                                print(f"🔄 Riprovo tra {delay} secondi...")
                                time.sleep(delay)
                                last_exception = Exception(error_msg)
                                continue
                            else:
                                print(f"❌ Fallito dopo {max_retries} tentativi")
                                return result

                    # Successo!
                    if attempt > 1:
                        print(f"✓ Successo al tentativo {attempt}/{max_retries}")
                    return result

                except retryable_exceptions as e:
                    last_exception = e
                    error_msg = f"{type(e).__name__}: {str(e)}"
                    print(f"⚠ Tentativo {attempt}/{max_retries} fallito: {error_msg}")

                    if attempt < max_retries:
                        delay = initial_delay * (backoff_factor ** (attempt - 1))
                        print(f"🔄 Riprovo tra {delay} secondi...")
                        time.sleep(delay)
                    else:
                        print(f"❌ Fallito dopo {max_retries} tentativi")
                        raise

                except Exception as e:
                    # Eccezioni non ritentabili: fallisci immediatamente
                    print(f"❌ Errore non ritentabile: {type(e).__name__}: {str(e)}")
                    raise

            # Se arriviamo qui, tutti i tentativi sono falliti
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def is_retryable_status(status_code: int) -> bool:
    """
    Verifica se uno status code HTTP dovrebbe attivare un retry

    Args:
        status_code: HTTP status code

    Returns:
        True se lo status code è ritentabile, False altrimenti
    """
    # 5xx: Server errors
    if 500 <= status_code <= 599:
        return True

    # 408: Request Timeout
    if status_code == 408:
        return True

    # 429: Too Many Requests
    if status_code == 429:
        return True

    return False
