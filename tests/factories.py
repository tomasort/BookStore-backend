from app.api.models import Author, Book, Publisher, Genre, Language, Series
import factory
from app import db


class BookFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Book
        # Use the SQLAlchemy session for database transactions
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    title = factory.Faker('sentence')
    subtitle = factory.Faker('sentence')
    isbn_10 = factory.Faker('isbn10')
    isbn_13 = factory.Faker('isbn13')
    alejandria_isbn = factory.Faker('isbn13')
    publish_date = factory.Faker('date_object')
    description = factory.Faker('text')
    current_price = factory.Faker(
        'pyfloat', right_digits=2, positive=True, min_value=10, max_value=100)
    cover_url = factory.Faker('image_url')
    current_price = factory.Faker(
        'pyfloat', min_value=3, max_value=200, right_digits=2, positive=True)
    previous_price = factory.Faker(
        'pyfloat', min_value=3, max_value=200, right_digits=2, positive=True)
    physical_format = factory.Faker(
        'random_element', elements=('Hardcover', 'Paperback', 'Ebook'))
    number_of_pages = factory.Faker('random_int', min=100, max=1000)
    physical_dimensions = factory.Faker(
        'random_element', elements=('5x8', '6x9', '8x11'))
    weight = factory.Faker('random_element', elements=('1lb', '2lb', '3lb'))
    publish_place = factory.Faker('city')
    edition_name = factory.Faker('sentence', nb_words=3)


class AuthorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Author
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker('name')
    birth_date = factory.Faker('date_object')
    death_date = factory.Faker('date_object')
    biography = factory.Faker('paragraph')


class GenreFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Genre
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker('random_element', elements=[
        "Fiction",
        "Non-Fiction",
        "Mystery",
        "Fantasy",
        "Science Fiction",
        "Romance",
        "Thriller",
        "Historical Fiction",
        "Horror",
        "Biography",
        "Young Adult",
        "Poetry",
        "Self-Help",
        "Memoir",
        "Graphic Novel"
    ])


class PublisherFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Publisher
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker('name')


class LanguageFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Language
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker('language_name')


class SeriesFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Series
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker('sentence', nb_words=3)
