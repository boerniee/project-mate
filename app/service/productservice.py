from app.models import Product, Offer
from sqlalchemy import and_, desc

def get_product(id):
    return Product.query.get(id)

def get_all_products():
    return Products.query.all()

def get_offer_by_product(productid):
    return Offer.query.filter(and_(Offer.product_id == productid, Offer.active == True, Offer.stock > 0)).join(Offer.user, aliased=True).filter_by(active=True).order_by(Offer.price.asc(), Offer.created.asc()).first();

def get_active_products():
    return Product.query.filter(and_(Product.active==True)).order_by(desc(Product.highlight)).all()

def get_offer_by_id(id):
    return Offer.query.get(id)
