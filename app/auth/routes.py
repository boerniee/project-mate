from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from app.models import User
from app.email import send_welcome_mail, send_activated_mail
from app.auth.email import send_password_reset_email

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Bitte kontrolliere deine Email für weitere anweisungen')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Passwort zurücksetzen', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Dein Passwort wurde zurückgesetzt.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Passwort zurücksetzen', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Falscher benutzername oder passwort')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', title='Einloggen', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, active=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Erfolgreich registriert, warte bitte auf die Freischaltung!')
        send_welcome_mail(user)
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Registrieren', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
