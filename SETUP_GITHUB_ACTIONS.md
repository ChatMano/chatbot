# Configurazione GitHub Actions per Automazione Bot

## Architettura Multi-Locale 🎯

Il bot legge le configurazioni dei locali **dal database** che gestisci tramite il frontend React.
**Non serve configurare username/password su GitHub per ogni locale!**

Tutto viene gestito dal frontend:
- ✅ Username e password (cifrati nel database)
- ✅ PIN iPratico (cifrato nel database)
- ✅ Selettore locale
- ✅ Google Sheet ID
- ✅ Orario esecuzione

## 1. Ottieni la ENCRYPTION_KEY

La chiave di cifratura si trova nel file `backend/.env`.

Oppure genera una nuova chiave con Python:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Copia la chiave (es: `gAAAAABh_xK...`)

## 2. Preparazione Credenziali Google

1. **Apri il file `credentials.json`** scaricato da Google Cloud Console
2. **Copia tutto il contenuto del file** (è un JSON completo)

## 3. Configurazione Secrets su GitHub

Vai su GitHub nel tuo repository:

**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Aggiungi **SOLO QUESTI 2 SECRETS**:

### Secret 1: GOOGLE_CREDENTIALS_JSON
- **Name**: `GOOGLE_CREDENTIALS_JSON`
- **Value**: Incolla tutto il contenuto di `credentials.json`
- Click **Add secret**

### Secret 2: ENCRYPTION_KEY
- **Name**: `ENCRYPTION_KEY`
- **Value**: La chiave di cifratura dal `backend/.env`
- Click **Add secret**

**Fatto! Solo 2 secrets!** 🎉

Tutti gli altri dati (username, password, PIN, locali, Google Sheet ID) vengono gestiti dal frontend e salvati nel database cifrato.

## 4. Aggiungi il Database al Repository

Il database contiene le credenziali cifrate e deve essere nel repository:

```bash
git add data/locali.db
git commit -m "Add encrypted database"
git push
```

Il database è **sicuro** perché:
- ✅ Le password sono cifrate con ENCRYPTION_KEY
- ✅ Solo chi ha la ENCRYPTION_KEY può decifrare
- ✅ La chiave è su GitHub Secrets (non nel repo)

## 5. Verifica Configurazione

Dopo aver aggiunto i 2 secrets e pushato il database:

1. Vai su **Actions** nel repository
2. Seleziona **iPratico Daily Download**
3. Click su **Run workflow** → **Run workflow**
4. Aspetta il completamento (2-5 minuti)
5. Controlla che i Google Sheets siano aggiornati

## 6. Esecuzione Automatica

Il bot eseguirà automaticamente **ogni giorno alle 23:00 UTC (01:00 ora italiana)**.

Per cambiare l'orario, modifica `.github/workflows/daily-download.yml`:

```yaml
schedule:
  - cron: '0 23 * * *'  # 23:00 UTC = 01:00 ora italiana
```

Esempi:
- `0 22 * * *` = 22:00 UTC (00:00 ora italiana)
- `30 21 * * *` = 21:30 UTC (23:30 ora italiana)
- `0 6 * * *` = 06:00 UTC (08:00 ora italiana)

## 7. Gestione Multi-Locale

### Aggiungere un nuovo locale:

1. **Apri il frontend React** (già funzionante)
2. **Aggiungi nuovo locale** con username, password, PIN, Google Sheet ID
3. **Salva** → le credenziali vengono cifrate nel database
4. **Committa il database aggiornato:**

```bash
git add data/locali.db
git commit -m "Add new locale: Nome Pizzeria"
git push
```

5. **Fatto!** La prossima notte il bot eseguirà anche il nuovo locale

### Modificare un locale esistente:

1. Modifica dal frontend
2. Committa il database aggiornato
3. Push

**Nessuna modifica a GitHub Actions richiesta!**

## 8. Monitoraggio

Per vedere lo stato delle esecuzioni:

1. Vai su **Actions** nel repository
2. Seleziona **iPratico Daily Download**
3. Vedrai tutte le esecuzioni passate
4. Click su una esecuzione per vedere:
   - Quali locali sono stati processati
   - Quali hanno successo (✓)
   - Quali hanno fallito (✗)
   - Log dettagliati per ogni locale

I log vengono anche salvati nel database e visibili dal frontend!

## 9. Troubleshooting

**Se il bot fallisce:**
1. Controlla i logs su GitHub Actions
2. Verifica che `ENCRYPTION_KEY` sia corretta
3. Verifica che `GOOGLE_CREDENTIALS_JSON` sia completo
4. Testa localmente: `ENCRYPTION_KEY=xxx python run_bot.py`

**Se un locale specifico fallisce:**
1. Controlla i log nel frontend (sezione Logs)
2. Verifica credenziali username/password
3. Verifica che il selettore locale sia corretto
4. Verifica che il Google Sheet ID sia corretto e condiviso

**Errore "ENCRYPTION_KEY non configurata":**
- Aggiungi il secret su GitHub Actions

**Errore "Nessun locale attivo trovato":**
- Verifica che ci sia almeno un locale attivo nel database
- Committa e pusha il database

## 10. Backup e Sicurezza

**Il database è sicuro:**
- ✅ Passwords cifrate con Fernet (AES-128)
- ✅ Chiave di cifratura solo su GitHub Secrets
- ✅ Anche se qualcuno clona il repo, non può decifrare

**Backup automatico:**
- ✅ Il database è versionato su Git
- ✅ Ogni modifica è tracciata
- ✅ Puoi tornare a versioni precedenti

**Per massima sicurezza:**
- Non condividere `ENCRYPTION_KEY`
- Rigenera `ENCRYPTION_KEY` se viene compromessa
- Mantieni privato il repository GitHub
