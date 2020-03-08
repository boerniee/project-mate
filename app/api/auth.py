from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.api.errors import error_response
from app.models import User
from app.api import bp
from flask import g, jsonify
from functools import wraps

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)

@token_auth.verify_token
def verify_token(token):
    g.current_user = User.verify_api_token(token) if token else None
    return g.current_user is not None

@token_auth.error_handler
@basic_auth.error_handler
def basic_auth_error():
    return error_response(401)

@bp.route('/auth/token', methods=['GET'])
@basic_auth.login_required
def issue_token():
    token = g.current_user.get_api_token()
    print("Token: " + token)
    return jsonify({'access_token': token})

def api_right_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if ( (not g.current_user.has_role(role)) and (role != "ANY")) and not g.current_user.has_role('admin'):
                return error_response(403)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
