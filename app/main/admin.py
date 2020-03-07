from app import app, db
from app.main.forms import ProductForm, UserForm
from flask import render_template, redirect, url_for, flash, jsonify, request
from flask_login import current_user, login_user, login_required
from app.models import User, Product, Invoice, Role, Consumption
from app.utils import right_required, getIntQueryParam, format_curr, save_image
from app.email import send_welcome_mail, send_activated_mail
from app.main import bp
from flask_babel import _
from sqlalchemy import or_, and_, func
from werkzeug import secure_filename

@bp.route('/manage/user')
@right_required(role='admin')
def manageusers():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    q = User.query.order_by(User.active.desc(), User.id.desc())
    s = request.args.get('search')
    if s:
        q = q.filter(or_(User.username.like(f'%{s}%'), User.email.like(f'%{s}%')))
    users = q.paginate(page,per_page,error_out=False)
    return render_template('admin/manage_users.html', users=users)

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
        if form.admin.data:
            user.add_role('admin')
        else:
            user.remove_role('admin')
        if form.supplier.data:
            user.add_role('supplier')
        else:
            user.remove_role('supplier')
        if id == 0:
            db.session.add(user)
        db.session.commit()
        flash(_('Gespeichert'))
        return redirect(url_for('main.manageusers'))
    form.username.data = user.username
    form.email.data = user.email
    form.active.data = user.active
    form.admin.data = user.has_role('admin')
    form.supplier.data = user.has_role('supplier')
    return render_template('admin/edit_user.html', form=form)

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
    return render_template('admin/manage_products.html', products=products, searchterm=s)

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
        product.active = form.active.data
        product.highlight = form.highlight.data
        if form.file.data:
            save_image(product, form.file, app)
        if id == 0:
            db.session.add(product)
        db.session.commit()
        flash(_('Gespeichert'))
        return redirect(url_for('main.manageproducts'))
    form.description.data = product.description
    form.active.data = product.active
    form.highlight.data = product.highlight
    return render_template('admin/edit_product.html', product=product, form=form)
