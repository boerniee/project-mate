from app import db
from app.models import Product, Offer
from app.api.schema import products_schema, product_schema, offers_schema
from app.api.auth import token_auth, api_right_required
from app.api.errors import error_response
from app.api import bp
from app.utils import get_request_bool_param
from flask import jsonify, request

@bp.route("/tellmesomething", methods=['GET'])
def something():
    s = """
    {\_/}
    (●_●)
    ( >🌮 Want a taco?
    """
    return s,418

@bp.route("/product", methods=['GET'])
@token_auth.login_required
def products():
    q = Product.query
    active = get_request_bool_param(request, 'active')
    if active != None:
        q=q.filter(Product.active==active)
    products = q.all()
    return products_schema.dump(products)

@bp.route("/product/<int:id>", methods=['GET'])
@token_auth.login_required
def product(id):
    product = Product.query.get(id)
    if not product:
        return error_response(404)
    return product_schema.dump(product)

@bp.route("/product", methods=['POST'])
@token_auth.login_required
def create_product():
    return error_response(501)

@bp.route("/product/<int:id>", methods=['PUT'])
@token_auth.login_required
def update_product(id):
    return error_response(501)

@bp.route("/product/<int:id>", methods=['DELETE'])
@token_auth.login_required
def delete_product(id):
    return error_response(501)
