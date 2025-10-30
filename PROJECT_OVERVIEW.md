# 🍕 Pratico Dashboard - Documentazione Completa del Sistema

**Ultimo aggiornamento:** 30 Ottobre 2025
**Versione:** 1.0 (Sistema completamente funzionante)

---

## 📋 Indice

1. [Panoramica del Sistema](#panoramica-del-sistema)
2. [Architettura](#architettura)
3. [Stack Tecnologico](#stack-tecnologico)
4. [Deployment e Infrastruttura](#deployment-e-infrastruttura)
5. [Funzionalità Principali](#funzionalità-principali)
6. [Come Funziona il Bot](#come-funziona-il-bot)
7. [Configurazione](#configurazione)
8. [Problemi Risolti](#problemi-risolti)
9. [Struttura del Progetto](#struttura-del-progetto)
10. [Debug e Troubleshooting](#debug-e-troubleshooting)
11. [Prossimi Sviluppi](#prossimi-sviluppi)

---

## 📖 Panoramica del Sistema

Sistema **multi-tenant** per automatizzare il download di file Excel dalla dashboard **iPratico Cloud** e caricarli automaticamente su **Google Sheets**. Ogni "locale" (ristorante/pizzeria) ha:

- Credenziali iPratico personalizzate
- Orario di esecuzione automatica configurabile
- Google Sheet di destinazione specifico
- Possibilità di esecuzione manuale istantanea

### Caso d'uso:
Ristoranti/pizzerie che usano iPratico per gestire ordini e necessitano di:
1. Scaricare automaticamente report giornalieri
2. Caricarli su Google Sheets per analisi/condivisione
3. Senza intervento manuale ogni giorno

---

## 🏗️ Architettura

```
┌─────────────────────────────────────────────────────────────────┐
│                        UTENTE FINALE                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                       │
│                  https://pratico-dashboard.netlify.app           │
│                                                                   │
│  - Gestione Locali (CRUD)                                        │
│  - Visualizzazione logs                                          │
│  - Pulsante "Esegui Ora"                                         │
│  - Axios con retry automatico (exponential backoff)              │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (Flask + SQLite)                       │
│              https://pratico-backend.onrender.com                │
│                                                                   │
│  - API REST (/api/locali, /api/locali/{id}/esegui-ora, etc.)   │
│  - Database SQLite (locali.db)                                   │
│  - Encryption/Decryption credenziali (Fernet)                   │
│  - Trigger GitHub Actions via API                                │
│  - Retry automatico per chiamate esterne                         │
└────────────────────────────┬────────────────────────────────────┘
                             │ Trigger workflow_dispatch
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS (Workflow)                     │
│                  .github/workflows/daily-download.yml            │
│                                                                   │
│  - Esecuzione schedulata (cron ogni ora)                         │
│  - Esecuzione manuale (workflow_dispatch)                        │
│  - Setup Chrome + Selenium                                       │
│  - Migrazione database automatica                                │
│  - Esecuzione bot Python                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BOT SELENIUM (Python)                       │
│                        run_bot.py                                │
│                                                                   │
│  1. Login su iPratico (con credenziali cifrate)                 │
│  2. Navigazione menu (popup segreto con PIN)                    │
│  3. Selezione locale specifico (se multi-locale)                │
│  4. Impostazione filtro data (ieri)                             │
│  5. Download file Excel                                          │
│  6. Upload su Google Sheets (via Google Sheets API)             │
│  7. Salvataggio log nel database                                │
│  8. Commit database aggiornato su Git                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Tecnologico

### Frontend
- **React 18** - UI Framework
- **Vite** - Build tool e dev server
- **Axios** - HTTP client con retry interceptor
- **CSS custom** - Styling

### Backend
- **Flask 3.0** - Web framework Python
- **SQLAlchemy** - ORM per database
- **SQLite** - Database (file-based)
- **Cryptography (Fernet)** - Encryption credenziali
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Gunicorn** - Production WSGI server

### Bot
- **Selenium WebDriver** - Browser automation
- **Chrome/ChromeDriver** - Headless browser
- **Google Sheets API** - Upload dati
- **Pandas/OpenPyxl** - Parsing Excel
- **pytz** - Gestione timezone (Europe/Rome)

### DevOps
- **GitHub Actions** - CI/CD e automation
- **Render** - Hosting backend (free tier)
- **Netlify** - Hosting frontend (free tier)
- **Git** - Version control

---

## 🌐 Deployment e Infrastruttura

### Frontend (Netlify)
- **URL:** https://pratico-dashboard.netlify.app (sostituire con URL reale)
- **Build Command:** `npm run build`
- **Publish Directory:** `dist`
- **Auto-deploy:** Push su `main` → deploy automatico
- **File config:** `netlify.toml`

### Backend (Render)
- **URL:** https://pratico-backend-gzp6.onrender.com
- **Tipo:** Web Service
- **Regione:** Frankfurt (Europe)
- **Start Command:** `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`
- **Auto-deploy:** Push su `main` → deploy automatico
- **File config:** `render.yaml`

### GitHub Actions (Workflow)
- **File:** `.github/workflows/daily-download.yml`
- **Schedule:** Cron `0 * * * *` (ogni ora alle :00)
- **Trigger manuale:** `workflow_dispatch` con input `locale_id` (opzionale)
- **Runner:** ubuntu-latest
- **Durata media:** 3-5 minuti per locale

### Database
- **Tipo:** SQLite (file-based)
- **Location produzione:** GitHub repository (`data/locali.db`)
- **Location Render:** Temporaneo (resetta ad ogni deploy)
- **Persistenza:** Database committato su Git dopo ogni esecuzione bot
- **Encryption:** Password e PIN cifrati con Fernet

---

## ✨ Funzionalità Principali

### 1. Gestione Locali (CRUD)

**Endpoint backend:**
- `GET /api/locali` - Lista tutti i locali
- `GET /api/locali/{id}` - Dettagli locale
- `POST /api/locali` - Crea nuovo locale
- `PUT /api/locali/{id}` - Aggiorna locale
- `DELETE /api/locali/{id}` - Elimina locale

**Campi locale:**
```json
{
  "id": 1,
  "nome": "Pizzeria Veneta",
  "username": "4gruppotessar@ipratico.com",
  "password_encrypted": "gAAAAAB...",
  "pin_encrypted": "gAAAAAB...",
  "orario_esecuzione": "03:00",
  "google_sheet_id": "1JDDcYoHkG5LTbB8w2tyMr8CcFc7l4ITsf9eYSVLwSNs",
  "locale_selector": "#wrapper > div.content-page > ...",
  "attivo": true,
  "esegui_ora": false,
  "created_at": "2025-10-30T22:23:44.817803",
  "updated_at": "2025-10-30T22:23:52.782764"
}
```

### 2. Esecuzione Immediata ("Esegui Ora")

**Flow completo:**

1. **Frontend:** Click pulsante "Esegui Ora" su un locale
   ```javascript
   POST /api/locali/1/esegui-ora
   ```

2. **Backend:**
   - Imposta flag `esegui_ora = true` nel database
   - Chiama GitHub Actions API per triggerare workflow
   ```python
   POST https://api.github.com/repos/ChatMano/chatbot/actions/workflows/daily-download.yml/dispatches
   {
     "ref": "main",
     "inputs": {
       "locale_id": "1"
     }
   }
   ```

3. **GitHub Actions:**
   - Workflow parte immediatamente (1-2 minuti)
   - Esegue migrazione database (se necessario)
   - Lancia `run_bot.py` con `LOCALE_ID=1`

4. **Bot:**
   - Legge credenziali dal database
   - Esegue SOLO il locale ID=1
   - Salva log nel database
   - Resetta flag `esegui_ora = false`
   - Commit database aggiornato

5. **Risultato:**
   - File Excel scaricato da iPratico
   - Dati caricati su Google Sheets
   - Log salvato nel database
   - Visibile nella dashboard frontend

**Tempo totale:** 3-5 minuti dall'inizio alla fine

### 3. Esecuzione Automatica Schedulata

**Cron schedule:** Ogni ora alle :00 (00:00, 01:00, 02:00, ..., 23:00)

**Logica di esecuzione:**

```python
def should_run_locale(locale):
    # Se esegui_ora è true → esegui sempre
    if locale.esegui_ora:
        return True

    # Ottieni ora corrente italiana
    now_italy = datetime.now(pytz.timezone('Europe/Rome'))
    current_hour = now_italy.hour

    # Confronta con orario_esecuzione del locale
    locale_hour = int(locale.orario_esecuzione.split(':')[0])

    if locale_hour != current_hour:
        return False

    # Verifica se già eseguito oggi
    # (controlla ultimo log con successo nella data odierna)

    return True
```

**Esempio:**
- Locale A: `orario_esecuzione = "03:00"` → esegue alle 3:00 AM
- Locale B: `orario_esecuzione = "14:00"` → esegue alle 2:00 PM
- Locale C: `orario_esecuzione = "03:00"` → esegue alle 3:00 AM (stesso orario di A)

**Alle 03:00 AM:** Locale A e C vengono eseguiti
**Alle 14:00 PM:** Solo Locale B viene eseguito

### 4. Retry Automatico

**Frontend (Axios Interceptor):**
```javascript
// frontend/src/utils/axiosConfig.js
- Retry automatico per errori di rete
- Retry per status 5xx, 408, 429
- Exponential backoff: 2s → 4s → 8s
- Massimo 3 tentativi
```

**Backend (Decorator):**
```python
# backend/retry_utils.py
@retry_request(max_retries=3, initial_delay=2.0)
def _trigger_github_workflow():
    return requests.post(api_url, ...)
```

**Bot Selenium (Decorator):**
```python
# bot/retry_selenium.py
@retry_selenium(max_retries=3, initial_delay=2.0)
def login(username, password):
    # Login con retry automatico
```

Tutte le operazioni critiche hanno retry automatico!

### 5. Logging e Monitoraggio

**Endpoint logs:**
```
GET /api/locali/{id}/logs
```

**Campi log:**
```json
{
  "id": 1,
  "locale_id": 1,
  "eseguito_at": "2025-10-30T23:45:00",
  "successo": true,
  "messaggio": "Completato con successo",
  "file_scaricato": "/downloads/report_20251030.xls",
  "sheet_aggiornato": true
}
```

**Dove vedere i log:**
1. **Dashboard frontend:** Sezione "Ultimi Log"
2. **GitHub Actions:** Logs del workflow run
3. **Render:** Logs del backend (real-time)

---

## 🤖 Come Funziona il Bot

### Flusso Completo di Esecuzione

```
START
  │
  ├─► 1. Setup Database
  │     └─► Migrazione automatica (aggiunge colonna esegui_ora se mancante)
  │
  ├─► 2. Carica Configurazione
  │     ├─► config.json (selettori CSS)
  │     ├─► credentials.json (Google Sheets)
  │     └─► ENCRYPTION_KEY (decifratura password)
  │
  ├─► 3. Determina Locale da Eseguire
  │     ├─► Se LOCALE_ID env var → esegui solo quel locale
  │     └─► Altrimenti → filtra per orario_esecuzione
  │
  ├─► 4. Per ogni locale selezionato:
  │     │
  │     ├─► 4.1 Setup Selenium
  │     │     ├─► Chrome headless
  │     │     └─► WebDriverWait (10s timeout)
  │     │
  │     ├─► 4.2 Login iPratico
  │     │     ├─► Naviga a login_url
  │     │     ├─► Inserisci username
  │     │     ├─► Inserisci password (decifrata)
  │     │     └─► Click login button
  │     │
  │     ├─► 4.3 Sblocco Popup Segreto
  │     │     ├─► Click 3x sul footer
  │     │     ├─► Inserisci PIN (decifrato)
  │     │     └─► Conferma
  │     │
  │     ├─► 4.4 Navigazione Menu
  │     │     ├─► Click menu principale
  │     │     └─► Click sottomenu report
  │     │
  │     ├─► 4.5 Selezione Locale (opzionale)
  │     │     ├─► Apri dropdown locale
  │     │     ├─► Click su locale_selector (se configurato)
  │     │     └─► Chiudi dropdown
  │     │
  │     ├─► 4.6 Filtro Data
  │     │     ├─► Calcola data ieri (timezone Roma)
  │     │     ├─► Apri date picker
  │     │     ├─► Imposta data inizio = ieri
  │     │     ├─► Imposta data fine = ieri
  │     │     └─► Applica
  │     │
  │     ├─► 4.7 Aggiornamento Dati
  │     │     └─► Click "Aggiornamento dati" button
  │     │
  │     ├─► 4.8 Download Excel
  │     │     ├─► Scroll a download button
  │     │     ├─► Click download XLSX
  │     │     ├─► Attendi file in downloads/
  │     │     └─► Verifica completamento download
  │     │
  │     ├─► 4.9 Upload Google Sheets
  │     │     ├─► Autenticazione service account
  │     │     ├─► Parse file Excel
  │     │     ├─► Cancella sheet esistente
  │     │     ├─► Upload nuovi dati
  │     │     └─► Formattazione headers (bold)
  │     │
  │     ├─► 4.10 Salvataggio Log
  │     │     ├─► Crea entry LocaleLog
  │     │     ├─► successo = true/false
  │     │     ├─► messaggio = descrizione
  │     │     ├─► file_scaricato = path
  │     │     └─► sheet_aggiornato = true/false
  │     │
  │     └─► 4.11 Reset Flag
  │           └─► esegui_ora = false
  │
  ├─► 5. Commit Database
  │     ├─► git add data/locali.db
  │     ├─► git commit -m "Update execution logs"
  │     └─► git push
  │
  └─► END
```

### Selettori CSS Configurabili

**File:** `config.json`

```json
{
  "dashboard": {
    "login_url": "https://dashboard.ipratico.com/login"
  },
  "selectors": {
    "username_field": "input[name='email']",
    "password_field": "input[name='password']",
    "login_button": "button[type='submit']",
    "secret_popup_trigger": "footer.footer",
    "secret_pin_field": "input#secret-pin",
    "secret_pin_confirm": "button#confirm-secret",
    "menu_main": "a[href='#/reports']",
    "menu_submenu": "a[href='#/reports/daily']",
    "locale_dropdown_button": "button#locale-selector",
    "date_filter_trigger": "button.date-filter",
    "date_start_input": "input#date-start",
    "date_end_input": "input#date-end",
    "date_apply_button": "button.apply-date",
    "aggiornamento_dati_button": "button.refresh-data",
    "download_xlsx_button": "a[download*='.xlsx']"
  },
  "navigation": {
    "wait_after_login": 3,
    "wait_after_pin": 2,
    "wait_after_menu_click": 2,
    "wait_after_locale_select": 2,
    "wait_after_date_select": 2,
    "wait_after_aggiornamento": 3,
    "secret_popup_clicks": 3
  }
}
```

**Come aggiornare i selettori:**

Se la struttura della pagina iPratico cambia:

1. **Ispeziona elemento** nel browser
2. **Copia selettore CSS**
3. **Aggiorna config.json**
4. **Commit e push**
5. Il bot userà i nuovi selettori automaticamente

---

## ⚙️ Configurazione

### Variabili d'Ambiente

#### Backend (Render)

| Variabile | Descrizione | Esempio | Obbligatorio |
|-----------|-------------|---------|--------------|
| `ENCRYPTION_KEY` | Chiave Fernet per cifrare password | `gAAAAAB...` | ✅ Sì |
| `GITHUB_TOKEN` | Token per triggerare workflow | `ghp_xxx...` | ✅ Sì (per esegui-ora) |
| `GITHUB_REPOSITORY` | Nome repository GitHub | `ChatMano/chatbot` | ⚠️ Opzionale (default già impostato) |
| `DATABASE_URL` | URL database SQLite | `sqlite:///locali.db` | ⚠️ Opzionale (default già impostato) |
| `SECRET_KEY` | Flask secret key | `random-string` | ⚠️ Opzionale (default già impostato) |
| `PORT` | Porta server | `5000` | ⚠️ Opzionale (Render la imposta) |

**Come generare ENCRYPTION_KEY:**
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Come generare GITHUB_TOKEN:**
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Scopes: `repo`, `workflow`
4. Copy token

#### GitHub Actions (Secrets)

| Secret | Descrizione | Dove trovarlo |
|--------|-------------|---------------|
| `ENCRYPTION_KEY` | Stesso di Render | Generato con Fernet |
| `GOOGLE_CREDENTIALS_JSON` | Service account Google | Google Cloud Console |

**Dove configurare:**
1. GitHub → Repository → Settings → Secrets and variables → Actions
2. New repository secret
3. Nome: `ENCRYPTION_KEY`
4. Value: (copia da Render o genera nuovo)

#### Frontend (Netlify)

| Variabile | Descrizione | Esempio |
|-----------|-------------|---------|
| `VITE_API_URL` | URL backend API | `https://pratico-backend-gzp6.onrender.com/api` |

**Dove configurare:**
1. Netlify → Site settings → Environment variables
2. Add variable
3. `VITE_API_URL` = URL backend

### Google Sheets API Setup

**1. Crea Service Account:**

```bash
# Google Cloud Console
1. Crea progetto (o usa esistente)
2. Abilita Google Sheets API
3. IAM & Admin → Service Accounts → Create Service Account
4. Nome: "Pratico Bot"
5. Grant role: Editor (opzionale)
6. Create key → JSON
7. Download JSON
```

**2. Configura Secret:**

```bash
# Copia contenuto del file JSON
cat service-account.json | pbcopy  # Mac
cat service-account.json | xclip   # Linux

# GitHub → Secrets → GOOGLE_CREDENTIALS_JSON
# Incolla il contenuto JSON
```

**3. Condividi Google Sheets:**

```
1. Apri il Google Sheet
2. Click "Share"
3. Aggiungi email del service account:
   Example: pratico-bot@project-id.iam.gserviceaccount.com
4. Role: Editor
5. Send
```

**Trova email service account:**
```bash
cat service-account.json | grep client_email
```

---

## 🐛 Problemi Risolti

### Sessione 30 Ottobre 2025

#### 1. ❌ Nessuna Logica di Riconnessione
**Problema:** Richieste HTTP fallivano senza retry, timeout Selenium causavano crash immediato

**Soluzione:**
- **Frontend:** Axios interceptor con retry automatico (exponential backoff)
  - File: `frontend/src/utils/axiosConfig.js`
  - Retry su errori di rete e 5xx
  - 3 tentativi con delay: 2s, 4s, 8s

- **Backend:** Decorator `@retry_request` per chiamate esterne
  - File: `backend/retry_utils.py`
  - Retry per GitHub API calls

- **Bot:** Decorator `@retry_selenium` per operazioni Selenium
  - File: `bot/retry_selenium.py`
  - Retry su TimeoutException, NoSuchElementException, etc.

**Commit:** `0b20101` - "Implementa logica di riconnessione automatica..."

#### 2. ❌ Pulsante "Esegui Ora" Non Funzionava
**Problema iniziale:** Tentativo di eseguire bot con subprocess.Popen non compatibile con Render

**Prima soluzione (fallita):**
```python
# Non funziona su Render (ambiente limitato)
subprocess.Popen([sys.executable, 'run_bot.py'], ...)
```

**Soluzione corretta:**
```python
# Trigger GitHub Actions via API
requests.post(
    f'https://api.github.com/repos/{repo}/actions/workflows/daily-download.yml/dispatches',
    json={'ref': 'main', 'inputs': {'locale_id': str(locale_id)}},
    headers={'Authorization': f'Bearer {GITHUB_TOKEN}'}
)
```

**Commit:** `51cbf7a` - "Fix: Trigger immediato workflow GitHub Actions..."

#### 3. ❌ Database Mancante Colonna `esegui_ora`
**Problema:** Bot crashava su GitHub Actions con:
```
sqlite3.OperationalError: no such column: locali.esegui_ora
```

**Causa:** Database locale aveva la colonna, ma database su GitHub Actions no (versione vecchia committata)

**Soluzione:**
- Creato `migrate_db.py` - script di migrazione automatica
- Aggiunto step nel workflow: "Migrate database"
- Script verifica se colonna esiste, se no la aggiunge
- Idempotente: può essere eseguito più volte senza problemi

**Commit:** `5c4f1de` - "Fix: Aggiungi migrazione database per colonna esegui_ora"

**Workflow step aggiunto:**
```yaml
- name: Migrate database (add esegui_ora column if missing)
  run: |
    python migrate_db.py
```

---

## 📁 Struttura del Progetto

```
chatbot/
│
├── .github/
│   └── workflows/
│       └── daily-download.yml          # GitHub Actions workflow
│
├── backend/
│   ├── __init__.py
│   ├── app.py                          # Flask application (API endpoints)
│   ├── models.py                       # SQLAlchemy models (Locale, LocaleLog)
│   ├── crypto.py                       # Encryption/Decryption (Fernet)
│   ├── retry_utils.py                  # Retry decorator per HTTP
│   ├── requirements.txt                # Python dependencies
│   └── .env.example                    # Example environment variables
│
├── bot/
│   ├── __init__.py
│   ├── scraper.py                      # Selenium bot (DashboardScraper)
│   ├── google_sheets.py                # Google Sheets uploader
│   ├── config_manager.py               # Config loader (config.json)
│   ├── auth.py                         # Auth manager
│   └── retry_selenium.py               # Retry decorator per Selenium
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                     # Main React component
│   │   ├── main.jsx                    # Entry point
│   │   ├── components/
│   │   │   ├── LocaleList.jsx          # Lista locali
│   │   │   ├── LocaleCard.jsx          # Card singolo locale
│   │   │   └── LocaleForm.jsx          # Form crea/modifica locale
│   │   ├── utils/
│   │   │   └── axiosConfig.js          # Axios con retry interceptor
│   │   └── index.css                   # Styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
├── data/
│   └── locali.db                       # SQLite database (committato su Git)
│
├── downloads/                          # File Excel scaricati (temporanei)
│
├── config.json                         # Selettori CSS e configurazione bot
├── migrate_db.py                       # Script migrazione database
├── run_bot.py                          # Entry point bot (eseguito da GitHub Actions)
├── requirements.txt                    # Python dependencies (root)
├── render.yaml                         # Configurazione Render
├── netlify.toml                        # Configurazione Netlify
│
├── README.md                           # Documentazione base
├── README_DASHBOARD.md                 # Documentazione dashboard
└── PROJECT_OVERVIEW.md                 # QUESTO FILE
```

### File Chiave

| File | Descrizione | Quando Modificare |
|------|-------------|-------------------|
| `backend/app.py` | API endpoints | Aggiungere nuovi endpoint, modificare logica backend |
| `backend/models.py` | Database models | Aggiungere nuovi campi al database |
| `bot/scraper.py` | Logica Selenium | iPratico cambia struttura, nuovi step necessari |
| `config.json` | Selettori CSS | iPratico cambia HTML/CSS, selettori non funzionano più |
| `migrate_db.py` | Migrazioni DB | Nuove colonne da aggiungere al database |
| `.github/workflows/daily-download.yml` | CI/CD | Cambiare schedule, aggiungere step, modificare triggers |
| `frontend/src/utils/axiosConfig.js` | HTTP retry | Modificare strategia retry, timeout |

---

## 🔍 Debug e Troubleshooting

### Frontend Non Si Connette al Backend

**Sintomo:** Errore CORS, o errore di rete

**Debug:**
```bash
# 1. Verifica che backend sia online
curl https://pratico-backend-gzp6.onrender.com/api/health

# 2. Verifica VITE_API_URL
# Netlify → Environment variables
# Deve essere: https://pratico-backend-gzp6.onrender.com/api

# 3. Controlla console browser (F12)
# Errore CORS → Backend non ha CORS abilitato
# Errore 404 → URL backend errato
```

### Bot Fallisce su GitHub Actions

**Sintomo:** Workflow run fallisce

**Debug:**
```bash
# 1. Apri workflow run su GitHub
https://github.com/ChatMano/chatbot/actions

# 2. Click sul run fallito

# 3. Espandi ogni step per vedere errori

# Errori comuni:
# - "no such column" → Migrazione database non eseguita
# - "ENCRYPTION_KEY not found" → Secret mancante
# - "TimeoutException" → Selettore CSS cambiato o timeout troppo corto
# - "No such element" → Selettore CSS errato
# - "Google auth failed" → GOOGLE_CREDENTIALS_JSON errato
```

### Selettori CSS Non Funzionano Più

**Sintomo:** Bot fallisce con "NoSuchElementException"

**Come Fixare:**

```bash
# 1. Apri iPratico dashboard nel browser
# 2. Login manuale
# 3. Naviga alla pagina dove il bot fallisce
# 4. Click destro sull'elemento → Inspect
# 5. Click destro sull'HTML → Copy → Copy selector
# 6. Aggiorna config.json con nuovo selettore

# Esempio:
{
  "selectors": {
    "download_xlsx_button": "a.new-download-btn[download*='.xlsx']"
    #                        ^^^ nuovo selettore
  }
}

# 7. Commit e push
git add config.json
git commit -m "Update download button selector"
git push
```

### Database Non Si Aggiorna

**Sintomo:** Modifiche nel backend non visibili nel frontend

**Debug:**

```bash
# 1. Verifica che database sia committato
cd data/
ls -la locali.db
git status

# 2. Se non committato:
git add data/locali.db
git commit -m "Update database"
git push

# 3. Verifica via API:
curl https://pratico-backend-gzp6.onrender.com/api/locali/1

# 4. Se ancora vecchio:
# Render potrebbe aver cachato vecchia versione
# Render Dashboard → Manual Deploy → Deploy latest commit
```

### "Esegui Ora" Non Parte

**Sintomo:** Click "Esegui Ora" ma workflow non parte

**Debug:**

```bash
# 1. Verifica GITHUB_TOKEN configurato su Render
# Render → pratico-backend → Environment → GITHUB_TOKEN

# 2. Verifica permessi token
# GitHub → Settings → Developer settings → Tokens
# Scopes richiesti: repo, workflow

# 3. Verifica log backend (Render)
# Render → pratico-backend → Logs
# Cerca: "Trigger immediato GitHub Actions"

# 4. Se vedi "GITHUB_TOKEN non configurato":
# Aggiungi variabile d'ambiente su Render

# 5. Se vedi "Errore GitHub API (status 401)":
# Token scaduto o permessi insufficienti → rigenera token

# 6. Se vedi "Errore GitHub API (status 404)":
# Repository o workflow file non trovato → verifica GITHUB_REPOSITORY
```

### Logs Completi per Debug

**Dove trovarli:**

1. **Frontend (Browser):**
   ```
   F12 → Console
   Vedi: richieste axios, retry attempts, errori
   ```

2. **Backend (Render):**
   ```
   https://dashboard.render.com
   → pratico-backend → Logs (real-time)
   ```

3. **GitHub Actions:**
   ```
   https://github.com/ChatMano/chatbot/actions
   → Click su workflow run → Espandi step
   ```

4. **Database (SQLite):**
   ```bash
   # Locale
   sqlite3 data/locali.db
   SELECT * FROM locale_logs ORDER BY eseguito_at DESC LIMIT 10;

   # Via API
   curl https://pratico-backend-gzp6.onrender.com/api/locali/1/logs
   ```

---

## 🚀 Prossimi Sviluppi

### Idee per Miglioramenti Futuri

#### 1. Modifiche al Percorso del Bot

**Scenario:** iPratico cambia struttura menu o aggiunge nuovi step

**Come Implementare:**

```python
# bot/scraper.py

# Aggiungere nuovo step nella sequenza
def nuovo_step_custom(self):
    """Nuovo step personalizzato"""
    try:
        selectors = self.config.get_selectors()

        # 1. Click su nuovo elemento
        new_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selectors.get('new_button')))
        )
        new_button.click()
        time.sleep(2)

        return True
    except TimeoutException:
        print("Errore: Timeout nuovo step")
        return False

# Aggiungere chiamata in run()
def run(self, pin, locale_selector):
    # ... existing steps ...

    # Nuovo step
    if not self.nuovo_step_custom():
        return None

    # ... continue ...
```

**Poi aggiorna config.json:**
```json
{
  "selectors": {
    "new_button": "button#custom-action"
  }
}
```

#### 2. Notifiche Email/Telegram

**Scenario:** Inviare notifica quando esecuzione completa o fallisce

**Implementazione:**

```python
# bot/notifier.py
import smtplib
from email.mime.text import MIMEText

def send_email_notification(locale_name, success, message):
    msg = MIMEText(f"Locale: {locale_name}\nSuccesso: {success}\nMessaggio: {message}")
    msg['Subject'] = f'Bot Execution: {locale_name}'
    msg['From'] = 'bot@pratico.com'
    msg['To'] = 'admin@pratico.com'

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
        server.send_message(msg)

# In run_bot.py dopo process_locale()
if log_entry.successo:
    send_email_notification(locale.nome, True, log_entry.messaggio)
else:
    send_email_notification(locale.nome, False, log_entry.messaggio)
```

#### 3. Dashboard Analytics

**Scenario:** Grafici di statistiche esecuzioni

**Endpoint backend:**
```python
@app.route('/api/stats/analytics', methods=['GET'])
def get_analytics():
    # Ultimi 30 giorni
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Esecuzioni per locale
    logs = LocaleLog.query.filter(
        LocaleLog.eseguito_at >= thirty_days_ago
    ).all()

    # Raggruppa per locale
    stats_per_locale = {}
    for log in logs:
        locale_name = log.locale.nome
        if locale_name not in stats_per_locale:
            stats_per_locale[locale_name] = {'successi': 0, 'fallimenti': 0}

        if log.successo:
            stats_per_locale[locale_name]['successi'] += 1
        else:
            stats_per_locale[locale_name]['fallimenti'] += 1

    return jsonify(stats_per_locale)
```

**Frontend (Chart.js):**
```jsx
import { Chart } from 'chart.js';

function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState({});

  useEffect(() => {
    axios.get('/api/stats/analytics')
      .then(res => setAnalytics(res.data));
  }, []);

  // Render charts...
}
```

#### 4. Configurazione Multi-Formato Download

**Scenario:** Alcuni locali vogliono PDF invece di Excel

**Implementazione:**

```python
# backend/models.py
class Locale(db.Model):
    # ... existing fields ...
    download_format = db.Column(db.String(10), default='xlsx')  # 'xlsx' or 'pdf'

# bot/scraper.py
def download_file(self, format='xlsx'):
    selectors = self.config.get_selectors()

    if format == 'xlsx':
        button_selector = selectors.get('download_xlsx_button')
    elif format == 'pdf':
        button_selector = selectors.get('download_pdf_button')

    download_button = self.wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
    )
    download_button.click()
    # ... rest of download logic ...
```

#### 5. Backup Automatico Database

**Scenario:** Backup periodico su cloud storage

**Implementazione:**

```yaml
# .github/workflows/backup-db.yml
name: Backup Database

on:
  schedule:
    - cron: '0 0 * * 0'  # Ogni domenica mezzanotte

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create backup
        run: |
          mkdir -p backups
          cp data/locali.db backups/locali_$(date +%Y%m%d).db

      - name: Upload to S3
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-1

      - run: |
          aws s3 cp backups/ s3://pratico-backups/ --recursive
```

#### 6. Webhook per Eventi

**Scenario:** Triggerare azioni esterne quando bot completa

**Implementazione:**

```python
# backend/models.py
class Locale(db.Model):
    # ... existing fields ...
    webhook_url = db.Column(db.String(500), nullable=True)

# run_bot.py - dopo process_locale()
if locale.webhook_url:
    try:
        requests.post(locale.webhook_url, json={
            'locale_id': locale.id,
            'locale_name': locale.nome,
            'success': log_entry.successo,
            'message': log_entry.messaggio,
            'timestamp': log_entry.eseguito_at.isoformat()
        }, timeout=5)
    except:
        print(f"Webhook fallito per {locale.nome}")
```

---

## 📞 Contatti e Supporto

### In Caso di Problemi

1. **Controlla i log:**
   - Frontend: Browser Console (F12)
   - Backend: Render Dashboard → Logs
   - Bot: GitHub Actions → Workflow run logs

2. **Verifica configurazione:**
   - Variabili d'ambiente (Render, Netlify, GitHub Secrets)
   - config.json (selettori CSS)
   - Database (via API `/api/locali`)

3. **Problemi comuni risolti:** Vedi sezione "Debug e Troubleshooting"

### Repository

**GitHub:** https://github.com/ChatMano/chatbot

### Deployment URLs

- **Frontend:** https://pratico-dashboard.netlify.app (sostituisci con URL reale)
- **Backend:** https://pratico-backend-gzp6.onrender.com
- **GitHub Actions:** https://github.com/ChatMano/chatbot/actions

---

## 📝 Note Finali

### Per Riprendere in Nuova Chat

Quando apri una nuova chat per continuare lo sviluppo:

1. **Condividi questo file** (`PROJECT_OVERVIEW.md`)
2. **Specifica cosa vuoi modificare:**
   - Modifiche al percorso bot (selettori CSS)
   - Nuove funzionalità
   - Bug fix
   - Ottimizzazioni

3. **Informazioni utili da includere:**
   - Errore specifico (se debug)
   - Logs (GitHub Actions, Render, Browser)
   - Cosa hai già provato
   - Comportamento atteso vs. comportamento attuale

### Esempio Messaggio per Nuova Chat

```
Ciao! Sto lavorando sul progetto Pratico Dashboard.

Ecco il file PROJECT_OVERVIEW.md con tutta la documentazione:
[incolla contenuto o link]

Problema/Richiesta:
[descrivi cosa vuoi fare]

Esempio:
"Il bot fallisce su iPratico perché hanno cambiato il selettore del pulsante download.
Devo aggiornare il selettore CSS in config.json. Ecco l'errore da GitHub Actions:
[incolla log errore]"
```

---

**Documento creato il:** 30 Ottobre 2025
**Versione sistema:** 1.0 - Funzionante e in produzione
**Ultimo deploy:** 30 Ottobre 2025

---

🎉 **Sistema completamente funzionante!** 🎉
