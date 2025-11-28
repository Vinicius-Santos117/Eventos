# app/main/views.py

from flask import render_template, session, redirect, url_for, flash, current_app
# Importamos o blueprint 'main' da pasta atual (.)
from . import main
# Importamos o formulário do arquivo forms.py na pasta atual (.)
from .forms import NameForm
# Importamos o banco de dados (db) e os modelos da pasta pai (..)
from .. import db
from ..models import User, Role, Email
# Importamos a função de envio de email da pasta pai (..)
from ..email import send_simple_message

# Rota Principal
@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    user_all = User.query.all()

    if form.validate_on_submit():
        # Busca usuário
        user = User.query.filter_by(username=form.name.data).first()

        if user is None:
            # Lógica de Role
            user_role = Role.query.filter_by(name='User').first()
            if user_role is None:
                user_role = Role(name='User')
                db.session.add(user_role)

            # Cria Usuário
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            session['known'] = False

            # Define destinatários
            # Acessamos configs via current_app.config
            destinatarios = [current_app.config['FLASKY_ADMIN']]

            # Salva Log de Email no Banco
            str_destinatarios = str(destinatarios).replace("[", "").replace("]", "").replace("'", "")
            email_log = Email(
                fromEmail=current_app.config['API_FROM'],
                toEmail=str_destinatarios,
                subjectEmail=current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' Novo usuário',
                textEmail="Novo usuário cadastrado: " + form.name.data
            )
            db.session.add(email_log)
            db.session.commit()

            # Envia E-mail (Se houver admin configurado)
            if current_app.config['FLASKY_ADMIN']:
                send_simple_message(destinatarios, 'Novo usuário', form.name.data)

        else:
            session['known'] = True

        session['name'] = form.name.data
        # ATENÇÃO: Redireciona para 'main.index' (nome do blueprint . nome da rota)
        return redirect(url_for('main.index'))

    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False), user_all=user_all)


    # Adicionamos a rota Sobre que estava faltando
@main.route('/sobre')
def sobre():
    return "<h1>Página sobre o sistema de eventos</h1>"


# Rota de E-mails Enviados
@main.route('/emailsEnviados')
def emailsEnviados():
    emails_all = Email.query.order_by(Email.timestampEmail.desc()).all()
    return render_template('emailsEnviados.html', emails_all=emails_all)