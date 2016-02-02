from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

import config

app = Flask(__name__)

# Config
app.config.from_object(config)
app.config.from_envvar('FLASK_CONFIG_FILE')

# Flask-SQLAlchemy
db = SQLAlchemy(app)

# Flask-Bootstrap
Bootstrap(app)

import views
