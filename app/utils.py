from flask import abort, Response
from flask_login import current_user
from app import login
from functools import wraps
from flask_babel import format_currency
import os
import uuid

def getIntQueryParam(request, default):
    page = request.args.get('page')
    if not page:
        return default
    else:
        try:
            return int(page)
        except TypeError:
            return default

def save_image(product, file, app):
    if product.imageUrl:
        try:
            os.remove(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], product.imageUrl))
        except FileNotFoundError:
            pass
    filename = str(uuid.uuid4())
    file.data.save(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
    product.imageUrl = filename

def format_curr(amount):
    if not amount:
        amount = 0
    return format_currency(amount, 'EUR')

def right_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return login.unauthorized()
            if ( (not current_user.has_role(role)) and (role != "ANY")) and not current_user.has_role('admin'):
                return login.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
