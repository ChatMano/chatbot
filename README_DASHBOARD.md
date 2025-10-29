# Pratico - Sistema Multi-Locale per Download & Upload Automatico

Sistema completo per gestire il download automatico di file Excel da iPratico Cloud e caricamento su Google Sheets per più locali.

## 🏗️ Architettura

```
┌─────────────────────┐
│  React Dashboard    │  Frontend per gestione locali
│  (Port 5173)        │  http://localhost:5173
└──────────┬──────────┘
           │ REST API
           ▼
┌─────────────────────┐
│  Flask Backend      │  Backend API
│  (Port 5000)        │  http://localhost:5000
│  + SQLite DB        │
└──────────┬──────────┘
           │ gestisce config
           ▼
┌─────────────────────┐
│  Bot Selenium       │  Download automatico
│  + Google Sheets    │  Upload su Sheets
└─────────────────────┘
```

## 🚀 Setup Iniziale

### 1. Installa dipendenze backend

```bash
cd backend
python -m venv venv

# Attiva virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configura backend

```bash
cp .env.example .env
# Modifica .env se necessario
```

### 3. Installa dipendenze frontend

```bash
cd frontend
npm install
```

### 4. Configura frontend

```bash
cp .env.example .env
# Modifica .env se necessario (di default punta a localhost:5000)
```

### 5. Configura Google Sheets API

Per usare Google Sheets hai due opzioni:

#### Opzione A: Service Account (per automazione - consigliato)

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto
3. Abilita **Google Sheets API**
4. Vai su "IAM & Admin" → "Service Accounts"
5. Crea un nuovo service account
6. Genera una chiave JSON
7. Scarica il file e rinominalo `service-account.json`
8. Mettilo nella root del progetto

**Importante**: Condividi i tuoi Google Sheets con l'email del service account (trovi l'email nel file JSON)

#### Opzione B: OAuth (per uso locale/interattivo)

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto
3. Abilita **Google Sheets API**
4. Vai su "APIs & Services" → "Credentials"
5. Crea credenziali OAuth 2.0 per "Desktop app"
6. Scarica il file JSON e rinominalo `credentials.json`
7. Mettilo nella root del progetto

## 🎯 Utilizzo

### Avvia il backend

```bash
cd backend
python app.py
```

Backend disponibile su: http://localhost:5000

### Avvia il frontend

In un nuovo terminale:

```bash
cd frontend
npm run dev
```

Frontend disponibile su: http://localhost:5173

### Usa la Dashboard

1. Apri http://localhost:5173
2. Clicca "Aggiungi Locale"
3. Compila il form:
   - **Nome Locale**: Es. "Roma Centro"
   - **Username**: Username iPratico
   - **Password**: Password iPratico
   - **Orario Esecuzione**: Es. "03:00" (formato 24h)
   - **Google Sheet ID**: ID del foglio Google Sheets
     - Esempio: da `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit`
     - L'ID è: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
   - **Selettore Locale** (opzionale): Selettore CSS o URL per identificare il locale su iPratico
   - **Attivo**: Spunta se vuoi che il locale sia attivo

4. Salva!

## 🤖 Bot Automatico

### Esecuzione manuale per un locale

```bash
# Dalla root del progetto
python -c "
from bot.scraper import DashboardScraper
from bot.auth import AuthManager
from bot.config_manager import ConfigManager
from bot.google_sheets import GoogleSheetsUploader

config = ConfigManager()
auth = AuthManager()

# Download
scraper = DashboardScraper(config, auth)
file_path = scraper.run()

# Upload su Sheets
if file_path:
    uploader = GoogleSheetsUploader()
    if uploader.authenticate(use_service_account=True):
        uploader.write_excel_to_sheet(
            file_path,
            'YOUR_SHEET_ID',
            worksheet_name='Sheet1',
            clear_existing=True
        )
"
```

### Automazione con GitHub Actions

Creeremo un workflow GitHub Actions che:
- Si esegue automaticamente ogni notte
- Legge tutti i locali attivi dal database
- Per ogni locale:
  1. Fa login su iPratico
  2. Scarica il file Excel
  3. Lo carica su Google Sheets
  4. Registra il log nel database

## 📊 API Endpoints

### Locali

- `GET /api/locali` - Lista tutti i locali
- `GET /api/locali/:id` - Ottieni un locale
- `POST /api/locali` - Crea un nuovo locale
- `PUT /api/locali/:id` - Aggiorna un locale
- `DELETE /api/locali/:id` - Elimina un locale
- `GET /api/locali/:id/credentials` - Ottieni credenziali decifrate (per il bot)
- `GET /api/locali/:id/logs` - Ottieni i log di un locale
- `POST /api/locali/:id/log` - Crea un nuovo log (per il bot)

### Statistiche

- `GET /api/stats` - Statistiche generali

### Health Check

- `GET /api/health` - Verifica stato del backend

## 🗄️ Database

Il sistema usa SQLite per memorizzare:

- **Locali**: Nome, credenziali (cifrate), orari, configurazione
- **Log**: Storico esecuzioni con successi/errori

Database location: `data/locali.db`

## 🔒 Sicurezza

- Le password sono cifrate usando `cryptography` (Fernet)
- La chiave di cifratura è in `SECRET_KEY` (file .env)
- **IMPORTANTE**: Cambia la `SECRET_KEY` in produzione!
- Non committare mai:
  - `credentials.json` (OAuth)
  - `service-account.json` (Service Account)
  - `token.json` (token OAuth)
  - File `.env`
  - Database `data/locali.db`

## 🚢 Deploy (Gratuito)

### Backend → Render.com

1. Crea account su [Render.com](https://render.com)
2. Collega il repository GitHub
3. Crea un nuovo "Web Service"
4. Seleziona `backend/` come root directory
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn app:app`
7. Aggiungi variabili d'ambiente:
   - `SECRET_KEY`: una chiave sicura
   - `DATABASE_URL`: lascia default (SQLite)

### Frontend → Netlify

1. Crea account su [Netlify](https://netlify.com)
2. Collega il repository GitHub
3. Build settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
4. Aggiungi variabile d'ambiente:
   - `VITE_API_URL`: URL del backend su Render

### Bot → GitHub Actions

Creeremo un workflow che si esegue automaticamente. Istruzioni nella prossima fase.

## 🧪 Test

### Test login iPratico

```bash
python test_login.py
```

### Test backend API

```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/locali
```

### Test frontend

Apri http://localhost:5173 nel browser

## 📝 Note

- Il sistema è completamente **gratuito** usando i servizi cloud gratuiti
- Backend Render: sleep dopo 15 min inattività (si risveglia in ~30s)
- GitHub Actions: 2000 minuti/mese gratis (abbondanti per questo uso)
- Google Sheets API: quota giornaliera generosa gratuita

## 🆘 Troubleshooting

### Backend non si avvia

- Verifica che il virtual environment sia attivo
- Verifica che tutte le dipendenze siano installate: `pip install -r requirements.txt`
- Controlla i log per errori

### Frontend non si connette al backend

- Verifica che il backend sia in esecuzione su porta 5000
- Controlla il file `frontend/.env` che `VITE_API_URL` punti a `http://localhost:5000/api`
- Controlla la console del browser per errori CORS

### Bot non riesce a scaricare

- Verifica che Chrome sia installato
- Verifica i selettori CSS in `config.json`
- Esegui `python test_login.py` per testare solo il login

### Errori Google Sheets

- Verifica di aver configurato correttamente il service account o OAuth
- Verifica di aver condiviso il foglio Google Sheets con l'email del service account
- Controlla che le API siano abilitate su Google Cloud Console

## 📞 Supporto

Per problemi, apri una issue sul repository GitHub.
