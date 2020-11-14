from flask import jsonify, abort, Response, request, render_template
from flask_login import current_user, login_required
from app import app, db
from app.utils import right_required, format_curr
from app.models import Product, Consumption, Invoice, User, Offer,  UserRoles, Role
import datetime
from sqlalchemy import or_, and_, func
from app.billing import run_billing
from app.ajax import bp
from app.schema import BookRequestSchema, offer_schema, supplier_schema
from app.email import send_invoice_reminder
from app.service.productservice import get_offer_by_id, get_offer_by_product, get_all_offers_by_product
from marshmallow import ValidationError
from flask_babel import _
import os
import json
from collections import defaultdict

@bp.route('/token', methods=['GET'])
@login_required
def issue_token():
    token = current_user.get_api_token()
    return jsonify({'token': token})

@bp.route('/offer/<int:id>', methods=['DELETE'])
@right_required(role='supplier')
def delete_offer(id):
    o = Offer.query.get(id)
    if not o:
        abort(Response(jsonify({'success': True, 'message': _('Angebot nicht gefunden')}), 404))
    if not current_user.has_role('admin') and o.user.id != current_user.id:
        abort(Response(jsonify({'success': False, 'message': _('Zugriff verweigert')}), 403))
    db.session.delete(o)
    db.session.commit()
    return jsonify({'success': True, 'message': _('Angebot gelöscht')})

@bp.route('/invoice/<int:id>/paid')
@right_required(role='supplier')
def mark_invoice_paid(id):
    invoice = Invoice.query.filter_by(id=id).first()
    if not invoice:
        abort(Response(jsonify({'success': False, 'message': _('Rechnung nicht gefunden')}), 404))
    if not current_user.has_role('admin') and invoice.supplier.id != current_user.id:
        abort(Response(jsonify({'success': False, 'message': _('Zugriff verweigert')}), 403))
    invoice.paid = True
    db.session.commit()
    return jsonify({'success': True, 'message': _('Rechnung bezahlt')})

@bp.route('/invoice/<int:id>/remind', methods=['POST'])
@right_required(role='admin')
def send_inv_reminder(id):
    inv = Invoice.query.get(id)
    if inv:
        send_invoice_reminder(inv)
    return jsonify({'success': True, 'message': _('Zahlungserinnerung gesendet')})

@bp.route('/offer/<int:offerid>/consume', methods=['POST'])
@login_required
def consume_offer(offerid):
    amount = request.json.get('amount')
    offer = Offer.query.with_for_update().get(offerid)
    if not offer or not offer.active or offer.stock < amount:
        return jsonify({'success': False, 'title': 'Ungültiges Angebot', 'text': 'Dieses Angebot ist nicht mehr gültig bitte versuche es noch einmal.'})

    offer.stock -= amount
    c = Consumption(amount=amount, user_id=current_user.id, price=offer.price, product_id=offer.product.id, billed=False, invoice_id=None, supplier_id=offer.user.id, time=datetime.datetime.utcnow())
    if offer.stock < 1:
        db.session.delete(offer)
    db.session.add(c)
    db.session.commit()

    return jsonify({'success': True, 'title': '🍻🎉', 'text': _('Viel spaß mit deinem Produkt!')})

@bp.route('/product/<int:id>/offer/popover')
@login_required
def offers_popover(id):
    offers = get_all_offers_by_product(id)
    return render_template('offers_popover.html', offers=offers)

@bp.route('/product/<int:productid>/offer')
@login_required
def get_offer_for_product(productid):
    response = {'found': False, 'text': "", 'offer': None}

    offer = get_offer_by_product(productid)
    text = None
    if offer == None:
        response['text'] = _('Ausverkauft')
    else:
        response['offer'] = offer.serialize()
        response['found'] = True
        response['text'] = _('Jetzt probieren') if offer.product.highlight else ""
    return jsonify(response)

@bp.route('/product/<int:productid>/offer/all')
@login_required
def get_all_offers_for_product(productid):
    offers = Offer.query.filter(and_(Offer.product_id==productid, Offer.active==True)).all()
    response = {'count': len(offers), 'offers': [o.serialize() for o in  offers]}
    return jsonify(response)

@bp.route('/product/<int:id>/image', methods=['DELETE'])
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

@bp.route('/product')
@right_required(role='admin')
def products():
    products = Product.query.all()
    return json.dumps([x.serialize() for x in products], ensure_ascii=False)

@bp.route('/ajax/supplier')
@right_required(role='admin')
def supplier():
    u = User.query.join(UserRoles).join(Role).filter(and_(or_(Role.name == 'supplier', Role.name == 'admin'), User.paypal != None)).all()
    return supplier_schema.dumps(u)

@bp.route('/product/book', methods=['POST'])
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
    c = Consumption(amount=amount, user=u, supplier=s, iniciator=current_user, price=req['price'], product_id=p.id, billed=False, invoice_id=None, time=datetime.datetime.utcnow())

    db.session.add(c)
    db.session.commit()
    return jsonify({'success': True, 'message': _('Erfolgreich gebucht')})

@bp.route('/billing/start')
@right_required(role='admin')
def billing():
    res = run_billing.delay()
    return jsonify({'id': res.id})

@bp.route('/billing/<string:id>/status')
@right_required(role='admin')
def get_task_status(id):
    task = run_billing.AsyncResult(id)
    return jsonify({'state': task.state})
