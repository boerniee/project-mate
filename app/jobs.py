from app import app, db, celery
from celery.schedules import crontab
from app.models import Drink
import os

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour=0, minute=0, day_of_week='*'), image_cleanup.s())

@celery.task
def image_cleanup():
    print('Cleaning up images')
    for root, dirs, files in os.walk(app.config['IMAGE_UPLOAD_FOLDER']):
        for filename in files:
            list = Drink.query.filter(Drink.imageUrl==filename).all()
            if len(list) < 1:
                print("deleting image: " + filename)
                os.remove(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
