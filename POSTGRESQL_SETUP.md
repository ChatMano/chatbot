# 🗄️ Migrazione a PostgreSQL su Render - Guida Completa

**Problema:** Il database SQLite su Render viene cancellato ad ogni deploy (filesystem effimero)

**Soluzione:** Usare PostgreSQL (gratuito su Render e **persistente**)

---

## ⚡ Setup Veloce (5 minuti)

### **STEP 1: Crea Database PostgreSQL su Render**

1. **Apri Render Dashboard:**
   ```
   https://dashboard.render.com
   ```

2. **Click "New +" in alto a destra**

3. **Seleziona "PostgreSQL"**

4. **Compila il form:**
   - **Name:** `pratico-database`
   - **Database:** `pratico_db`
   - **User:** `pratico_user` (o lascia default)
   - **Region:** `Frankfurt` ⚠️ **IMPORTANTE**: Stesso del backend!
   - **PostgreSQL Version:** `16` (latest)
   - **Datadog API Key:** (lascia vuoto)
   - **Plan:** **`Free`** ✅

5. **Click "Create Database"**

6. **Aspetta 1-2 minuti** - apparirà "Available" quando pronto

---

### **STEP 2: Collega Database al Backend**

1. **Nella dashboard del database**, vai alla sezione **"Connect"** (in alto)

2. **Copia "Internal Database URL"** (NON External):
   ```
   postgres://pratico_user:xxxxxxxx@dpg-xxxxx-a/pratico_db
   ```

   ⚠️ **Usa INTERNAL** - è più veloce e gratuito (External costa bandwidth)

3. **Vai al servizio backend:**
   - Dashboard → Services → `pratico-backend`

4. **Click "Environment" nel menu a sinistra**

5. **Cerca la variabile `DATABASE_URL`:**

   - **Se esiste già:** Click "Edit" e sostituisci con l'URL copiato
   - **Se NON esiste:** Click "Add Environment Variable"
     - **Key:** `DATABASE_URL`
     - **Value:** (incolla l'URL PostgreSQL)

6. **Click "Save Changes"**

7. **Render farà AUTO-REDEPLOY** (aspetta 2-3 minuti)

---

### **STEP 3: Verifica che Funzioni**

1. **Apri i logs del backend:**
   ```
   Dashboard → pratico-backend → Logs
   ```

2. **Cerca questa riga nei logs:**
   ```
   Database type: PostgreSQL
   ```

   ✅ Se vedi "PostgreSQL" → Funziona!
   ❌ Se vedi "SQLite" → DATABASE_URL non è configurata correttamente

3. **Test finale - crea un locale:**
   - Vai sulla dashboard frontend
   - Click "Aggiungi Locale"
   - Compila e salva

4. **Triggera un redeploy manuale:**
   - Dashboard → pratico-backend → Manual Deploy → Deploy latest commit

5. **Verifica che il locale esista ancora:**
   - Apri frontend
   - Il locale dovrebbe essere ancora lì! ✅

---

## 🔄 Migrazione Dati Esistenti (Opzionale)

Se hai già dati nel database SQLite locale e vuoi copiarli su PostgreSQL:

### **Metodo 1: Copia Manuale via Dashboard**

1. **Esporta da SQLite:**
   ```bash
   sqlite3 data/locali.db
   SELECT * FROM locali;
   # Copia i dati
   ```

2. **Ricrea i locali manualmente** tramite frontend

### **Metodo 2: Script Python (Automatico)**

```python
# migrate_sqlite_to_postgres.py
import sqlite3
import psycopg2
import os

# Connetti a SQLite
sqlite_conn = sqlite3.connect('data/locali.db')
sqlite_cur = sqlite_conn.cursor()

# Connetti a PostgreSQL (usa DATABASE_URL di Render)
postgres_url = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')
postgres_conn = psycopg2.connect(postgres_url)
postgres_cur = postgres_conn.cursor()

# Leggi da SQLite
sqlite_cur.execute("SELECT * FROM locali")
locali = sqlite_cur.fetchall()

# Scrivi su PostgreSQL
for locale in locali:
    postgres_cur.execute("""
        INSERT INTO locali (id, nome, username, ...)
        VALUES (%s, %s, %s, ...)
    """, locale)

postgres_conn.commit()
print(f"✅ Migrati {len(locali)} locali")
```

**Esegui:**
```bash
export DATABASE_URL="postgres://..."
python migrate_sqlite_to_postgres.py
```

---

## 🎯 Vantaggi PostgreSQL

| Caratteristica | SQLite (Prima) | PostgreSQL (Ora) |
|---------------|----------------|------------------|
| **Persistenza** | ❌ Cancellato ad ogni deploy | ✅ Sempre disponibile |
| **Costo** | Gratis | Gratis (free tier Render) |
| **Performance** | OK per sviluppo | ✅ Migliore per produzione |
| **Concorrenza** | Single-writer | ✅ Multi-writer |
| **Backup** | ❌ Manuale | ✅ Automatico (Render) |
| **Scalabilità** | Limitata | ✅ Alta |

---

## 🔍 Troubleshooting

### ❌ "Database type: SQLite" nei logs

**Problema:** DATABASE_URL non configurata o errata

**Soluzione:**
1. Verifica che DATABASE_URL esista in Environment variables
2. Verifica che inizi con `postgres://` (Render lo genera così)
3. Prova a riavviare: Manual Deploy → Deploy latest commit

### ❌ "could not connect to server"

**Problema:** URL database errato o database non disponibile

**Soluzione:**
1. Vai alla dashboard del database PostgreSQL
2. Verifica che sia "Available" (non "Creating" o "Suspended")
3. Copia di nuovo l'Internal Database URL
4. Aggiorna DATABASE_URL nel backend

### ❌ "relation does not exist"

**Problema:** Tabelle non create nel database PostgreSQL

**Soluzione:**
```python
# Il backend crea automaticamente le tabelle con db.create_all()
# Se non funziona, forza ricreazione:

from backend.app import app, db
with app.app_context():
    db.drop_all()  # ATTENZIONE: cancella tutti i dati!
    db.create_all()
```

Oppure triggera un redeploy - `db.create_all()` viene chiamato all'avvio.

### ❌ "password authentication failed"

**Problema:** Password PostgreSQL errata

**Soluzione:**
1. Vai alla dashboard del database
2. Click su "Connections" → "Reset password"
3. Copia nuovo URL con nuova password
4. Aggiorna DATABASE_URL nel backend

---

## 📊 Verifica Configurazione

**Check completo prima del deploy:**

```bash
# 1. Verifica requirements.txt
grep psycopg2-binary backend/requirements.txt
# Output atteso: psycopg2-binary==2.9.9

# 2. Verifica backend/app.py
grep "postgresql://" backend/app.py
# Output atteso: codice che gestisce il fix postgres→postgresql

# 3. Verifica Environment variables su Render
# Render Dashboard → pratico-backend → Environment
# Deve esserci: DATABASE_URL = postgres://...
```

---

## 🎉 Completamento

Dopo aver completato tutti gli step:

✅ Database PostgreSQL creato su Render
✅ DATABASE_URL configurata nel backend
✅ Backend deployato e usa PostgreSQL
✅ Locali persistono anche dopo redeploy
✅ Sistema production-ready!

---

## 📝 Note Importanti

1. **Free Tier Limits di PostgreSQL su Render:**
   - Storage: 1 GB
   - Connessioni: 97 simultaneous
   - Bandwidth: Unlimited (internal)
   - Durata: 90 giorni poi viene sospeso (devi riattivarlo)

2. **Riattivazione database sospeso:**
   - Dashboard → Database → Resume
   - Dati NON vengono persi

3. **Backup automatici:**
   - Render fa snapshot giornalieri (ultimi 7 giorni)
   - Dashboard → Database → Backups

4. **Monitoring:**
   - Dashboard → Database → Metrics
   - Vedi connessioni, storage, CPU

---

## 🚀 Prossimi Passi

Dopo la migrazione, considera:

1. **Backup periodico su cloud storage** (opzionale)
2. **Monitoring avanzato** con Datadog o similari
3. **Upgrade a paid tier** se superi 1GB storage

---

**Guida creata il:** 30 Ottobre 2025
**Per progetto:** Pratico Dashboard
**Database:** PostgreSQL 16 su Render Free Tier

---

🎊 **Fine della guida!** Ora il tuo database è persistente e production-ready!
