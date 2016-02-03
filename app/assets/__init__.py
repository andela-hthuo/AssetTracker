from flask import Blueprint

assets = Blueprint('assets', __name__)
from app.assets import views
