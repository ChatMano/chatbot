/**
 * Configurazione Axios con logica di retry automatica
 *
 * Questa configurazione implementa:
 * - Retry automatico per errori di rete e errori 5xx
 * - Exponential backoff (2s, 4s, 8s)
 * - Massimo 3 tentativi per richiesta
 * - Logging dettagliato dei retry
 */

import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

// Configurazione retry
const MAX_RETRIES = 3
const INITIAL_RETRY_DELAY = 2000 // 2 secondi

/**
 * Calcola il delay con exponential backoff
 * @param {number} retryCount - Numero del tentativo corrente
 * @returns {number} Delay in millisecondi
 */
const getRetryDelay = (retryCount) => {
  return INITIAL_RETRY_DELAY * Math.pow(2, retryCount - 1)
}

/**
 * Determina se un errore è riconoscibile
 * @param {Object} error - Errore axios
 * @returns {boolean} True se l'errore dovrebbe attivare un retry
 */
const isRetryableError = (error) => {
  if (!error.response) {
    // Errore di rete (nessuna risposta dal server)
    console.log('Errore di rete rilevato - retry necessario')
    return true
  }

  const status = error.response.status

  // Retry per errori 5xx (server errors)
  if (status >= 500 && status <= 599) {
    console.log(`Errore server ${status} rilevato - retry necessario`)
    return true
  }

  // Retry per errori 408 (Request Timeout) e 429 (Too Many Requests)
  if (status === 408 || status === 429) {
    console.log(`Errore ${status} rilevato - retry necessario`)
    return true
  }

  return false
}

/**
 * Esegue una pausa asincrona
 * @param {number} ms - Millisecondi da attendere
 * @returns {Promise} Promise che si risolve dopo il delay
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

// Crea istanza axios configurata
const axiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 secondi timeout (più del backend)
})

// Interceptor per le richieste
axiosInstance.interceptors.request.use(
  (config) => {
    // Inizializza il contatore di retry se non esiste
    config.retryCount = config.retryCount || 0
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor per le risposte con retry logic
axiosInstance.interceptors.response.use(
  (response) => {
    // Risposta OK - ritorna la risposta
    return response
  },
  async (error) => {
    const config = error.config

    // Se non esiste config o è già al massimo dei retry, fallisci
    if (!config || config.retryCount >= MAX_RETRIES) {
      if (config && config.retryCount >= MAX_RETRIES) {
        console.error(`❌ Fallito dopo ${MAX_RETRIES} tentativi:`, error.message)
      }
      return Promise.reject(error)
    }

    // Verifica se l'errore è ritentabile
    if (!isRetryableError(error)) {
      return Promise.reject(error)
    }

    // Incrementa il contatore di retry
    config.retryCount += 1
    const retryDelay = getRetryDelay(config.retryCount)

    console.log(
      `🔄 Tentativo ${config.retryCount}/${MAX_RETRIES} per ${config.url}...`,
      `Attendo ${retryDelay}ms prima del prossimo tentativo`
    )

    // Attendi prima di riprovare
    await sleep(retryDelay)

    // Riprova la richiesta
    return axiosInstance(config)
  }
)

export default axiosInstance
export { API_URL }
