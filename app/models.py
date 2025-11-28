# app/models.py

from datetime import datetime
# Importamos a instância 'db' do arquivo __init__.py que está na mesma pasta (.)
from . import db

# --- TABELA ROLE (Funções de usuário) ---
class Role(db.Model):
    # Nome da tabela no banco de dados
    __tablename__ = 'roles'
    
    # Colunas
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    
    # Relacionamento reverso: permite acessar user.role
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

# --- TABELA USER (Usuários) ---
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    
    # Chave Estrangeira ligando à tabela roles
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

# --- TABELA EMAIL (Log de envios) ---
class Email(db.Model):
    __tablename__ = 'emails'
    
    id = db.Column(db.Integer, primary_key=True)
    fromEmail = db.Column(db.String(64))
    toEmail = db.Column(db.String(64))
    subjectEmail = db.Column(db.String(128))
    textEmail = db.Column(db.Text)
    
    # default=datetime.utcnow pega a hora do servidor no momento da gravação
    timestampEmail = db.Column(db.DateTime, index=True, default=datetime.utcnow)