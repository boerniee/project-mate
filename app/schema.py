from app import ma
from app.models import Product
from marshmallow import fields

class BookRequestSchema(ma.Schema):
    product = fields.Integer()
    price = fields.Float()
    user = fields.Integer()
    amount = fields.Integer()
    supplier = fields.Integer()
    credit = fields.Boolean()

class SupplierSchema(ma.ModelSchema):
    class Meta:
        fields = ("id", "username")

class ProductSchema(ma.ModelSchema):
    class Meta:
        fields = ("id", "description", "price", "stock")

class OfferSchema(ma.Schema):
    supplier = fields.String(attribute="user.username")
    product_name = fields.String(attribute="product.description")
    class Meta:
        fields = ("id", "stock", "supplier", "price", "product_name")

supplier_schema = SupplierSchema(many=True)
products_schema = ProductSchema(many=True)
product_schema = ProductSchema()
offer_schema = OfferSchema()
