from app import ma
from app.models import Product
from marshmallow import fields, post_dump
from app.utils import format_curr

class BookRequestSchema(ma.Schema):
    product = fields.Integer()
    user = fields.Integer()
    amount = fields.Integer()
    stock = fields.Boolean()
    credit = fields.Boolean()

class ProductSchema(ma.ModelSchema):
    class Meta:
        fields = ("id", "description", "price", "stock")

class ConsumptionSchema(ma.ModelSchema):
    product = fields.Nested(ProductSchema, only=("description",))
    datetime = fields.DateTime('%d.%m.%Y %H:%M:%S', attribute="time")

    class Meta:
        fields = ("price", "amount", "product", "datetime")

    @post_dump()
    def format_currency(self, data, **kwargs):
        data['sum'] = format_curr(data['sum'])
        data['price'] = format_curr(data['price'])
        return data

    @post_dump()
    def calculate_sum(self, data, **kwargs):
        data['sum'] = data['amount'] * data['price']
        return data

products_schema = ProductSchema(many=True)
product_schema = ProductSchema()
consumptions_schema = ConsumptionSchema(many=True)
