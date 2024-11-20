from flask import Blueprint

books = Blueprint("books", __name__, url_prefix="/books")

from app.api.books import views
