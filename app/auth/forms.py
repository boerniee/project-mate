from flask_wtf import FlaskForm
from app.models import User
from app import app
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_babel import lazy_gettext as _l

def validate_lang(form, field):
    if field.data not in app.config['LANGUAGES'].keys():
        raise ValidationError(_l('Sprache ist nicht unterstützt'))

def validate_username(self, username):
    if (current_user is not None and not current_user.is_anonymous) and current_user.username == username.data:
        return
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
        raise ValidationError(_l('Bitte nutze einen anderen Benutzernamen.'))

def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user is not None:
        raise ValidationError(_l('Bitte nutze eine andere Email Adresse.'))

def validate_password(self, field):
    pass

class EditProfile(FlaskForm):
    username = StringField(_l('Benutzername'), validators=[DataRequired(), validate_username])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    paypal = StringField(_l('PayPal.me'))
    lang = SelectField(_l('Sprache'), choices=[(key, val) for key,val in app.config['LANGUAGES'].items()], validators=[DataRequired(), validate_lang])
    submit = SubmitField(_l('Speichern'))

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
    username = StringField(_l('Benutzername'), validators=[DataRequired(), validate_username])
    email = StringField(_l('Email'), validators=[DataRequired(), Email(), validate_email])
    password = PasswordField(_l('Passwort'), validators=[DataRequired(), validate_password])
    password2 = PasswordField(
        _l('Passwort Wiederholen'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Registrieren'))
