from flask import Blueprint

languages = Blueprint("languages", __name__, url_prefix="/languages")

from app.api.languages import views
