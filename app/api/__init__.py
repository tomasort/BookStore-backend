from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

from app.api.books import books
from app.api.authors import authors
from app.api.genres import genres
from app.api.publishers import publishers
from app.api.series import series
from app.api.languages import languages
from app.api.providers import providers
from app.api.featured_books import featured_books
from app.api.reviews import reviews

api.register_blueprint(authors)
api.register_blueprint(books)
api.register_blueprint(genres)
api.register_blueprint(publishers)
api.register_blueprint(series)
api.register_blueprint(languages)
api.register_blueprint(providers)
api.register_blueprint(featured_books)
api.register_blueprint(reviews)

from app.api import populate
