from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

from app.api.books import books
from app.api.authors import authors

api.register_blueprint(authors)
api.register_blueprint(books)

from app.api import models
