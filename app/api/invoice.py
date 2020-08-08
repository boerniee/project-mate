from app import db
from app.models import Invoice
from app.api.schema import invoice_schema, invoices_schema
from app.api.auth import token_auth, api_right_required
from app.api.errors import error_response
from app.utils import get_request_bool_param
from app.api import bp
from flask import jsonify, request, g

@bp.route("/invoice", methods=['GET'])
@token_auth.login_required
def invoices():
    q = Invoice.query
    if not g.current_user.has_role('admin'):
        q=q.filter(Invoice.user_id==g.current_user.id)
    paid = get_request_bool_param(request, 'paid')
    q = q.filter(Invoice.paid==False if paid is None else paid)
    invoices = q.all()
    return invoices_schema.dump(invoices)

@bp.route("/invoice/<int:id>", methods=['GET'])
@token_auth.login_required
def invoice(id):
    invoice = Invoice.query.get(id)
    if not invoice:
        return error_response(404)
    if invoice.user_id != g.current_user.id and not g.current_user.has_role('admin'):
        return error_response(403)
    return invoice_schema.dump(invoice)

@bp.route('/invoice/<int:id>/paid', methods=['POST'])
@token_auth.login_required
@api_right_required('supplier')
def invoice_paid(id):
    invoice = Invoice.query.get(id)
    if not invoice:
        return error_response(404)
    if invoice.supplier_id != g.current_user.id and not g.current_user.has_role('admin'):
        return error_response(403)
    if not invoice.paid:
        invoice.paid = True
        db.session.commit()
    return invoice_schema.dump(invoice)
