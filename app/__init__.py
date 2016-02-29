from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CsrfProtect

from config import config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CsrfProtect()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name) or config.get('default'))

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    Bootstrap(app)

    from app.assets import assets as assets_blueprint
    from app.auth import auth as auth_blueprint
    from app.account import account as account_blueprint
    app.register_blueprint(assets_blueprint, url_prefix='/assets')
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(account_blueprint)

    with app.app_context():
        import views

    return app
