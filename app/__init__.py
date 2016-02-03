from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

import config

app = Flask(__name__)

# Config
app.config.from_object(config)
app.config.from_envvar('FLASK_CONFIG_FILE')

# Flask-SQLAlchemy
db = SQLAlchemy(app)

# Flask-Bootstrap
Bootstrap(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Flask-Mail
mail = Mail(app)

import views
