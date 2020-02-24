from flask import jsonify, abort, Response, request
from flask_login import current_user, login_required
from app import app, db
from app.utils import right_required, format_curr
from app.models import Product, Consumption, Invoice, User, Offer
import datetime
from sqlalchemy import and_
from app.billing import run_billing
from app.main import bp
from app.schema import BookRequestSchema, offer_schema
from app.email import send_invoice_reminder
from app.service.productservice import get_offer_by_id, get_offer_by_product
from marshmallow import ValidationError
from flask_babel import _
import os
import json

@bp.route('/manage/invoice/<int:id>/paid')
@right_required(role='admin')
def markinvoiceaspaid(id):
    invoice = Invoice.query.filter_by(id=id).first()
    invoice.paid = True
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/ajax/invoice/<int:id>/remind', methods=['POST'])
def send_reminder(id):
    inv = Invoice.query.get(id)
    if inv:
        send_invoice_reminder(inv)
    return jsonify({'success': True})

@bp.route('/ajax/stock', methods=['POST'])
@right_required(role='admin')
def add_stock():
    id = request.json['product_id']
    product = Product.query.with_for_update().get(id)

    if not product:
        abort(Response("Not a valid productid", 400))
    try:
        amount = int(request.json['stock'])
    except Exception:
        abort(Response('Invalid stock value', 400))
    product.stock += amount
    db.session.commit()
    return jsonify({'success': True, 'id': product.id,  'stock': product.stock if product.stock_active else '-'})

@bp.route('/ajax/consume/offer/<int:offerid>', methods=['POST'])
@login_required
def consume(offerid):
    offer = Offer.query.with_for_update().get(offerid)
    if not offer or not offer.active or offer.stock <= 0:
        return jsonify({'success': False, 'title': 'Ungültiges Angebot', 'text': 'Dieses Angebot ist nicht mehr gültig bitte versuche es noch einmal.'})

    offer.stock -= 1
    c = Consumption(amount=1, user_id=current_user.id, price=offer.price, product_id=offer.product.id, offer_id=offer.id, billed=False, time=datetime.datetime.utcnow())
    db.session.add(c)
    db.session.commit()
    print(c.getprice)

    return jsonify({'success': True, 'title': '🍻🎉', 'text': _('Viel spaß mit deinem Produkt!')})
    #if not product:
    #    abort(Response("Not a valid productid", 400))

    #if not product.active:
#        abort("Product inactive", 400)

    #if product.stock_active and product.stock <= 0:
    #    abort("Out of stock", 400)
    #elif product.stock_active and product.stock > 0:
    #    product.stock -= 1

    #c = Consumption(amount=1, user_id=current_user.id, price=product.price, product_id=product.id, billed=False, time=datetime.datetime.utcnow())

    #db.session.add(c)
    #db.session.commit()

    #return jsonify({'success': True, 'active': product.stock_active, 'stock': product.stock})

@bp.route('/ajax/product/<int:id>/offer')
def get_offer_for_product(id):
    response = {'found': False, 'text': "", 'offer': None}

    offer = get_offer_by_product(id)
    text = None
    if offer == None:
        response['text'] = _('Ausverkauft')
    else:
        response['offer'] = offer.serialize()
        response['found'] = True
    return jsonify(response)

@bp.route('/ajax/product/<int:id>/image', methods=['DELETE'])
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

@bp.route('/manage/book', methods=['POST'])
@right_required(role='admin')
def book():
    schema = BookRequestSchema()
    try:
        req = schema.load(request.get_json())
    except ValidationError as err:
        print(err)
        return _("Fehler bei der Validierung"), 400

    if req['stock']:
        p = Product.query.with_for_update().get(req['product'])
    else:
        p = Product.query.get(req['product'])
    if not p:
        abort(Response("Not a valid productid", 400))

    u = User.query.get(req['user'])
    if not u:
        abort(Response("Not a valid user", 400))

    amount = -int(req['amount']) if req['credit'] else int(req['amount'])
    c = Consumption(amount=amount, user_id=u.id, price=p.price, product_id=p.id, billed=False, time=datetime.datetime.utcnow())
    if req['stock']:
        p.stock -= amount

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
