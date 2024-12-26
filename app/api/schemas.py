from app import ma
from app.api.models import Book, Author, Genre, Series, Publisher, Language, Provider, FeaturedBook
from marshmallow import fields


class BookSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Book

    # Fields for the Book model
    id = ma.auto_field(dump_only=True)  # Read-only field
    title = ma.auto_field(required=True)
    isbn_10 = ma.auto_field()
    isbn_13 = ma.auto_field()
    publish_date = ma.auto_field()
    description = ma.auto_field()
    cover_url = ma.auto_field()
    current_price = fields.Decimal(as_string=True)
    previous_price = fields.Decimal(as_string=True)
    price_alejandria = fields.Decimal(as_string=True)
    iva = fields.Decimal(as_string=True)
    cost = fields.Decimal(as_string=True)
    cost_supplier = fields.Decimal(as_string=True)
    average_cost_alejandria = fields.Decimal(as_string=True)
    last_cost_alejandria = fields.Decimal(as_string=True)
    stock = ma.auto_field()
    stock_alejandria = ma.auto_field()
    stock_consig = ma.auto_field()
    stock_consig_alejandria = ma.auto_field()
    physical_format = ma.auto_field()
    number_of_pages = ma.auto_field()
    bar_code_alejandria = ma.auto_field()
    isbn_alejandria = ma.auto_field()
    code_alejandria = ma.auto_field()
    physical_dimensions = ma.auto_field()
    weight = ma.auto_field()
    publish_places = ma.auto_field()
    edition_name = ma.auto_field()
    subtitle = ma.auto_field()

    # Relationships
    proviers = fields.List(fields.Nested(lambda: ProviderSchema(exclude=['books']), allow_none=True))
    publishers = fields.List(fields.Nested(lambda: PublisherSchema(exclude=['books']), allow_none=True))
    authors = fields.List(fields.Nested(lambda: AuthorSchema(exclude=['books']), allow_none=True))
    genres = fields.List(fields.Nested(lambda: GenreSchema(exclude=['books']), allow_none=True))
    languages = fields.List(fields.Nested(lambda: LanguageSchema(exclude=['books']), allow_none=True))
    series = fields.List(fields.Nested(lambda: SeriesSchema(exclude=['books']), allow_none=True))


class AuthorSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Author

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field()
    birth_date = ma.auto_field()
    birth_date_str = ma.auto_field()
    death_date = ma.auto_field()
    death_date_str = ma.auto_field()
    biography = ma.auto_field()
    other_names = ma.auto_field()
    photo_url = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['authors'])))
    open_library_id = ma.auto_field()
    casa_del_libro_id = ma.auto_field()


class GenreSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Genre

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['genres'])))


class SeriesSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Series

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['series'])))


class PublisherSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Publisher

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['publishers'])))


class LanguageSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Language

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['languages'])))


class ProviderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Provider

    id = ma.auto_field()
    alejandria_code = ma.auto_field()
    cedula = ma.auto_field()
    name = ma.auto_field()
    url = ma.auto_field()
    address = ma.auto_field()
    phone = ma.auto_field()
    email = ma.auto_field()
    contact_name = ma.auto_field()
    nombre_banco = ma.auto_field()
    titular_banco = ma.auto_field()
    rif_banco = ma.auto_field()
    cod_cuenta = ma.auto_field()
    notes = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['providers'])))


class FeaturedBookSchema(ma.SQLAlchemySchema):
    class Meta:
        model = FeaturedBook

    id = ma.auto_field(dump_only=True)
    book_id = ma.auto_field()
    featured_date = ma.auto_field()
    expiry_date = ma.auto_field()
    priority = ma.auto_field()

    book = fields.Nested(lambda: BookSchema())
