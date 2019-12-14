from app import db
from app.models import Invoice
from app.api import bp
from flask import jsonify

@bp.route("/invoice")
def invoices():
    return jsonify({"text": "nothing to see here"})
