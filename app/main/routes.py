from flask import render_template, jsonify, request, abort, Response, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Drink, Consumption, Invoice, User
import datetime
from babel.numbers import format_currency
from sqlalchemy import and_, desc
from sqlalchemy.sql import text
from app.utils import getIntQueryParam, getCookieValue
from app.email import send_email
from app.utils import format_curr
from app.main import bp

@bp.route('/version')
@login_required
def get_version():
    return render_template('version.html')

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    drinks = Drink.query.filter_by(active=True).order_by(desc(Drink.highlight)).all()
    return render_template('index.html', title='Start', drinks=drinks)

@bp.route('/overview',methods=['GET'])
@login_required
def overview():
    page = getIntQueryParam(request, 1)
    per_page = 10
    cons = Consumption.query.filter(and_(Consumption.user_id == current_user.id, Consumption.billed == False)).order_by(desc(Consumption.time)).paginate(page,per_page,error_out=False)

    sum = db.engine.execute(text('select sum(amount * price) from consumption where user_id = :uid and billed = 0'), uid=current_user.id).fetchone()
    return render_template('overview.html', title='Übersicht', summed=format_curr(sum[0] or 0), consumptions=cons)

@bp.route('/invoice')
@login_required
def invoice():
    page = getIntQueryParam(request, 1)
    per_page = 10
    invoices = db.session.query(Invoice).join(User).filter(User.id==current_user.id).order_by(Invoice.paid).paginate(page,per_page,error_out=False)
    return render_template('invoices.html', title='Rechnungen', invoices=invoices)

@bp.route('/invoice/<id>', methods=['GET'])
@login_required
def show_invoice(id):
    invoice = Invoice.query.get(id)
    return render_template('invoice.html', title='# '+str(id), invoice=invoice)
