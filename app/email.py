# app/email.py

import requests
from threading import Thread
# current_app é um "proxy" que aponta para a aplicação que está rodando agora
from flask import current_app

# Função assíncrona (Roda em segundo plano)
def send_async_email(app, destinatarios, subject, text_body):
    # Precisamos "entrar" no contexto do app para acessar as configs (API_KEY, etc)
    with app.app_context():
        try:
            print('--- [THREAD] Enviando e-mail... ---', flush=True)
            requests.post(
                app.config['API_URL'], 
                auth=("api", app.config['API_KEY']), 
                data={
                    "from": app.config['API_FROM'], 
                    "to": destinatarios, 
                    "subject": app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject, 
                    "text": text_body
                }
            )
        except Exception as e:
            print(f'--- [THREAD] Erro: {e} ---', flush=True)

# Função principal chamada pelas Views
def send_simple_message(destinatarios, subject, newUser):
    # MÁGICA: O current_app é só um atalho. Para passar para a Thread, 
    # precisamos pegar o objeto real por trás dele.
    app_real = current_app._get_current_object()
    
    texto_email = "Novo usuário cadastrado: " + newUser
    
    # Cria a Thread passando o app_real
    thr = Thread(target=send_async_email, args=[app_real, destinatarios, subject, texto_email])
    thr.start()
    
    return thr