from app import db, login, app
from time import time
import jwt
from hashlib import md5
from app.utils import format_curr
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    active = db.Column(db.Boolean)
    roles = db.relationship('Role', secondary='user_roles')
    consumptions = db.relationship("Consumption", back_populates="user")
    invoices = db.relationship("Invoice")

    @property
    def is_active(self):
        return self.active

    @property
    def unpaid_bills(self):
        unpaidBills = sum(i.paid == False for i in self.invoices)
        return unpaidBills if unpaidBills > 0 else ""

    def __eq__(self, other):
        return self.id == other.id

    def has_role(self, role):
        return role in [r.name for r in self.roles]

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(64), index=True, unique=True)
    price = db.Column(db.Float, index=True)
    imageUrl = db.Column(db.String(2048))
    active = db.Column(db.Boolean)
    highlight = db.Column(db.Boolean)

    def getprice(self):
        return format_curr(self.price)

    def __repr__(self):
        return '<Drink {}>'.format(self.description)

class Consumption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    price = db.Column(db.Float)
    drink_id = db.Column(db.Integer, db.ForeignKey('drink.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DateTime)
    billed = db.Column(db.Boolean)
    user = db.relationship('User', back_populates="consumptions")
    drink = db.relationship('Drink')

    def serialize(self):
        return {
            'amount': self.amount,
            'drink': self.drink.description,
            'price': self.getprice,
            'time': self.time
        }

    @property
    def getprice(self):
        return format_curr(self.drink.price * self.amount)

    def __repr__(self):
        return '<Consumption {}>'.format(self.id)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sum = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime)
    paid = db.Column(db.Boolean)
    positions = db.relationship("Position")
    user = db.relationship("User")

    def getsum(self):
        return format_curr(self.sum)

    def __repr__(self):
        return '<Invoice {}>'.format(self.id)

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('drink.id'))
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    amount = db.Column(db.Integer)
    price = db.Column(db.Float)
    sum = db.Column(db.Float)
    drink = db.relationship('Drink')
    invoice = db.relationship('Invoice')

    def getsum(self):
        return format_curr(self.sum)

    def __repr__(self):
        return '<Position {}>'.format(self.id)
