from app import app, db
from app.main import bp
from app.utils import right_required, getIntQueryParam, format_curr
from flask_login import current_user
from flask import render_template, request
from app.models import Invoice, Role, Consumption
from sqlalchemy import and_
from flask_babel import _

@bp.route('/manage/invoice')
@right_required(role='supplier')
def manageinvoices():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    q = Invoice.query
    if current_user.has_role('admin'):
        q = q.filter(Invoice.paid==False)
    else:
        q = q.filter(and_(Invoice.supplier_id==current_user.id, Invoice.paid==False))
    invoices = q.paginate(page,per_page,error_out=False)
    return render_template('supplier/manage_invoices.html', invoices=invoices)

@bp.route('/manage/dashboard')
@right_required(role='supplier')
def admindashboard():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']

    q = Consumption.query
    if request.args.get('all') and current_user.has_role('admin'):
        q = q.filter(Consumption.billed == False)
        open = db.engine.execute('select sum(amount * price) from consumption where billed = 0').first()[0]
    else:
        q = q.filter(and_(Consumption.billed == False, Consumption.supplier_id == current_user.id))
        open = db.engine.execute('select sum(amount * price) from consumption where billed = 0 and supplier_id = ' + str(current_user.id)).first()[0]
    cons = q.order_by(Consumption.time.desc()).paginate(page,per_page,error_out=False)
    return render_template('supplier/dashboard.html', consumptions=cons, open=format_curr(open))
