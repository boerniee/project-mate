from flask import abort, Response
from flask_login import current_user
from app import login
from functools import wraps
from babel.numbers import format_currency

def getIntQueryParam(request, default):
    page = request.args.get('page')
    if not page:
        return default
    else:
        try:
            return int(page)
        except TypeError:
            return default

def getCookieValue(request, cookie):
    value = request.cookies.get(cookie)
    if not value:
        abort(Response("please set cookie '" + cookie + "'", 400))
    return value

def format_curr(amount):
    return format_currency(amount, 'EUR')

def right_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return login.unauthorized()
            if ( (not current_user.has_role(role)) and (role != "ANY")):
                return login.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
