from flask import render_template
from app import db
from app.errors import bp

@bp.app_errorhandler(403)
def forbidden(error):
    return render_template('error/403.html'), 403

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('error/404.html'), 404

@bp.app_errorhandler(400)
def not_found_error(error):
    return render_template('error/400.html'), 400

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error/500.html'), 500

@bp.app_errorhandler(413)
def internal_error(error):
    db.session.rollback()
    return render_template('error/413.html'), 413
