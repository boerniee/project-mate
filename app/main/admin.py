from app import app, db
from app.main.forms import DrinkForm, UserForm
from flask import render_template, redirect, url_for, flash, jsonify, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Drink, Invoice, Role, Consumption
from app.utils import right_required, getIntQueryParam, format_curr
from app.email import send_welcome_mail, send_activated_mail
from app.main import bp
from flask_babel import _

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
    users = User.query.paginate(page,per_page,error_out=False)
    return render_template('admin/manageusers.html', title=_('Benutzerverwaltung'), users=users)

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

@bp.route('/manage/drink')
@right_required(role='admin')
def managedrinks():
    page = getIntQueryParam(request, 1)
    per_page = app.config['PER_PAGE']
    q = Drink.query.order_by(Drink.active.desc())
    s = request.args.get('search')
    if s:
        q = q.filter(Drink.description.like(f'%{s}%'))
    print(type(q))
    drinks = q.paginate(page,per_page,error_out=False)
    return render_template('admin/managedrinks.html', title=_('Getränkeverwaltung'), drinks=drinks, searchterm=s)

@bp.route('/manage/drink/<int:id>', methods=['GET', 'POST'])
@right_required(role='admin')
def editdrink(id):
    form = DrinkForm()
    if id == 0:
        drink = Drink()
    else:
        drink = Drink.query.get(id)
    if form.validate_on_submit():
        drink.description = form.description.data
        drink.price = form.price.data
        drink.active = form.active.data
        drink.stock_active = form.stock.data
        drink.highlight = form.highlight.data
        if id == 0:
            db.session.add(drink)
        db.session.commit()
        flash(_('Gespeichert'))
        return redirect(url_for('main.managedrinks'))
    form.description.data = drink.description
    form.price.data = drink.price
    form.active.data = drink.active
    form.stock.data = drink.stock_active
    form.highlight.data = drink.highlight
    return render_template('admin/editdrink.html', title=_('Barbeiten '), form=form)

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
