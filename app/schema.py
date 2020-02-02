from app import ma
from app.models import Product
from marshmallow import fields

class BookRequestSchema(ma.Schema):
    product = fields.Integer()
    user = fields.Integer()
    amount = fields.Integer()
    stock = fields.Boolean()
    credit = fields.Boolean()

class ProductSchema(ma.ModelSchema):
    class Meta:
        fields = ("id", "description", "price", "stock")

products_schema = ProductSchema(many=True)
product_schema = ProductSchema()
