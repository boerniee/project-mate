from app import app, db
from app.main.forms import ProductForm, UserForm
from flask import render_template, redirect, url_for, flash, jsonify, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Product, Invoice, Role, Consumption
from app.utils import right_required, getIntQueryParam, format_curr, save_image
from app.email import send_welcome_mail, send_activated_mail
from app.main import bp
from flask_babel import _
from sqlalchemy import or_
from werkzeug import secure_filename

@bp.route('/manage/dashboard')
@right_required(role='admin')
def admindashboard():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    open = db.engine.execute('select sum(amount * price) from consumption where billed = 0').first()[0]
    cons = Consumption.query.filter(Consumption.billed == False).order_by(Consumption.time.desc()).paginate(page,per_page,error_out=False)
    return render_template('admin/dashboard.html', title=_('Dashboard'), consumptions=cons, open=format_curr(open))

@bp.route('/manage/user')
@right_required(role='admin')
def manageusers():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    q = User.query.order_by(User.id.desc())
    s = request.args.get('search')
    if s:
        q = q.filter(or_(User.username.like(f'%{s}%'), User.email.like(f'%{s}%')))
    users = q.paginate(page,per_page,error_out=False)
    return render_template('admin/manageusers.html', title=_('Benutzerverwaltung'), users=users, searchterm=s)

@bp.route('/manage/user/<int:id>', methods=['GET', 'POST'])
@right_required(role='admin')
def edituser(id):
    form = UserForm()
    if id == 0:
        user = User()
    else:
        user = User.query.get(id)
    if form.validate_on_submit():
        if not user.active and form.active.data:
            send_activated_mail(user)
        user.email = form.email.data
        user.active = form.active.data
        if form.admin.data and not user.has_role('admin'):
            role = Role.query.filter_by(name='admin').first()
            user.roles.append(role)
        elif not form.admin.data and user.has_role('admin'):
            role = Role.query.filter_by(name='admin').first()
            user.roles.remove(role)
        if id == 0:
            db.session.add(user)
        db.session.commit()
        flash(_('Gespeichert'))
        return redirect(url_for('main.manageusers'))
    form.username.data = user.username
    form.email.data = user.email
    form.active.data = user.active
    form.admin.data = user.has_role('admin')
    return render_template('admin/edituser.html', title='Barbeiten ', form=form)

@bp.route('/manage/product')
@right_required(role='admin')
def manageproducts():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    q = Product.query.order_by(Product.active.desc())
    s = request.args.get('search')
    if s:
        q = q.filter(Product.description.like(f'%{s}%'))
    products = q.paginate(page,per_page,error_out=False)
    return render_template('admin/manageproducts.html', title=_('Produktverwaltung'), products=products, searchterm=s)

@bp.route('/manage/product/<int:id>', methods=['GET', 'POST'])
@right_required(role='admin')
def editproduct(id):
    form = ProductForm()
    if id == 0:
        product = Product()
        product.stock = 0
    else:
        product = Product.query.get(id)
    if form.validate_on_submit():
        product.description = form.description.data
        product.price = form.price.data
        product.active = form.active.data
        product.stock_active = form.stock.data
        product.highlight = form.highlight.data
        if form.file.data:
            save_image(product, form.file, app)
        if id == 0:
            db.session.add(product)
        db.session.commit()
        flash(_('Gespeichert'))
        return redirect(url_for('main.manageproducts'))
    form.description.data = product.description
    form.price.data = product.price
    form.active.data = product.active
    form.stock.data = product.stock_active
    form.highlight.data = product.highlight
    return render_template('admin/editproduct.html', title=_('Barbeiten '), product=product, form=form)

@bp.route('/manage/invoice')
@right_required(role='admin')
def manageinvoices():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    invoices = Invoice.query.filter_by(paid=False).paginate(page,per_page,error_out=False)
    return render_template('admin/manageinvoices.html', title=_('Rechnungen verwalten'), invoices=invoices)

@bp.route('/manage/admin')
@right_required(role='superadmin')
def superadmin():
    return render_template('admin/superadmin.html', title=_('Superadmin'))
