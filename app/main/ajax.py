from flask import jsonify, abort, Response
from flask_login import current_user, login_required
from app import app, db
from app.utils import right_required
from app.models import Drink, Consumption
import datetime
from app.billing import run_billing
from app.main import bp

@bp.route('/api/consume/<id>', methods=['POST'])
@login_required
def consume(id):
    drink = Drink.query.get(id)
    if not drink:
        abort(Response("Not a valid drinkid", 400))

    c = Consumption(amount=1, user_id=current_user.id, price=drink.price, drink_id=drink.id, billed=False, time=datetime.datetime.utcnow())
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
