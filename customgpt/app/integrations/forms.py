from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.simple import StringField
from wtforms.validators import Regexp


class TelegramForm(FlaskForm):
    token = StringField("API токен", validators=[Regexp("^\d+:[a-zA-Z0-9_-]{35}$", message="Неверный токен")])
    submit = SubmitField("Сохранить")
