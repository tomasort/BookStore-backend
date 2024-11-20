from flask import Blueprint

authors = Blueprint("authors", __name__, url_prefix="/authors")

from app.api.authors import views
