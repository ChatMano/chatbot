# Bot Multi-Tenant per Download Excel e Upload su Google Drive

Bot Python che scarica automaticamente file Excel da una dashboard cloud e li carica su Google Drive. Supporta configurazioni multi-tenant con autenticazione personalizzata.

## Caratteristiche

- **Multi-tenant**: Supporta credenziali multiple per diversi tenant
- **Selenium WebDriver**: Naviga automaticamente nella dashboard usando Chrome
- **Google Drive API**: Carica automaticamente i file scaricati su Google Drive
- **Configurabile**: Selettori CSS e URL completamente personalizzabili
- **Modalità Headless**: Può essere eseguito senza interfaccia grafica
- **Retry Logic**: Gestione automatica degli errori con tentativi multipli

## Requisiti

- Python 3.8 o superiore
- Chrome browser installato
- Account Google con accesso a Google Drive
- Credenziali per la dashboard da cui scaricare i file

## Installazione

1. **Clona il repository**
```bash
git clone <repository-url>
cd chatbot
```

2. **Crea un virtual environment (consigliato)**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows
```

3. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

4. **Configura le variabili d'ambiente**
```bash
cp .env.example .env
# Modifica il file .env con le tue configurazioni
```

5. **Configura i selettori e URL della dashboard**
```bash
cp config.json.example config.json
# Modifica il file config.json con i selettori della tua dashboard
```

## Configurazione Google Drive

Per utilizzare l'upload su Google Drive, devi configurare le credenziali OAuth 2.0:

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto o seleziona uno esistente
3. Abilita **Google Drive API**:
   - Vai su "APIs & Services" > "Enable APIs and Services"
   - Cerca "Google Drive API" e abilitala
4. Crea le credenziali:
   - Vai su "APIs & Services" > "Credentials"
   - Clicca "Create Credentials" > "OAuth client ID"
   - Scegli "Desktop app" come tipo di applicazione
   - Scarica il file JSON delle credenziali
5. Rinomina il file scaricato in `credentials.json` e mettilo nella root del progetto

### Primo utilizzo con Google Drive

Al primo avvio, il bot:
1. Aprirà una finestra del browser
2. Chiederà di autorizzare l'applicazione
3. Salverà le credenziali in `token.json` per i successivi utilizzi

## Configurazione Dashboard

### File `.env`

Modifica il file `.env` con le tue impostazioni:

```bash
# Credenziali Dashboard (opzionale, se lasciati vuoti verranno chiesti all'avvio)
DASHBOARD_USERNAME=tuo_username
DASHBOARD_PASSWORD=tua_password

# ID della cartella Google Drive (opzionale, se omesso verrà creata automaticamente)
GOOGLE_DRIVE_FOLDER_ID=

# Modalità headless (true/false)
HEADLESS_MODE=false

# Path per i download
DOWNLOAD_PATH=./downloads
```

### File `config.json`

Configura i selettori CSS e gli URL della tua dashboard:

```json
{
  "dashboard": {
    "base_url": "https://tua-dashboard.com",
    "login_url": "https://tua-dashboard.com/login",
    "download_page_url": "https://tua-dashboard.com/reports/download"
  },
  "selectors": {
    "username_field": "#username",
    "password_field": "#password",
    "login_button": "button[type='submit']",
    "download_button": ".btn-download"
  },
  "navigation": {
    "wait_after_login": 3,
    "wait_for_download": 10,
    "max_retries": 3
  },
  "google_drive": {
    "folder_name": "Dashboard Reports",
    "file_prefix": "report_"
  }
}
```

### Come trovare i selettori CSS

1. Apri la dashboard nel browser
2. Clicca con il tasto destro sull'elemento (es. campo username)
3. Seleziona "Ispeziona" o "Inspect Element"
4. Nel pannello degli sviluppatori, copia il selettore CSS dell'elemento
5. Inserisci il selettore nel file `config.json`

## Utilizzo

### Esecuzione base

```bash
python main.py
```

Il bot chiederà le credenziali (se non configurate nel `.env`) e procederà con:
1. Login nella dashboard
2. Navigazione alla pagina di download
3. Download del file Excel
4. Upload del file su Google Drive
5. Eliminazione del file locale

### Opzioni da linea di comando

```bash
# Specifica un file di configurazione diverso
python main.py --config config_custom.json

# Scarica il file senza caricarlo su Google Drive
python main.py --no-upload

# Mantieni il file locale dopo l'upload
python main.py --keep-file

# Combina le opzioni
python main.py --config config_custom.json --keep-file
```

## Struttura del Progetto

```
chatbot/
├── bot/                        # Package principale del bot
│   ├── __init__.py
│   ├── auth.py                 # Gestione autenticazione multi-tenant
│   ├── config_manager.py       # Gestione configurazione
│   ├── google_drive.py         # Upload su Google Drive
│   └── scraper.py              # Bot Selenium per la dashboard
├── downloads/                  # Directory per i file scaricati (creata automaticamente)
├── functions/                  # Netlify functions (progetto web esistente)
├── .env                        # Variabili d'ambiente (non committare!)
├── .env.example                # Template per le variabili d'ambiente
├── .gitignore                  # File da escludere da Git
├── config.json                 # Configurazione della dashboard (non committare!)
├── config.json.example         # Template per la configurazione
├── credentials.json            # Credenziali Google Drive (non committare!)
├── token.json                  # Token Google Drive (non committare!)
├── main.py                     # Script principale
├── requirements.txt            # Dipendenze Python
└── README.md                   # Questo file
```

## Modalità Multi-Tenant

Il bot supporta la gestione di credenziali multiple per diversi tenant:

1. **Modalità interattiva**: Se non configuri username/password nel `.env`, il bot li chiederà all'avvio
2. **Modalità automatica**: Configura le credenziali nel `.env` per esecuzioni automatiche
3. **Tenant multipli**: Puoi creare più file `.env` e `config.json` per tenant diversi e specificarli a runtime

### Esempio con tenant multipli

```bash
# Tenant 1
python main.py --config config_tenant1.json

# Tenant 2
python main.py --config config_tenant2.json
```

## Automazione

### Cron Job (Linux/Mac)

Per eseguire il bot automaticamente ogni giorno alle 9:00:

```bash
crontab -e
```

Aggiungi:
```
0 9 * * * cd /path/to/chatbot && /path/to/venv/bin/python main.py
```

### Task Scheduler (Windows)

1. Apri Task Scheduler
2. Crea una nuova attività
3. Imposta il trigger (es. ogni giorno alle 9:00)
4. Imposta l'azione: `python.exe` con argomento `/path/to/chatbot/main.py`

## Troubleshooting

### Il browser non si apre

- Verifica che Chrome sia installato
- Prova a eseguire senza modalità headless (`HEADLESS_MODE=false`)

### Elementi non trovati

- Verifica i selettori CSS nel file `config.json`
- I selettori potrebbero essere cambiati nella dashboard
- Usa gli strumenti di sviluppo del browser per trovare i selettori corretti

### Download non completato

- Aumenta il valore di `wait_for_download` in `config.json`
- Verifica che il file venga effettivamente scaricato nella cartella `downloads`

### Errori Google Drive

- Verifica che il file `credentials.json` sia presente
- Elimina `token.json` e riautorizza l'applicazione
- Verifica che Google Drive API sia abilitata nel progetto Google Cloud

## Sicurezza

⚠️ **IMPORTANTE**: Non committare mai i seguenti file:
- `.env` (contiene credenziali)
- `config.json` (potrebbe contenere informazioni sensibili)
- `credentials.json` (credenziali Google Drive)
- `token.json` (token di accesso Google Drive)
- File scaricati nella cartella `downloads/`

Questi file sono già inclusi nel `.gitignore`.

## Licenza

Questo progetto è fornito "as-is" senza garanzie di alcun tipo.

## Supporto

Per problemi o domande, apri una issue nel repository.
