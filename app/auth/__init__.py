from flask import Blueprint

auth = Blueprint('auth', __name__, url_prefix='/auth')

from app.auth import views, cli
