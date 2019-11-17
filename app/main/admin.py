from app import app, db
from app.main.forms import DrinkForm, UserForm
from flask import render_template, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Drink, Invoice, Role
from app.utils import right_required
from app.email import send_welcome_mail, send_activated_mail
from app.main import bp

@bp.route('/manage/billing')
@right_required(role='admin')
def managebilling():
    return render_template('admin/billing.html', title="Abrechnung")

@bp.route('/manage/user')
@right_required(role='admin')
def manageusers():
    users = User.query.all()
    return render_template('admin/manageusers.html', title='Benutzerverwaltung', users=users)

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
        flash("Gespeichert")
        return redirect(url_for('main.manageusers'))
    form.username.data = user.username
    form.email.data = user.email
    form.active.data = user.active
    form.admin.data = user.has_role('main.admin')
    return render_template('admin/edituser.html', title='Barbeiten ', form=form)

@bp.route('/manage/drink')
@right_required(role='admin')
def managedrinks():
    drinks = Drink.query.order_by(Drink.active.desc()).all()
    return render_template('admin/managedrinks.html', title='Getränkeverwaltung', drinks=drinks)

@bp.route('/manage/drink/edit/<int:id>', methods=['GET', 'POST'])
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
        drink.highlight = form.highlight.data
        if id == 0:
            db.session.add(drink)
        db.session.commit()
        flash("Gespeichert")
        return redirect(url_for('main.managedrinks'))
    form.description.data = drink.description
    form.price.data = drink.price
    form.active.data = drink.active
    form.highlight.data = drink.highlight
    return render_template('admin/editdrink.html', title='Barbeiten ', form=form)

@bp.route('/manage/invoice')
@right_required(role='admin')
def manageinvoices():
    invoices = Invoice.query.filter_by(paid=False).all()
    return render_template('admin/manageinvoices.html', title="Rechnungen verwalten", invoices=invoices)

@bp.route('/manage/invoice/<int:id>/paid')
@right_required(role='admin')
def markinvoiceaspaid(id):
    invoice = Invoice.query.filter_by(id=id).first()
    invoice.paid = True
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/manage/admin')
@right_required(role='superadmin')
def superadmin():
    return render_template('admin/superadmin.html', title='Superadmin')
