"""
Backend Flask API per la gestione dei locali
"""
import os
import sys
import subprocess
import requests
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from models import db, Locale, LocaleLog
from crypto import CryptoManager
from retry_utils import retry_request

# Carica variabili d'ambiente
load_dotenv()

# Inizializza Flask
app = Flask(__name__)
CORS(app)  # Abilita CORS per React

# Configurazione
# Costruisci il path assoluto del database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(os.path.dirname(basedir), 'data', 'locali.db')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    f'sqlite:///{db_path}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me-in-production')

# Inizializza database
db.init_app(app)

# Inizializza crypto manager
crypto = CryptoManager()

# Crea le tabelle
with app.app_context():
    db.create_all()


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/locali', methods=['GET'])
def get_locali():
    """Ottiene la lista di tutti i locali"""
    try:
        locali = Locale.query.order_by(Locale.nome).all()
        return jsonify([locale.to_dict() for locale in locali]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/locali/<int:locale_id>', methods=['GET'])
def get_locale(locale_id):
    """Ottiene un singolo locale"""
    try:
        locale = Locale.query.get_or_404(locale_id)
        return jsonify(locale.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/locali', methods=['POST'])
def create_locale():
    """Crea un nuovo locale"""
    try:
        data = request.get_json()

        # Validazione
        required_fields = ['nome', 'username', 'password', 'orario_esecuzione', 'google_sheet_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} obbligatorio'}), 400

        # Verifica nome univoco
        if Locale.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Esiste già un locale con questo nome'}), 400

        # Cifra la password
        password_encrypted = crypto.encrypt(data['password'])

        # Cifra il PIN se presente
        pin_encrypted = None
        if data.get('pin'):
            pin_encrypted = crypto.encrypt(data['pin'])

        # Crea il locale
        locale = Locale(
            nome=data['nome'],
            username=data['username'],
            password_encrypted=password_encrypted,
            pin_encrypted=pin_encrypted,
            orario_esecuzione=data['orario_esecuzione'],
            google_sheet_id=data['google_sheet_id'],
            locale_selector=data.get('locale_selector'),
            attivo=data.get('attivo', True)
        )

        db.session.add(locale)
        db.session.commit()

        return jsonify(locale.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/locali/<int:locale_id>', methods=['PUT'])
def update_locale(locale_id):
    """Aggiorna un locale esistente"""
    try:
        locale = Locale.query.get_or_404(locale_id)
        data = request.get_json()

        # Aggiorna i campi
        if 'nome' in data:
            # Verifica nome univoco
            existing = Locale.query.filter_by(nome=data['nome']).first()
            if existing and existing.id != locale_id:
                return jsonify({'error': 'Esiste già un locale con questo nome'}), 400
            locale.nome = data['nome']

        if 'username' in data:
            locale.username = data['username']

        if 'password' in data:
            locale.password_encrypted = crypto.encrypt(data['password'])

        if 'pin' in data:
            if data['pin']:  # Se il PIN è presente, cifralo
                locale.pin_encrypted = crypto.encrypt(data['pin'])
            else:  # Se il PIN è vuoto, rimuovilo
                locale.pin_encrypted = None

        if 'orario_esecuzione' in data:
            locale.orario_esecuzione = data['orario_esecuzione']

        if 'google_sheet_id' in data:
            locale.google_sheet_id = data['google_sheet_id']

        if 'locale_selector' in data:
            locale.locale_selector = data['locale_selector']

        if 'attivo' in data:
            locale.attivo = data['attivo']

        db.session.commit()

        return jsonify(locale.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/locali/<int:locale_id>', methods=['DELETE'])
def delete_locale(locale_id):
    """Elimina un locale"""
    try:
        locale = Locale.query.get_or_404(locale_id)
        db.session.delete(locale)
        db.session.commit()

        return jsonify({'message': 'Locale eliminato con successo'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/locali/<int:locale_id>/credentials', methods=['GET'])
def get_locale_credentials(locale_id):
    """Ottiene le credenziali decifrate di un locale (per il bot)"""
    try:
        locale = Locale.query.get_or_404(locale_id)

        # Decifra la password
        password = crypto.decrypt(locale.password_encrypted)

        # Decifra il PIN se presente
        pin = None
        if locale.pin_encrypted:
            pin = crypto.decrypt(locale.pin_encrypted)

        return jsonify({
            'username': locale.username,
            'password': password,
            'pin': pin,
            'locale_selector': locale.locale_selector
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/locali/<int:locale_id>/logs', methods=['GET'])
def get_locale_logs(locale_id):
    """Ottiene i log di esecuzione di un locale"""
    try:
        locale = Locale.query.get_or_404(locale_id)
        logs = LocaleLog.query.filter_by(locale_id=locale_id).order_by(
            LocaleLog.eseguito_at.desc()
        ).limit(50).all()

        return jsonify([log.to_dict() for log in logs]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _trigger_github_workflow(api_url: str, payload: dict, headers: dict):
    """
    Helper function per chiamare GitHub Actions API con retry automatico

    Args:
        api_url: URL dell'API GitHub
        payload: Payload JSON da inviare
        headers: Headers HTTP

    Returns:
        Response object di requests
    """
    @retry_request(max_retries=3, initial_delay=2.0)
    def _make_request():
        return requests.post(api_url, json=payload, headers=headers, timeout=15)

    return _make_request()


@app.route('/api/locali/<int:locale_id>/esegui-ora', methods=['POST'])
def esegui_locale_ora(locale_id):
    """Esegue immediatamente il bot per un locale specifico"""
    try:
        locale = Locale.query.get_or_404(locale_id)

        if not locale.attivo:
            return jsonify({
                'error': f'Il locale {locale.nome} non è attivo. Attivalo prima di eseguirlo.'
            }), 400

        # Imposta il flag esegui_ora per questo locale
        locale.esegui_ora = True
        db.session.commit()

        print(f"🚀 Esecuzione manuale richiesta per locale {locale_id} ({locale.nome})")

        # Trova il path di run_bot.py (nella root del progetto)
        backend_dir = Path(__file__).parent
        project_root = backend_dir.parent
        run_bot_path = project_root / 'run_bot.py'

        if not run_bot_path.exists():
            return jsonify({
                'error': f'Script run_bot.py non trovato in {run_bot_path}'
            }), 500

        # Prepara le variabili d'ambiente per il subprocess
        env = os.environ.copy()
        env['LOCALE_ID'] = str(locale_id)

        # Assicurati che ENCRYPTION_KEY sia presente
        if 'ENCRYPTION_KEY' not in env:
            return jsonify({
                'error': 'ENCRYPTION_KEY non configurata. Configura la variabile d\'ambiente nel backend.'
            }), 500

        # Esegui il bot in background (non blocca la risposta HTTP)
        print(f"  Esecuzione comando: python {run_bot_path}")
        print(f"  Variabili d'ambiente: LOCALE_ID={locale_id}")

        process = subprocess.Popen(
            [sys.executable, str(run_bot_path)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(project_root),
            start_new_session=True  # Detach dal processo parent
        )

        print(f"  ✓ Processo avviato con PID: {process.pid}")

        # Ritorna immediatamente la risposta all'utente
        return jsonify({
            'success': True,
            'message': f'🚀 Bot avviato per {locale.nome}!\n\nIl processo è partito in background. Controlla i log per seguire l\'avanzamento.',
            'process_id': process.pid
        }), 200

    except Exception as e:
        # Resetta il flag in caso di errore
        try:
            locale.esegui_ora = False
            db.session.commit()
        except:
            pass

        print(f"❌ Errore durante l'avvio del bot: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({'error': f'Errore nell\'avvio del bot: {str(e)}'}), 500


@app.route('/api/locali/<int:locale_id>/log', methods=['POST'])
def create_locale_log(locale_id):
    """Crea un nuovo log per un locale (usato dal bot)"""
    try:
        locale = Locale.query.get_or_404(locale_id)
        data = request.get_json()

        log = LocaleLog(
            locale_id=locale_id,
            successo=data.get('successo', False),
            messaggio=data.get('messaggio'),
            file_scaricato=data.get('file_scaricato'),
            sheet_aggiornato=data.get('sheet_aggiornato', False)
        )

        db.session.add(log)
        db.session.commit()

        return jsonify(log.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Ottiene statistiche generali"""
    try:
        totale_locali = Locale.query.count()
        locali_attivi = Locale.query.filter_by(attivo=True).count()

        # Ultimi log
        ultimi_logs = LocaleLog.query.order_by(
            LocaleLog.eseguito_at.desc()
        ).limit(10).all()

        return jsonify({
            'totale_locali': totale_locali,
            'locali_attivi': locali_attivi,
            'ultimi_logs': [log.to_dict() for log in ultimi_logs]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/locali/<int:locale_id>/test', methods=['POST'])
def test_locale(locale_id):
    """
    Esegue un test manuale del download per un locale
    (Avvia il bot in background)
    """
    try:
        locale = Locale.query.get_or_404(locale_id)

        # Ritorna subito una risposta che il processo è stato avviato
        # In una implementazione reale, questo dovrebbe essere eseguito in background
        # con Celery, RQ o un thread separato

        return jsonify({
            'message': f'Test avviato per locale {locale.nome}',
            'locale_id': locale_id,
            'status': 'started'
        }), 202  # 202 Accepted - processo avviato

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
