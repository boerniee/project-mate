from flask_mail import Message
from app import mail, app
from threading import Thread
from flask import render_template
from flask_babel import _

def send_email_async(app, msg):
    with app.app_context():
        if app.config['BETA']:
            msg.subject = '[BETA - MATE] ' + msg.subject
        else:
            msg.subject = '[MATE] ' + msg.subject
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body, fif=True):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if fif:
        Thread(target=send_email_async, args=(app, msg)).start()
    else:
        send_email_async(app, msg)

def send_invoice_reminder(inv):
    send_email(_('Friendly Reminder: Unbezahlte Rechnung'),
               sender=app.config['ADMINS'][0],
               recipients=[inv.user.email],
               text_body=render_template('mail/invoice.txt',
                                         invoice=inv),
                html_body=render_template('mail/invoice.html',
                                          invoice=inv),
                fif=False)

def send_welcome_mail(user):
    send_email(_('Halloo'),
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('mail/newuser.txt',
                                         username=user.username),
                html_body=render_template('mail/newuser.html',
                                          username=user.username))

def send_activated_mail(user):
    send_email(_('Du wurdest aktiviert'),
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('mail/activeuser.txt',
                                         user=user),
                html_body=render_template('mail/activeuser.html',
                                          user=user))
