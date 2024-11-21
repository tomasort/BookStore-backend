from flask import Blueprint

series = Blueprint('series', __name__, url_prefix='/series')

from app.api.series import views
