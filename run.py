import os
from app import create_app, db
from app.models import User, Role, Email # Vamos mover esses models jajá

# Cria a aplicação usando a fábrica
app = create_app()

# Contexto para o shell
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Email=Email)