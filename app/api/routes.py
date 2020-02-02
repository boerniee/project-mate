from app import db
from app.models import Product
from app.schema import products_schema, product_schema
from app.api import bp
from flask import jsonify

@bp.route("/product")
def products():
    products = Product.query.all()
    print(products_schema.dump(products))
    return jsonify(products=products_schema.dump(products))

@bp.route("/product/<int:id>")
def product(id):
    products = Product.query.get(id)
    return product_schema.dump(products)
