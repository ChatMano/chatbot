"""
Modelli del database per la gestione dei locali
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Locale(db.Model):
    """Modello per un locale/punto vendita"""

    __tablename__ = 'locali'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, unique=True)
    username = db.Column(db.String(200), nullable=False)
    password_encrypted = db.Column(db.Text, nullable=False)
    pin_encrypted = db.Column(db.Text, nullable=True)  # PIN opzionale per iPratico
    orario_esecuzione = db.Column(db.String(5), nullable=False, default='03:00')  # HH:MM format
    google_sheet_id = db.Column(db.String(200), nullable=False)
    locale_selector = db.Column(db.String(500), nullable=True)  # Selettore per identificare il locale su iPratico
    attivo = db.Column(db.Boolean, default=True, nullable=False)
    esegui_ora = db.Column(db.Boolean, default=False, nullable=False)  # Flag per esecuzione manuale immediata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relazione con i log
    logs = db.relationship('LocaleLog', backref='locale', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Converte il locale in dizionario (senza password)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'username': self.username,
            'orario_esecuzione': self.orario_esecuzione,
            'google_sheet_id': self.google_sheet_id,
            'locale_selector': self.locale_selector,
            'attivo': self.attivo,
            'esegui_ora': self.esegui_ora,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'ultimo_log': self.logs[0].to_dict() if self.logs else None
        }


class LocaleLog(db.Model):
    """Log delle esecuzioni per ogni locale"""

    __tablename__ = 'locale_logs'

    id = db.Column(db.Integer, primary_key=True)
    locale_id = db.Column(db.Integer, db.ForeignKey('locali.id'), nullable=False)
    eseguito_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    successo = db.Column(db.Boolean, nullable=False)
    messaggio = db.Column(db.Text, nullable=True)
    file_scaricato = db.Column(db.String(500), nullable=True)
    sheet_aggiornato = db.Column(db.Boolean, default=False)

    def to_dict(self):
        """Converte il log in dizionario"""
        return {
            'id': self.id,
            'locale_id': self.locale_id,
            'eseguito_at': self.eseguito_at.isoformat() if self.eseguito_at else None,
            'successo': self.successo,
            'messaggio': self.messaggio,
            'file_scaricato': self.file_scaricato,
            'sheet_aggiornato': self.sheet_aggiornato
        }
