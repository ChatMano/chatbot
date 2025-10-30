#!/usr/bin/env python3
"""
Script di migrazione database per aggiungere la colonna esegui_ora
"""
import sqlite3
import sys
from pathlib import Path

def migrate_database(db_path):
    """Aggiunge la colonna esegui_ora se non esiste"""

    print(f"Migrazione database: {db_path}")

    # Verifica che il database esista
    if not Path(db_path).exists():
        print(f"⚠️  Database non trovato in {db_path}")
        print("   Verrà creato automaticamente da Flask al primo avvio")
        return True

    try:
        # Connetti al database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verifica se la colonna esiste già
        cursor.execute("PRAGMA table_info(locali)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'esegui_ora' in columns:
            print("✓ Colonna 'esegui_ora' già presente nel database")
            conn.close()
            return True

        # Aggiungi la colonna esegui_ora
        print("⚙️  Aggiunta colonna 'esegui_ora' alla tabella 'locali'...")
        cursor.execute("""
            ALTER TABLE locali
            ADD COLUMN esegui_ora BOOLEAN DEFAULT 0 NOT NULL
        """)

        conn.commit()
        print("✅ Migrazione completata con successo!")

        # Verifica che la colonna sia stata aggiunta
        cursor.execute("PRAGMA table_info(locali)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'esegui_ora' in columns:
            print("✓ Colonna 'esegui_ora' verificata nel database")
        else:
            print("❌ ERRORE: Colonna non aggiunta correttamente")
            conn.close()
            return False

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Errore SQLite durante la migrazione: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore durante la migrazione: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Path del database
    db_path = Path(__file__).parent / 'data' / 'locali.db'

    print("\n" + "="*60)
    print("MIGRAZIONE DATABASE - Aggiunta colonna esegui_ora")
    print("="*60 + "\n")

    success = migrate_database(str(db_path))

    if success:
        print("\n✅ Migrazione completata!")
        sys.exit(0)
    else:
        print("\n❌ Migrazione fallita!")
        sys.exit(1)
