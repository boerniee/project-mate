import pyqrcode
from io import BytesIO
from app.auth.forms import OtpForm
from app import db
from app.auth import bp
from app.models import User
from flask_login import current_user, login_required
from flask import render_template, session, redirect, url_for, request, abort, flash
from app.auth.routes import login
from flask_babel import _
from app.email import send_2fa_code

@bp.route('/qrcode')
@login_required
def qrcode():
    if current_user.otp_type() is None:
        abort(404)

    if 'username' in session:
        del session['username']
    url = pyqrcode.create(current_user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=5)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}

@bp.route('/otp', methods=['GET', 'POST'])
def otp_input():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if not 'username' in session:
        return redirect(url_for('auth.login'))
    form = OtpForm()
    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        return redirect(url_for('auth.login'))
    if user.otp_type() == 'hotp' and 'resend' in request.args:
        send_2fa_code(user)
        flash(_('Code wurde versendet'))
        return redirect(url_for('auth.otp_input'))
    if form.validate_on_submit():
        if user.verify_otp(form.otp.data):
            del session['username']
            return login(user, session.get('next'))
        flash(_('Code nicht gültig'))
        form.otp.data = None
    return render_template('auth/otp_input.html', form=form, user=user)

@bp.route('/activate_otp')
@login_required
def activate_otp():
    # TODO choose hotp or totp
    if current_user.otp_type() is None and 'type' not in request.args:
        return render_template('auth/choose_2fa.html')

    if current_user.otp_type() is None:
        hotp = request.args.get('type') == 'hotp'
        current_user.activate_otp(hotp=hotp)
        db.session.commit()
    return render_template('auth/setup_2fa.html')

@bp.route('/deactivate_otp')
@login_required
def deactivate_otp():
    current_user.deactivate_otp()
    db.session.commit()
    return redirect(url_for('auth.editself'))
