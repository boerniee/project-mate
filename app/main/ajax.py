from flask import jsonify, abort, Response, request
from flask_login import current_user, login_required
from app import app, db
from app.utils import right_required
from app.models import Drink, Consumption, Invoice
import datetime
from app.billing import run_billing
from app.main import bp

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
    print(request.data)
    request.json
    id = request.json['drink_id']
    drink = Drink.query.with_for_update().get(id)

    if not drink:
        abort(Response("Not a valid drinkid", 400))
    try:
        amount = int(request.json['stock'])
    except Exception:
        abort(Response('Invalid stock value', 400))
    drink.stock += amount
    db.session.commit()
    return jsonify({'success': True, 'id': drink.id,  'stock': drink.stock if drink.stock_active else '-'})

@bp.route('/api/consume/<id>', methods=['POST'])
@login_required
def consume(id):
    drink = Drink.query.with_for_update().get(id)
    if not drink:
        abort(Response("Not a valid drinkid", 400))

    if drink.stock_active and drink.stock <= 0:
        abort("Out of stock", 400)
    elif drink.stock_active and drink.stock > 0:
        drink.stock -= 1

    c = Consumption(amount=1, user_id=current_user.id, price=drink.price, drink_id=drink.id, billed=False, time=datetime.datetime.utcnow())

    db.session.add(c)
    db.session.commit()

    return jsonify({'success': True, 'stock': drink.stock})

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
