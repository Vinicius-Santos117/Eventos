import os
import requests
from threading import Thread
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Configuração do diretório base
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_super_secreta_para_prova'

# --- BANCO DE DADOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- CONFIGURAÇÕES DE E-MAIL (Vindas do Sistema/WSGI) ---
# Note que não temos load_dotenv() aqui. O WSGI fará isso pra nós.
app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['API_URL'] = os.environ.get('API_URL')
app.config['API_FROM'] = os.environ.get('API_FROM')
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'

# Inicialização das Extensões
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- MODELOS (TABELAS) ---

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

# Novo Modelo: Persistência de E-mails (Igual ao do professor)
class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    fromEmail = db.Column(db.String(64))
    toEmail = db.Column(db.String(64))
    subjectEmail = db.Column(db.String(128))
    textEmail = db.Column(db.Text)
    # Pega a hora atual automaticamente
    timestampEmail = db.Column(db.DateTime, index=True, default=datetime.utcnow)

# --- LÓGICA DE ENVIO DE E-MAIL (ASSÍNCRONA) ---

# 1. Função que roda em SEGUNDO PLANO (na Thread)
def send_async_email(app, destinatarios, subject, text_body):
    # Precisamos do contexto da aplicação para acessar app.config dentro da thread
    with app.app_context():
        try:
            print('--- [THREAD] Iniciando envio para Mailgun... ---', flush=True)
            resposta = requests.post(
                app.config['API_URL'],
                auth=("api", app.config['API_KEY']),
                data={
                    "from": app.config['API_FROM'],
                    "to": destinatarios,
                    "subject": app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                    "text": text_body
                }
            )
            print(f'--- [THREAD] Resposta Mailgun: {resposta.status_code} ---', flush=True)
        except Exception as e:
            print(f'--- [THREAD] Erro: {e} ---', flush=True)

# 2. Função Gatilho (Que a rota chama)
def send_simple_message(destinatarios, subject, newUser):
    # Pega a instância real do app para passar para a thread
    app_real = app
    texto_email = "Novo usuário cadastrado: " + newUser

    # Cria a Thread apontando para a função async
    thr = Thread(target=send_async_email, args=[app_real, destinatarios, subject, texto_email])
    thr.start()

    return thr

# --- FORMULÁRIO ---
class NameForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

# --- ROTAS ---

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    # Pega todos os usuários para mostrar na lista (opcional)
    user_all = User.query.all()

    if form.validate_on_submit():
        # Lógica de Criação de Usuário e Role
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            # Verifica e cria Role se necessário
            user_role = Role.query.filter_by(name='User').first()
            if user_role is None:
                user_role = Role(name='User')
                db.session.add(user_role)

            # Cria Usuário
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            session['known'] = False

            # --- PREPARAÇÃO DO E-MAIL ---
            destinatarios = [app.config['FLASKY_ADMIN']]


            # --- SALVAR E-MAIL NO BANCO (Email Log) ---
            # Convertemos a lista de destinatários para string para salvar no banco
            str_destinatarios = str(destinatarios).replace("[", "").replace("]", "").replace("'", "")

            email_log = Email(
                fromEmail=app.config['API_FROM'],
                toEmail=str_destinatarios,
                subjectEmail=app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' Novo usuário',
                textEmail="Novo usuário cadastrado: " + form.name.data
            )
            db.session.add(email_log)

            # Grava tudo no banco (User, Role, EmailLog)
            db.session.commit()

            # --- ENVIA O E-MAIL (ASSÍNCRONO) ---
            if app.config['FLASKY_ADMIN']:
                print('Disparando Thread de E-mail...', flush=True)
                send_simple_message(destinatarios, 'Novo usuário', form.name.data)
                flash('Cadastro realizado e e-mail disparado!')

        else:
            session['known'] = True
            flash('Você já está cadastrado!')

        session['name'] = form.name.data
        return redirect(url_for('index'))

    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False), user_all=user_all)

@app.route('/emailsEnviados')
def emailsEnviados():
    # Busca e-mails ordenados por data
    emails_all = Email.query.order_by(Email.timestampEmail.desc()).all()
    # Precisamos criar esse template 'emailsEnviados.html'
    return render_template('emailsEnviados.html', emails_all=emails_all)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Email=Email)