# app/main/__init__.py

from flask import Blueprint

# Criamos o Blueprint chamado 'main'
main = Blueprint('main', __name__)

# Importamos as views e errors DEPOIS de criar o objeto 'main'
# (Isso evita erro de importação circular)
from . import views, errors, forms