from app import app, db, celery
from app.models import Consumption, Invoice, Position, User
from collections import defaultdict
from app.email import send_email
from flask_login import login_required
import datetime
from flask import jsonify, render_template
import time
import redis
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery.task
def run_billing():
    res = db.engine.execute('select distinct user_id from consumption where billed = 0')
    userToBeBilled = [i[0] for i in res]
    res.close()
    for user in userToBeBilled:
        u = User.query.get(user)
        res = billUser(u)
        db.session.commit()
    send_emails.delay()

@celery.task
def send_emails():
    invoices = Invoice.query.filter(Invoice.sent == False).all()
    for invoice in invoices:
        sendEmail(invoice)

def billUser(user):
    cons = db.session.query(Consumption).filter(Consumption.user==user, Consumption.billed==False).all()
    cons_by_supplier = defaultdict(list)
    for con in cons:
        cons_by_supplier[con.supplier_id].append(con)
    for k,v in cons_by_supplier.items():
        createInvoice(v, k, user)

def createInvoice(inv_data, supplier_id, user):
    groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for c in inv_data:
        if c.amount > 0:
            groups[c.product][c.price]['+'].append(c)
        else:
            groups[c.product][c.price]['-'].append(c)

    invoice = Invoice(user=user, sent=(user.id == supplier_id), paid=(user.id == supplier_id), date=datetime.datetime.utcnow(), positions=[], supplier_id=supplier_id)

    for product, pricedict in groups.items():
        for price, consumptions in pricedict.items():
            if len(consumptions['+']) > 0:
                summe = sum((c.price * c.amount) for c in consumptions['+'])
                amount = sum(c.amount for c in consumptions['+'])
                p = Position(amount=amount, price=price, sum=summe, invoice=invoice, product=product)
                invoice.positions.append(p)
            if len(consumptions['-']) > 0:
                summe = sum((c.price * c.amount) for c in consumptions['-'])
                amount = sum(c.amount for c in consumptions['-'])
                p = Position(amount=amount, price=price, sum=summe, invoice=invoice, product=product)
                invoice.positions.append(p)

    for c in inv_data:
        c.billed = True

    invsum = float("{0:.2f}".format(sum(p.sum for p in invoice.positions)))
    invoice.sum=invsum
    db.session.add(invoice)

def sendEmail(invoice):
    send_email('Deine Rechnung',
               sender=app.config['ADMINS'][0],
               recipients=[invoice.user.email],
               text_body=render_template('mail/invoice.txt',
                                         invoice=invoice),
               html_body=render_template('mail/invoice.html',
                                         invoice=invoice))
