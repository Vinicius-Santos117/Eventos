from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config # Importa o arquivo que acabamos de criar

# 1. Cria as extensões (mas não as liga ao app ainda)
bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    # 2. Inicializa o App
    app = Flask(__name__)

    # 3. Carrega configurações do config.py
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 4. Liga as extensões ao app criado
    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # 5. Registra o Blueprint (Vamos criar isso jajá)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app