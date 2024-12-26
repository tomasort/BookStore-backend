from flask import Blueprint

featured_books = Blueprint("featured_books", __name__, url_prefix="/featured_books")

from app.api.featured_books import views
