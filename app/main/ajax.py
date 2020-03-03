from flask import jsonify, abort, Response, request
from flask_login import current_user, login_required
from app import app, db
from app.utils import right_required, format_curr
from app.models import Product, Consumption, Invoice, User, Offer,  UserRoles, Role
import datetime
from sqlalchemy import or_, and_, func
from app.billing import run_billing
from app.main import bp
from app.schema import BookRequestSchema, offer_schema, supplier_schema
from app.email import send_invoice_reminder
from app.service.productservice import get_offer_by_id, get_offer_by_product
from marshmallow import ValidationError
from flask_babel import _
import os
import json
from collections import defaultdict

@bp.route('/ajax/offer/<int:id>', methods=['DELETE'])
@login_required
def delete_offer(id):
    o = Offer.query.get(id)
    if o:
        db.session.delete(o)
        db.session.commit()
    return jsonify({'success': True})

@bp.route('/manage/invoice/<int:id>/paid')
@right_required(role='admin')
def markinvoiceaspaid(id):
    invoice = Invoice.query.filter_by(id=id).first()
    invoice.paid = True
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/ajax/invoice/<int:id>/remind', methods=['POST'])
@login_required
def send_reminder(id):
    inv = Invoice.query.get(id)
    if inv:
        send_invoice_reminder(inv)
    return jsonify({'success': True})

@bp.route('/ajax/consume/offer/<int:offerid>', methods=['POST'])
@login_required
def consume(offerid):
    offer = Offer.query.with_for_update().get(offerid)
    if not offer or not offer.active or offer.stock <= 0:
        return jsonify({'success': False, 'title': 'Ungültiges Angebot', 'text': 'Dieses Angebot ist nicht mehr gültig bitte versuche es noch einmal.'})

    offer.stock -= 1
    c = Consumption(amount=1, user_id=current_user.id, price=offer.price, product_id=offer.product.id, supplier_id=offer.user.id, billed=False, time=datetime.datetime.utcnow())
    if offer.stock < 1:
        db.session.delete(offer)
    db.session.add(c)
    db.session.commit()

    return jsonify({'success': True, 'title': '🍻🎉', 'text': _('Viel spaß mit deinem Produkt!')})

@bp.route('/ajax/product/<int:id>/offer/all')
@right_required(role='admin')
def get_all_offers_product(id):
    offers = Offer.query.filter(Offer.product_id == id).all()
    return jsonify({'offers': [o.serialize() for o in offers]})

@bp.route('/ajax/product/<int:id>/offer')
@login_required
def get_offer_for_product(id):
    response = {'found': False, 'text': "", 'offer': None}

    offer = get_offer_by_product(id)
    text = None
    if offer == None:
        response['text'] = _('Ausverkauft')
    else:
        response['offer'] = offer.serialize()
        response['found'] = True
        response['text'] = _('Jetzt probieren') if offer.product.highlight else ""
    return jsonify(response)

@bp.route('/ajax/product/<int:id>/image', methods=['DELETE'])
@right_required(role='admin')
def delete_product_image(id):
    product = Product.query.get(id)
    if not product:
        abort(Response("Not a valid productid", 400))
    filename = product.imageUrl
    try:
        os.remove(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
    except FileNotFoundError:
        pass
    product.imageUrl = None
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/ajax/products')
@right_required(role='admin')
def products():
    products = Product.query.all()
    return json.dumps([x.serialize() for x in products], ensure_ascii=False)

@bp.route('/ajax/supplier')
@right_required(role='admin')
def supplier():
    u = User.query.join(UserRoles).join(Role).filter(and_(or_(Role.name == 'supplier', Role.name == 'admin'), User.paypal != None)).all()
    return supplier_schema.dumps(u)

@bp.route('/manage/book', methods=['POST'])
@right_required(role='admin')
def book():
    schema = BookRequestSchema()
    try:
        req = schema.load(request.get_json())
    except ValidationError as err:
        return _("Fehler bei der Validierung"), 400

    p = Product.query.get(req['product'])
    if not p:
        abort(Response("Not a valid productid", 400))

    u = User.query.get(req['user'])
    if not u:
        abort(Response("Not a valid user", 400))

    s = User.query.get(req['supplier'])

    amount = -int(req['amount']) if req['credit'] else int(req['amount'])
    c = Consumption(amount=amount, user=u, supplier=s, price=req['price'], product_id=p.id, billed=False, time=datetime.datetime.utcnow())

    db.session.add(c)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/manage/billing/start')
@right_required(role='admin')
def billing():
    res = run_billing.delay()
    return jsonify({'id': res.id})

@bp.route('/manage/billing/status/<string:id>')
@right_required(role='admin')
def get_task_status(id):
    task = run_billing.AsyncResult(id)
    return jsonify({'state': task.state})
