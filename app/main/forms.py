from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, FloatField, IntegerField, SelectField, TextField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Email, Optional
from flask_babel import lazy_gettext as _l

class OfferForm(FlaskForm):
    product = SelectField(_l('Produkt'), coerce=int,validators=[DataRequired()])
    price = FloatField(_l('Preis'), validators=[DataRequired()])
    stock = IntegerField(_l('Bestand'), validators=[Optional()])
    active = BooleanField(_l('Aktiv'))
    supplier = TextField(_l('Lieferant'), render_kw={'readonly': True})
    submit = SubmitField(_l('Speichern'))

class ProductForm(FlaskForm):
    description = StringField(_l('Beschreibung'), validators=[DataRequired()])
    active = BooleanField(_l('Aktiv'))
    highlight = BooleanField(_l('Hervorheben'))
    submit = SubmitField(_l('Speichern'))
    file = FileField(_l('Produktbild'), validators=[
        FileAllowed(['jpg', 'png'], _l('Nur Dateiendungen jpg order png erlaubt!'))
    ])

class UserForm(FlaskForm):
    username = StringField(_l('Benutzername'), render_kw={'readonly': True})
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    active = BooleanField(_l('Aktiv'))
    supplier = BooleanField(_l('Lieferant'))
    admin = BooleanField(_l('Admin'))
    submit = SubmitField(_l('Speichern'))
