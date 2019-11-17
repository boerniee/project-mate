from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, FloatField
from wtforms.validators import DataRequired, Email

class DrinkForm(FlaskForm):
    description = StringField('Beschreibung')
    price = FloatField('Preis')
    active = BooleanField('Aktiv')
    highlight = BooleanField('Hervorheben')
    submit = SubmitField('Speichern')

class UserForm(FlaskForm):
    username = StringField('Benutzername', render_kw={'readonly': True})
    email = StringField('Email', validators=[DataRequired(), Email()])
    active = BooleanField('Aktiv')
    admin = BooleanField('Admin')
    submit = SubmitField('Speichern')
