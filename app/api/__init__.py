from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import auth, errors, product, offer, consumption
