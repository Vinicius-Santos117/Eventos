# app/main/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
    # Campo de texto obrigatório
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    
    # Botão de envio
    submit = SubmitField('Cadastrar')