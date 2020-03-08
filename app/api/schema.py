from app import ma
from marshmallow import fields, post_dump

class WrappedModelSchema(ma.ModelSchema):
    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        if many and hasattr(self, 'many_name'):
            return {self.many_name: data}
        else:
            return data

class ProductSchema(WrappedModelSchema):
    many_name = "products"
    class Meta:
        fields = ("id", "description", "active", "_links")

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.product', id='<id>'),
        'collection': ma.URLFor('api.products'),
        'offers': ma.URLFor('api.offers', product='<id>')
    })

class OfferSchema(WrappedModelSchema):
    many_name = "offers"
    class Meta:
        fields = ("id", "stock", "created", "price", "_links")

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.offer', id='<id>'),
        'collection': ma.URLFor('api.offers')
    })

class UserSchema(WrappedModelSchema):
    class Meta:
        fields = ("id","username")

class ConsumptionSchema(WrappedModelSchema):
    many_name = "consumptions"
    supplier = fields.Nested(UserSchema(only=("id", "username")))
    product = fields.Nested(ProductSchema(only=("id", "description")))
    class Meta:
        fields = ("id","amount", "price", "time", "supplier", "product", "_links")

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.consumption', id='<id>'),
        'collection': ma.URLFor('api.consumptions')
    })

products_schema = ProductSchema(many=True)
product_schema = ProductSchema()
offers_schema = OfferSchema(many=True)
offer_schema = OfferSchema()
consumptions_schema = ConsumptionSchema(many=True)
consumption_schema = ConsumptionSchema()
