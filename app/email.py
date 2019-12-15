from flask_mail import Message
from app import mail, app
from threading import Thread
from flask import render_template
from flask_babel import _

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_invoice(inv):
    send_email(_('[MATE] Du hast eine neue Rechnung'),
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('mail/invoice.txt',
                                         invoice=inv),
                html_body=render_template('mail/invoice.html',
                                          invoice=inv))

def send_welcome_mail(user):
    send_email(_('[MATE] Halloo'),
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('mail/newuser.txt',
                                         username=user.username),
                html_body=render_template('mail/newuser.html',
                                          username=user.username))

def send_activated_mail(user):
    send_email(_('[MATE] Du wurdest aktiviert'),
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('mail/activeuser.txt',
                                         user=user),
                html_body=render_template('mail/activeuser.html',
                                          user=user))
