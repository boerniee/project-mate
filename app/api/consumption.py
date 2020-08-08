from app.api import bp
from app.models import Consumption
from app.api.schema import consumptions_schema, consumption_schema
from app.api.auth import token_auth
from app.api.errors import error_response
from flask import g, request
from sqlalchemy import and_

@bp.route('/consumption', methods=['GET'])
@token_auth.login_required
def consumptions():
    q = Consumption.query.filter(Consumption.billed==False)
    if not g.current_user.has_role('admin'):
        q = q.filter(Consumption.user_id==g.current_user.id)
    if request.args.get('product'):
        q=q.filter(Consumption.product_id==request.args.get('product'))
    consumptions = q.all()
    return consumptions_schema.dump(consumptions)

@bp.route('/consumption/<int:id>', methods=['GET'])
@token_auth.login_required
def consumption(id):
    consumption = Consumption.query.get(id)
    if not consumption:
        return error_response(404)
    if g.current_user.id != consumption.user_id and not g.current_user.has_role('admin'):
        return error_response(403)
    return consumption_schema.dump(consumption)
