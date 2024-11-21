from flask import Blueprint

publishers = Blueprint('publishers', __name__, url_prefix='/publishers')

from app.api.publishers import views
