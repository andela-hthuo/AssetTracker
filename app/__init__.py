from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

from app.assets import assets

import config

app = Flask(__name__)

# Config
app.config.from_object(config)
app.config.from_envvar('FLASK_CONFIG_FILE')

# initialize Flask-SQLAlchemy
db = SQLAlchemy(app)

# initialize Flask-Bootstrap
Bootstrap(app)

# initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# initialize Flask-Mail
mail = Mail(app)

# Register assets blueprint
app.register_blueprint(assets, url_prefix='/assets')

import views
