from app import db
from app.models import Offer
from app.api.schema import offers_schema, offer_schema
from app.api.auth import token_auth, api_right_required
from app.api.errors import error_response
from app.api import bp
from flask import jsonify, request, g

@bp.route("/offer", methods=['GET'])
@token_auth.login_required
@api_right_required('supplier')
def offers():
    q = Offer.query
    if not g.current_user.has_role('admin'):
        q = q.filter(Offer.user_id==g.current_user.id)
    if request.args.get('product'):
        q=q.filter(Offer.product_id==request.args.get('product'))
    offers = q.all()
    return offers_schema.dump(offers)

@bp.route("/offer/<int:id>", methods=['GET'])
@token_auth.login_required
@api_right_required('supplier')
def offer(id):
    offer = Offer.query.get(id)
    if not offer:
        return error_response(404)
    if offer.user_id != g.current_user.id and not g.current_user.has_role('admin'):
        return error_response(403)
    return offer_schema.dump(offer)

@bp.route("/offer", methods=['POST'])
@token_auth.login_required
@api_right_required('supplier')
def create_offer():
    return error_response(501)

@bp.route("/offer/<int:id>", methods=['PUT'])
@token_auth.login_required
@api_right_required('supplier')
def update_offer(id):
    return error_response(501)

@bp.route("/offer/<int:id>", methods=['DELETE'])
@token_auth.login_required
@api_right_required('supplier')
def delete_offer(id):
    return error_response(501)
