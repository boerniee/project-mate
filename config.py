import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    PER_PAGE = 10
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL= os.environ.get('REDIS_URL') or 'redis://brnhaed:6378'
    CELERY_RESULT_BACKEND= os.environ.get('REDIS_URL') or 'redis://brnhaed:6378'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['saas@mate.brnhaed.de']
    IMAGE_UPLOAD_FOLDER = os.environ.get('IMAGE_UPLOAD_FOLDER') or '/src/clubmate/app/static/images/'
    LANGUAGES = {
        'de': 'German',
        'en': 'English'
    }
    BABEL_DEFAULT_LOCALE = 'de'
    PAYPAL = os.environ.get('PAYPAL') or 'sooos'
    TEMPLATES_AUTO_RELOAD = True
    SERVER_NAME = os.environ.get('SERVER_NAME') or 'localhost:5000'
    INFORMATION = {
        "version": "1.2.1",
        "name": os.environ.get('PROJECT_NAME') or "Projekt Mate",
        "description": "Sell Mate to your colleagues. Fast! WOW!"
    }
    BETA = 'rc' in INFORMATION['version']
