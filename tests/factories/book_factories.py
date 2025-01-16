from app.models import Author, Book, Publisher, Genre, Language, Series, Provider, FeaturedBook
import random
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
    publish_date = factory.Faker('date_object')
    description = factory.Faker('text')
    current_price = factory.Faker('pyfloat', right_digits=2, positive=True, min_value=10, max_value=100)
    previous_price = factory.Faker('pyfloat', min_value=3, max_value=200, right_digits=2, positive=True)
    price_alejandria = factory.Faker('pyfloat', right_digits=2, positive=True, min_value=5, max_value=150)
    iva = factory.Faker('pyfloat', right_digits=2, positive=True, min_value=1, max_value=20)
    cost = factory.Faker('pyfloat', right_digits=2, positive=True, min_value=5, max_value=150)
    cost_supplier = factory.Faker('pyfloat', right_digits=2, positive=True, min_value=5, max_value=150)
    average_cost_alejandria = factory.Faker('pyfloat', right_digits=2, positive=True, min_value=5, max_value=150)
    last_cost_alejandria = factory.Faker('pyfloat', right_digits=2, positive=True, min_value=5, max_value=150)
    stock = factory.Faker('random_int', min=0, max=500)
    stock_alejandria = factory.Faker('random_int', min=0, max=500)
    stock_consig = factory.Faker('random_int', min=0, max=500)
    stock_consig_alejandria = factory.Faker('random_int', min=0, max=500)
    physical_format = factory.Faker('random_element', elements=('Hardcover', 'Paperback', 'Ebook'))
    number_of_pages = factory.Faker('random_int', min=100, max=1000)
    bar_code_alejandria = factory.Faker('ean13')
    isbn_alejandria = factory.Faker('isbn13')
    code_alejandria = factory.Faker('ean8')
    physical_dimensions = factory.Faker('random_element', elements=('5x8', '6x9', '8x11'))
    weight = factory.Faker('random_element', elements=('1lb', '2lb', '3lb'))
    publish_places = factory.LazyAttribute(lambda _: [factory.Faker('city').evaluate({}, None, {'locale': None}) for _ in range(3)])
    edition_name = factory.Faker('sentence', nb_words=3)
    authors = factory.LazyAttribute(lambda _: [AuthorFactory() for _ in range(random.randint(1, 3))])


class AuthorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Author
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker('name')
    birth_date = factory.Faker('date_object')
    birth_date_str = factory.LazyAttribute(lambda o: f"{o.birth_date.year}-{o.birth_date.month}-{o.birth_date.day}")
    death_date = factory.Faker('date_object')
    death_date_str = factory.LazyAttribute(lambda o: f"{o.death_date.year}-{o.death_date.month}-{o.death_date.day}")
    biography = factory.Faker('paragraph')
    other_names = factory.LazyAttribute(lambda _: [factory.Faker('name').evaluate({}, None, {'locale': None}) for _ in range(3)])
    open_library_id = factory.Faker('isbn13')
    casa_del_libro_id = factory.Faker('isbn13')


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


class ProviderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Provider
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    alejandria_code = factory.Faker('random_int', min=1, max=1000)
    cedula = factory.Faker('random_element', elements=[
        'V185262398',
        'J412245562',
        'J406802794',
        'V131134785',
        'J408153173',
        'V10338653',
        'J406271691',
        'V6446257',
        'J307761296',
        'V067305244',
        'J001633308',
        'J317582888',
        'V3156101',
    ])
    name = factory.Faker('name')
    url = factory.Faker('url')
    address = factory.Faker('address')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    contact_name = factory.Faker('name')
    nombre_banco = factory.Faker('random_element', elements=[
        'BANCO DE VENEZUELA',
        'BANCO VENEZOLANO DE CREDITO',
        'BANCO MERCANTIL',
        'BANCO PROVINCIAL',
        'BANCARIBE',
        'BANCO EXTERIOR',
        'BANESCO BANCO UNIVERSAL',
        'BANCAMIGA BANCO UNIVERSAL',
        'BANPLUS',
        'BANCO NACIONAL DE CREDITO',
    ])
    titular_banco = factory.Faker('name')
    rif_banco = factory.Faker('random_element', elements=[
        'J000000000',
        'V000000000',
        'V13113478',
        'J408153173',
        'V10338653',
        '4681359',
        'V6446257',
        'J-30776129-6',
        'V67305244',
        'J001633308',
    ])
    cod_cuenta = factory.Faker('random_int', min=100000000000, max=999999999999)
    notes = factory.Faker('paragraph')
    books = factory.LazyAttribute(lambda _: [BookFactory() for _ in range(random.randint(1, 5))])


class FeaturedBookFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FeaturedBook
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    featured_date = factory.Faker('past_date')
    expiry_date = factory.Faker('future_date')
    priority = factory.Faker('random_int', min=1, max=5)
    book = factory.SubFactory(BookFactory)  # Reference an existing BookFactory
