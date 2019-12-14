from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from celery import Celery
from flask_mail import Mail
from flask_babel import Babel, lazy_gettext as _l
from babel.core import negotiate_locale

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app)
login = LoginManager(app)
login.login_view = 'auth.login'
login.login_message = _l("Bitte logge dich ein.")
celery = make_celery(app)
celery.conf.update(app.config)
mail = Mail(app)

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api/v1')
from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
from app.main import bp as main_bp
app.register_blueprint(main_bp)

app.jinja_env.auto_reload = True

from app import models, billing

@babel.localeselector
def get_locale():
    preferred = [x.replace('-', '_') for x in request.accept_languages.values()]
    return negotiate_locale(preferred, app.config['LANGUAGES'])
