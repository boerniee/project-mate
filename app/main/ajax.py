from flask import jsonify, abort, Response, request
from flask_login import current_user, login_required
from app import app, db
from app.utils import right_required
from app.models import Product, Consumption, Invoice
import datetime
from app.billing import run_billing
from app.main import bp
from app.email import send_invoice_reminder
import os

@bp.route('/manage/invoice/<int:id>/paid')
@right_required(role='admin')
def markinvoiceaspaid(id):
    invoice = Invoice.query.filter_by(id=id).first()
    invoice.paid = True
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/api/stock', methods=['POST'])
@right_required(role='admin')
def add_stock():
    request.json
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

@bp.route('/api/consume/<id>', methods=['POST'])
@login_required
def consume(id):
    product = Product.query.with_for_update().get(id)
    if not product:
        abort(Response("Not a valid productid", 400))

    if not product.active:
        abort("Product inactive", 400)

    if product.stock_active and product.stock <= 0:
        abort("Out of stock", 400)
    elif product.stock_active and product.stock > 0:
        product.stock -= 1

    c = Consumption(amount=1, user_id=current_user.id, price=product.price, product_id=product.id, billed=False, time=datetime.datetime.utcnow())

    db.session.add(c)
    db.session.commit()

    return jsonify({'success': True, 'active': product.stock_active, 'stock': product.stock})

@bp.route('/invoice/<int:id>/remind', methods=['POST'])
def send_reminder(id):
    inv = Invoice.query.get(id)
    if inv:
        send_invoice_reminder(inv)
    return jsonify({'success': True})
@bp.route('/manage/product/<int:id>/image', methods=['DELETE'])
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
