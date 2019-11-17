from app import app, db, celery
from .models import Consumption, Invoice, Position
from collections import defaultdict
from flask_login import login_required
import datetime
from flask import jsonify
import time
import redis

@celery.task
def run_billing():
    userToBeBilled = db.engine.execute('select distinct user_id from consumption where billed = 0')
    for user in userToBeBilled:
        res = billUser(user[0])

def billUser(user):
    createInvoice(user)

def createInvoice(user):
    groups = defaultdict(list)
    consumptions = Consumption.query.filter_by(user_id=user, billed=False).all()
    for consumption in consumptions:
        groups[consumption.drink].append(consumption)

    invoice = Invoice(user_id=user, paid=False, date=datetime.datetime.utcnow(), positions=[])
    for k,v in groups.items():
        summe = sum((c.price * c.amount) for c in v)
        amount = sum(c.amount for c in v)
        p = Position(amount=amount, sum=summe, invoice=invoice, drink=k)
        invoice.positions.append(p)

    for consumption in consumptions:
        consumption.billed = True

    invsum = sum(p.sum for p in invoice.positions)
    invoice.sum=invsum
    db.session.add(invoice)
    db.session.commit()
