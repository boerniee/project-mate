from app import db, app
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm, ChangePasswordForm, ResetPasswordRequestForm, EditProfile, ChangeEmailForm
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User
from app.email import send_welcome_mail, send_activated_mail
from app.auth.email import send_password_reset_email, send_change_email_mail
from flask_babel import _, get_locale, refresh, lazy_gettext as _l

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def editself():
    form = EditProfile()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        user.lang = form.lang.data
        user.paypal = form.paypal.data
        if user.username != form.username.data:
            user.username = form.username.data
        db.session.commit()
        flash(_l('Gespeichert'))
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.paypal.data = current_user.paypal
    form.lang.data = current_user.lang or app.config['BABEL_DEFAULT_LOCALE']
    refresh()
    return render_template('auth/edit_self.html', form=form, avatar=current_user.avatar(175))

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            send_password_reset_email(user)
        flash(_('Bitte kontrolliere deine Emails für weitere anweisungen'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Passwort zurücksetzen'), form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash(_('Token ungültig'))
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Dein Passwort wurde zurückgesetzt.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Falscher benutzername oder passwort'))
        else:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data.lower(), active=False, lang=get_locale().language)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Erfolgreich registriert, warte bitte auf die Freischaltung!'))
        send_welcome_mail(user)
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@bp.route('/change_email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    user = User.verify_change_email_token(token)
    if not user or not current_user.id == user.id:
        flash(_('Token ungültig'))
        db.session.rollback()
        return redirect(url_for('main.index'))
    db.session.commit()
    flash(_("Deine Email Adresse wurde zu '%(value)s' geändert", value=user.email))
    return redirect(url_for('main.index'))

@bp.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.email == form.new_email.data.lower():
            return redirect(url_for('main.index'))
        send_change_email_mail(current_user, form.new_email.data)
        flash(_('Bitte kontrolliere deine Emails für weitere anweisungen'))
        return redirect(url_for('main.index'))
    return render_template('auth/change_email.html', form=form)

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash(_('Passwort geändert'))
        return redirect(url_for('main.index'))
    return render_template('auth/change_password.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
