from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

from app.api.books import books
from app.api.authors import authors
from app.api.genres import genres
from app.api.publishers import publishers

api.register_blueprint(authors)
api.register_blueprint(books)
api.register_blueprint(genres)
api.register_blueprint(publishers)

from app.api import models
