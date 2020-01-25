from app import app, db, celery
from celery.schedules import crontab
from app.models import Drink
import os

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour=0, minute=0, day_of_week='*'), image_cleanup.s())

@celery.task
def image_cleanup():
    pass
