from app import app, db, celery
from app.models import Consumption, Invoice, Position
from collections import defaultdict
from app.email import send_email
from flask_login import login_required
import datetime
from flask import jsonify, render_template
import time
import redis

@celery.task
def run_billing():
    userToBeBilled = db.engine.execute('select distinct user_id from consumption where billed = 0')
    for user in userToBeBilled:
        res = billUser(user[0])

def billUser(user):
    cons = Consumption.query.filter_by(user_id=user, billed=False).all()
    cons_by_supplier = defaultdict(list)
    for con in cons:
        cons_by_supplier[con.supplier_id].append(con)
    
    for k,v in cons_by_supplier:
        createInvoice(v)

def createInvoice(inv_data, supplier_id):
    groups = defaultdict(list)
    for c in inv_data:
        groups[c.product].append(c)

    invoice = Invoice(user_id=user, paid=False, date=datetime.datetime.utcnow(), positions=[], supplier_id=supplier_id)
    for k,v in groups.items():
        summe = sum((c.price * c.amount) for c in v)
        amount = sum(c.amount for c in v)
        p = Position(amount=amount, sum=summe, invoice=invoice, product=k)
        invoice.positions.append(p)

    for c in inv_data:
        c.billed = True

    invsum = sum(p.sum for p in invoice.positions)
    invoice.sum=invsum
    db.session.add(invoice)
    db.session.commit()
    sendEmail(invoice)

def sendEmail(invoice):
    send_email('[MATE] Deine Rechnung',
               sender=app.config['ADMINS'][0],
               recipients=[invoice.user.email],
               text_body=render_template('mail/invoice.txt',
                                         invoice=invoice),
               html_body=render_template('mail/invoice.html',
                                         invoice=invoice))
