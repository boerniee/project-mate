from flask import render_template, jsonify, request, abort, Response, url_for
from flask_login import current_user, login_required
from app import db, app
from app.models import Drink, Consumption, Invoice, User
from datetime import datetime
from babel.numbers import format_currency
from sqlalchemy import and_, desc, or_
from sqlalchemy.sql import text
from app.utils import getIntQueryParam
from app.email import send_email
from app.utils import format_curr
from app.main import bp
from flask_babel import _

@bp.route('/about')
@login_required
def about():
    return render_template('about.html', title=_('Über'), now=datetime.utcnow(), information=app.config['INFORMATION'])

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    drinks = Drink.query.filter(and_(Drink.active==True)).order_by(desc(Drink.highlight)).all()
    return render_template('index.html', title=_('Start'), drinks=drinks)

@bp.route('/overview',methods=['GET'])
@login_required
def overview():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    cons = Consumption.query.filter(and_(Consumption.user_id == current_user.id, Consumption.billed == False)).order_by(desc(Consumption.time)).paginate(page,per_page,error_out=False)

    sum = db.engine.execute(text('select sum(amount * price) from consumption where user_id = :uid and billed = 0'), uid=current_user.id).fetchone()
    return render_template('overview.html', title=_('Übersicht'), summed=format_curr(sum[0] or 0), consumptions=cons)

@bp.route('/invoice')
@login_required
def invoice():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    invoices = db.session.query(Invoice).join(User).filter(User.id==current_user.id).order_by(Invoice.paid).paginate(page,per_page,error_out=False)
    return render_template('invoices.html', title=_('Rechnungen'), invoices=invoices)

@bp.route('/invoice/<id>', methods=['GET'])
@login_required
def show_invoice(id):
    invoice = Invoice.query.get(id)
    if not invoice:
        abort(404, _('Rechnung nicht gefunden'))
    if invoice.user_id != current_user.id and not current_user.has_role('admin'):
        abort(403, _('Das darfst du leider nicht'))
    return render_template('invoice.html', title='# ' + str(id), invoice=invoice)
