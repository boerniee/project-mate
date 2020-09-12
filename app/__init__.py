from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from celery import Celery
from flask_moment import Moment
from flask_mail import Mail
from flask_babel import Babel, get_locale, lazy_gettext as _l
from flask_assets import Environment, Bundle
from babel.core import negotiate_locale
from flask_marshmallow import Marshmallow
from flask import g

def patch_requests_class(app):
    reqclass = app.request_class
    patched = type(reqclass.__name__, (reqclass,),
                   {'max_content_length': 1 * 1024 * 1024})
    app.request_class = patched

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
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
patch_requests_class(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
assets = Environment(app)
moment = Moment(app)
migrate = Migrate(app, db)
babel = Babel(app)
login = LoginManager(app)
login.login_view = 'auth.login'
login.login_message = _l("Bitte logge dich ein.")
celery = make_celery(app)
mail = Mail(app)

js_mate = Bundle('js/dark-mode-switch.min.js', 'js/jquery.cookie.js',
            filters='jsmin', output='gen/clubmate.min.js')
js_product = Bundle('js/product.js',filters='jsmin', output='gen/product.min.js')
js_pwd = Bundle('js/password.js', filters='jsmin', output='gen/password.min.js')
assets.register('js_product', js_product)
assets.register('js_pwd', js_pwd)
assets.register('js_mate', js_mate)

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api/v1')
from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
from app.ajax import bp as ajax_bp
app.register_blueprint(ajax_bp, url_prefix='/ajax')
from app.main import bp as main_bp
app.register_blueprint(main_bp)

app.jinja_env.auto_reload = True

from app import models, billing

@app.before_request
def before_request():
    g.locale = str(get_locale())

@babel.localeselector
def get_locale():
    if current_user is not None and not current_user.is_anonymous:
        return current_user.lang
    preferred = [x.replace('-', '_') for x in request.accept_languages.values()]
    return negotiate_locale(preferred, Config.LANGUAGES.keys())
