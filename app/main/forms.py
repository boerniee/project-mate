from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, FloatField
from wtforms.validators import DataRequired, Email
from flask_babel import lazy_gettext as _l

class DrinkForm(FlaskForm):
    description = StringField(_l('Beschreibung'), validators=[DataRequired()])
    price = FloatField(_l('Preis'), validators=[DataRequired()])
    active = BooleanField(_l('Aktiv'))
    highlight = BooleanField(_l('Hervorheben'))
    stock = BooleanField(_l('Bestand führen'))
    submit = SubmitField(_l('Speichern'))

class UserForm(FlaskForm):
    username = StringField(_l('Benutzername'), render_kw={'readonly': True})
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    active = BooleanField(_l('Aktiv'))
    admin = BooleanField(_l('Admin'))
    submit = SubmitField(_l('Speichern'))
