from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = StringField('Пароль', validators=[DataRequired()])
    agree = BooleanField('Я согласен с условиями', validators=[DataRequired()])
    submit = SubmitField('Привязать аккаунт')