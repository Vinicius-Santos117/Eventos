import os

class Config:
    SECRET_KEY = 'chave_super_secreta_para_prova'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações do Mailgun (Vêm do ambiente)
    API_KEY = os.environ.get('API_KEY')
    API_URL = os.environ.get('API_URL')
    API_FROM = os.environ.get('API_FROM')
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_MAIL_SUBJECT_PREFIX = '[EventosApp]'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    # Define o banco de dados
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

# Dicionário para facilitar a escolha da config
config = {
    'default': DevelopmentConfig
}