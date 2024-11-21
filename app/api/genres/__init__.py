from flask import Blueprint

genres = Blueprint("genres", __name__, url_prefix="/genres")

from app.api.genres import views
