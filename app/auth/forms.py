from flask_wtf import FlaskForm
from app.models import User
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_babel import lazy_gettext as _l

class EditProfile(FlaskForm):
    username = StringField(_l('Benutzername'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])

class LoginForm(FlaskForm):
    username = StringField(_l('Benutzername'), validators=[DataRequired()])
    password = PasswordField(_l('Passwort'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Angemeldet bleiben'))
    submit = SubmitField(_l('Anmelden'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Email senden'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Passwort'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Passwort wiederholen'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Passwort zurücksetzen'))

class RegistrationForm(FlaskForm):
    username = StringField(_l('Benutzername'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Passwort'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Passwort Wiederholen'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Registrieren'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Bitte nutze einen anderen Benutzernamen.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Bitte nutze eine andere Email Adresse.'))
