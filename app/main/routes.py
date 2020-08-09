from flask import render_template, jsonify, request, abort, Response, url_for, flash, redirect
from flask_login import current_user, login_required
from app import db, app
from app.models import Product, Consumption, Invoice, User, Offer
from datetime import datetime
from babel.numbers import format_currency
from sqlalchemy import and_, desc, or_
from sqlalchemy.sql import text
from app.utils import getIntQueryParam
from app.email import send_email
from app.utils import format_curr, right_required
from app.service.productservice import get_active_products
from app.main.forms import OfferForm
from app.main import bp
from flask_babel import _

@bp.route('/about')
@login_required
def about():
    return render_template('about.html', now=datetime.utcnow())

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    products = get_active_products()
    return render_template('index.html', products=products)

@bp.route('/overview',methods=['GET'])
@login_required
def overview():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    cons = Consumption.query.filter(and_(Consumption.user_id == current_user.id, Consumption.billed == False)).order_by(desc(Consumption.time)).paginate(page,per_page,error_out=False)

    sum = db.engine.execute(text('select sum(amount * price) from consumption where user_id = :uid and billed = 0'), uid=current_user.id).fetchone()
    return render_template('overview.html', summed=format_curr(sum[0] or 0), consumptions=cons)

@bp.route('/invoice')
@login_required
def invoice():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    invoices = db.session.query(Invoice).join(User, User.id == Invoice.user_id).filter(User.id==current_user.id).order_by(Invoice.paid, Invoice.date.desc()).paginate(page,per_page,error_out=False)
    return render_template('invoices.html', invoices=invoices)

@bp.route('/invoice/<id>', methods=['GET'])
@login_required
def show_invoice(id):
    invoice = Invoice.query.get(id)
    if not invoice:
        abort(404, _('Rechnung nicht gefunden'))
    if invoice.user_id != current_user.id and invoice.supplier_id != current_user.id and not current_user.has_role('admin'):
        abort(403, _('Das darfst du leider nicht'))
    return render_template('invoice.html', invoice=invoice)

@bp.route('/invoice/<id>/detail')
@login_required
def invoice_detail(id):
    invoice = Invoice.query.get(id)
    if not invoice:
        abort(404, _('Rechnung nicht gefunden'))
    if invoice.user_id != current_user.id and invoice.supplier_id != current_user.id and not current_user.has_role('admin'):
        abort(403, _('Das darfst du leider nicht'))
    return render_template('invoice_detail.html', invoice=invoice)

@bp.route('/offer/<int:id>', methods=['GET', 'POST'])
@right_required(role='supplier')
def offer(id):
    form = OfferForm()
    if id == 0:
        offer = Offer()
        offer.user = current_user
        offer.product_id = 1
        offer.created = datetime.utcnow()
    else:
        offer = Offer.query.get(id)
        if not offer:
            abort(404, _('Angebot nicht gefunden'))
        if offer.user.id != current_user.id and not current_user.has_role('admin'):
            abort(403, _('Das darfst du leider nicht'))

    products = Product.query.filter(Product.active == True).all()
    form.product.choices = [(p.id,p.description) for p in products]
    if form.validate_on_submit():
        offer.active = form.active.data
        offer.price = form.price.data
        offer.stock = form.stock.data
        offer.product_id = form.product.data
        if not offer.id:
            db.session.add(offer)
        db.session.commit()
        flash(_('Gespeichert'))
        return redirect(url_for('main.offers'))
    if offer.product:
        form.product.data = offer.product.id
    form.active.data = offer.active
    form.price.data = offer.price
    form.stock.data = offer.stock
    form.supplier.data = offer.user.username
    return render_template('offer.html', form=form)

@bp.route('/offer')
@right_required(role='supplier')
def offers():
    if not current_user.paypal:
        flash(_('Bitte hinterlege deine PayPal.me Kennung'))
        return redirect(url_for('auth.editself'))
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    q = Offer.query
    if not current_user.has_role('admin') or not request.args.get('all'):
        q = q.filter(Offer.user == current_user)
    offers = q.order_by(Offer.created.desc()).paginate(page,per_page,error_out=False)
    return render_template('offers.html', offers=offers)
