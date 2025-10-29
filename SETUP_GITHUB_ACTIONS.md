# Configurazione GitHub Actions per Automazione Bot

## 1. Preparazione Credenziali Google

1. **Apri il file `credentials.json`** scaricato da Google Cloud Console
2. **Copia tutto il contenuto del file** (è un JSON)

## 2. Configurazione Secrets su GitHub

Vai su GitHub nel tuo repository:

**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Aggiungi i seguenti secrets:

### Secret 1: GOOGLE_CREDENTIALS_JSON
- **Name**: `GOOGLE_CREDENTIALS_JSON`
- **Value**: Incolla tutto il contenuto di `credentials.json`
- Click **Add secret**

### Secret 2: IPRATICO_USERNAME
- **Name**: `IPRATICO_USERNAME`
- **Value**: Il tuo username iPratico (es: `info@pizzeriaveneta.it`)
- Click **Add secret**

### Secret 3: IPRATICO_PASSWORD
- **Name**: `IPRATICO_PASSWORD`
- **Value**: La tua password iPratico
- Click **Add secret**

### Secret 4: IPRATICO_PIN
- **Name**: `IPRATICO_PIN`
- **Value**: Il PIN del popup segreto (es: `123456`)
- Click **Add secret**

### Secret 5: IPRATICO_LOCALE_SELECTOR
- **Name**: `IPRATICO_LOCALE_SELECTOR`
- **Value**: Selettore CSS del locale (es: `#wrapper > div.content-page > div > div:nth-child(3) > div > div > div > div:nth-child(1) > div > ul > li:nth-child(3) > a > label`)
- Click **Add secret**

### Secret 6: GOOGLE_SHEET_ID
- **Name**: `GOOGLE_SHEET_ID`
- **Value**: L'ID del tuo Google Sheet (es: `1JDDcYoHkG5LTbB8w2tyMr8CcFc7l4ITsf9eYSVLwSNs`)
- Click **Add secret**

## 3. Verifica Configurazione

Dopo aver aggiunto tutti i secrets:

1. Vai su **Actions** nel repository
2. Seleziona **iPratico Daily Download**
3. Click su **Run workflow** → **Run workflow**
4. Aspetta il completamento (2-3 minuti)
5. Controlla che il Google Sheet sia aggiornato

## 4. Esecuzione Automatica

Il bot eseguirà automaticamente **ogni giorno alle 23:00 UTC (01:00 ora italiana)**.

Per cambiare l'orario, modifica il file `.github/workflows/daily-download.yml`:

```yaml
schedule:
  - cron: '0 23 * * *'  # 23:00 UTC
```

Esempi:
- `0 22 * * *` = 22:00 UTC (00:00 ora italiana)
- `30 21 * * *` = 21:30 UTC (23:30 ora italiana)
- `0 6 * * *` = 06:00 UTC (08:00 ora italiana)

## 5. Monitoraggio

Per vedere lo stato delle esecuzioni:

1. Vai su **Actions**
2. Seleziona **iPratico Daily Download**
3. Vedrai tutte le esecuzioni passate
4. Click su una esecuzione per vedere i log dettagliati

## 6. Multi-Locale (Futuro)

Per gestire più locali:
- Creare più workflow files (uno per locale)
- Oppure modificare il database per leggere da lì
- Oppure usare matrix strategy in GitHub Actions

## Troubleshooting

**Se il bot fallisce:**
1. Controlla i logs su GitHub Actions
2. Verifica che tutti i secrets siano corretti
3. Testa manualmente con `python run_bot.py` in locale

**Se mancano dati:**
- Verifica che il selettore del locale sia corretto
- Controlla che il PIN sia valido
- Verifica che le credenziali siano corrette
