from flask import render_template, request
from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response

def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']

@bp.app_errorhandler(403)
def forbidden(error):
    if wants_json_response():
        return api_error_response(403)
    return render_template('error/403.html'), 403

@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template('error/404.html'), 404

@bp.app_errorhandler(400)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(400)
    return render_template('error/400.html'), 400

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template('error/500.html'), 500

@bp.app_errorhandler(413)
def internal_error(error):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(413)
    return render_template('error/413.html'), 413
