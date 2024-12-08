from app.api.providers import views
from flask import Blueprint

providers = Blueprint('providers', __name__, url_prefix='/providers')
