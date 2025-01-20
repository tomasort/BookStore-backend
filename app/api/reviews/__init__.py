from flask import Blueprint

reviews = Blueprint("reviews", __name__, url_prefix="/reviews")

from app.api.reviews import views
