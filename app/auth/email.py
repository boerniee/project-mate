from flask import render_template, current_app
from app.email import send_email
from flask_babel import _

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_('Setze dein tolles Passwort zurück'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('mail/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('mail/reset_password.html',
                                         user=user, token=token))

def send_change_email_mail(user, email):
    token = user.get_new_email_token(email)
    send_email(_('Änderung deiner Email Adresse'),
               sender=current_app.config['ADMINS'][0],
               recipients=[email],
               text_body=render_template('mail/change_email.txt',
                                         user=user, token=token, email=email),
               html_body=render_template('mail/change_email.html',
                                         user=user, token=token, email=email))
