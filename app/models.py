from app import db, login, app
from time import time
import jwt
import pyotp
from hashlib import md5
from app.utils import format_curr
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal, ROUND_HALF_UP

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    active = db.Column(db.Boolean)
    paypal = db.Column(db.String(50))
    lang = db.Column(db.String(3))
    otp_secret = db.Column(db.String(16))
    otp_count = db.Column(db.Integer)
    roles = db.relationship('Role', secondary='user_roles')
    consumptions = db.relationship("Consumption", foreign_keys="Consumption.user_id", back_populates="user")
    invoices = db.relationship("Invoice", lazy="dynamic", foreign_keys="Invoice.user_id")

    @property
    def is_active(self):
        return self.active

    @property
    def unpaid_bills(self):
        unpaidBills = self.invoices.filter(Invoice.paid==False).count()
        return unpaidBills if unpaidBills > 0 else ""

    def __eq__(self, other):
        return self.id == other.id

    def has_role(self, role):
        return role in [r.name for r in self.roles]

    def remove_role(self, role):
        if self.has_role(role):
            r = Role.query.filter_by(name=role).first()
            self.roles.remove(r)

    def add_role(self, role):
        if not self.has_role(role):
            r = Role.query.filter_by(name=role).first()
            self.roles.append(r)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_new_email_token(self, email, expires_in=86400):
        return jwt.encode(
            {'change_email': self.id, 'email': email, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def get_api_token(self, expires_in=86400):
        return jwt.encode(
            {'user': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def activate_otp(self, hotp=False):
        self.otp_secret = pyotp.random_base32()
        if hotp:
            self.otp_count = 0

    def deactivate_otp(self):
        self.otp_secret = None
        self.otp_count = None

    def otp_type(self):
        if self.otp_secret is not None and self.otp_count is None:
            return 'totp'
        elif self.otp_secret is not None and self.otp_count is not None:
            return 'hotp'
        return None

    def get_hotp(self):
        self.otp_count += 1
        db.session.commit()
        return pyotp.HOTP(self.otp_secret).at(self.otp_count)

    def verify_otp(self, otp):
        if self.otp_type() == 'hotp':
            return pyotp.HOTP(self.otp_secret).verify(otp, self.otp_count)
        if self.otp_type() == 'totp':
            return pyotp.TOTP(self.otp_secret).verify(otp)
        return True

    def get_totp_uri(self):
        app_name = app.config['INFORMATION']['name'].replace(" ", "%20")
        if self.otp_type() == 'hotp':
            return f'otpauth://hotp/{self.username}?secret={self.otp_secret}&issuer={app_name}'
        else:
            return f'otpauth://totp/{self.username}?secret={self.otp_secret}&issuer={app_name}&counter={self.otp_count}'

    @staticmethod
    def verify_api_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['user']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_change_email_token(token):
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])
            id = decoded_token['change_email']
            email = decoded_token['email']
        except:
            return
        u = User.query.get(id)
        if u:
            u.email = email
        return u

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

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(64), index=True, unique=True)
    imageUrl = db.Column(db.String(2048))
    active = db.Column(db.Boolean)
    highlight = db.Column(db.Boolean)
    offers = db.relationship("Offer")

    def serialize(self):
        return {
            'id': self.id,
            'description': self.description,
            'active': self.active
        }

    def __repr__(self):
        return '<Product {}>'.format(self.description)

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    price = db.Column(db.Float)
    created = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product')
    user = db.relationship("User")

    def serialize(self):
        return {
            'id': self.id,
            'price': self.getprice(),
            'stock': self.stock,
            'supplier': self.user.username
        }

    def getprice(self):
        if not self.price:
            return None
        return format_curr(self.price)

    def is_valid_offer(self, amount):
        if self.active == False:
            return False
        if not self.stock:
            return True
        if self.stock >= amount:
            return True
        return False

    def is_empty(self):
        if self.stock == None:
            return False
        if self.stock == 0:
            return True
        return False

class Consumption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    price = db.Column(db.Float)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    billed = db.Column(db.Boolean)
    supplier_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    iniciator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DateTime)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    invoice = db.relationship('Invoice')
    user = db.relationship('User', foreign_keys="Consumption.user_id")
    product = db.relationship('Product')
    supplier = db.relationship('User', foreign_keys="Consumption.supplier_id")
    iniciator = db.relationship('User', foreign_keys="Consumption.iniciator_id")

    def serialize(self):
        return {
            'amount': self.amount,
            'product': self.product.description,
            'price': self.getprice,
            'time': self.time
        }

    @property
    def getprice(self):
        return format_curr(self.price)

    @property
    def getsum(self):
        return format_curr(self.price * self.amount)

    def __repr__(self):
        return '<Consumption {}>'.format(self.id)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sum = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime)
    paid = db.Column(db.Boolean)
    sent = db.Column(db.Boolean)
    supplier_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    consumptions = db.relationship('Consumption')
    positions = db.relationship("Position")
    user = db.relationship("User", foreign_keys="Invoice.user_id")
    supplier = db.relationship("User", foreign_keys="Invoice.supplier_id")

    def get_paypal_link(self):
        if self.supplier:
            return f"https://www.paypal.me/{self.supplier.paypal}/{self.getsum()}"
        else:
            return ""

    def getsum(self):
        return Decimal(self.sum).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)

    def formatsum(self):
        return format_curr(self.getsum())

    def __repr__(self):
        return '<Invoice {}>'.format(self.id)

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    amount = db.Column(db.Integer)
    price = db.Column(db.Float)
    sum = db.Column(db.Float)
    product = db.relationship('Product')
    invoice = db.relationship('Invoice')

    def getsum(self):
        return format_curr(self.sum)

    def getprice(self):
        return format_curr(self.price)

    def __repr__(self):
        return '<Position {}>'.format(self.id)
