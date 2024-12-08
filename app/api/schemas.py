from app import ma
from app.api.models import Book, Author, Genre, Series, Publisher, Language, Provider
from marshmallow import fields


class BookSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Book

    id = ma.auto_field(dump_only=True)  # id is auto-generated, only include it in the output
    title = ma.auto_field()
    isbn_10 = ma.auto_field()
    isbn_13 = ma.auto_field()
    publish_date = ma.auto_field()
    description = ma.auto_field()
    cover_url = ma.auto_field()
    current_price = ma.auto_field()
    previous_price = ma.auto_field()
    cost = ma.auto_field()
    cost_supplier = ma.auto_field()
    physical_format = ma.auto_field()
    number_of_pages = ma.auto_field()
    alejandria_isbn = ma.auto_field()
    physical_dimensions = ma.auto_field()
    weight = ma.auto_field()
    publish_place = ma.auto_field()
    edition_name = ma.auto_field()
    subtitle = ma.auto_field()
    provider_id = ma.auto_field()
    provider = fields.Nested(lambda: ProviderSchema())
    authors = fields.List(fields.Nested(lambda: AuthorSchema()))
    genres = fields.List(fields.Nested(lambda: GenreSchema()))
    publisher_id = ma.auto_field()
    publisher = fields.Nested(lambda: PublisherSchema())
    languages = fields.List(fields.Nested(lambda: LanguageSchema()))
    series = fields.List(fields.Nested(lambda: SeriesSchema()))


class AuthorSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Author

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field()
    birth_date = ma.auto_field()
    death_date = ma.auto_field()
    biography = ma.auto_field()
    other_names = ma.auto_field()
    photo_url = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema()))


class GenreSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Genre

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema()))


class SeriesSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Series

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema()))


class PublisherSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Publisher

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema()))


class LanguageSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Language

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema()))


class ProviderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Provider

    id = ma.auto_field(dump_only=True)
    alejandria_code = ma.auto_field()
    cedula = ma.auto_field()
    name = ma.auto_field()
    url = ma.auto_field()
    address = ma.auto_field()
    phone = ma.auto_field()
    email = ma.auto_field()
    contact_name = ma.auto_field()
    banco = ma.auto_field()
    titular_banco = ma.auto_field()
    rif_banco = ma.auto_field()
    cod_cuenta = ma.auto_field()
    books = fields.List(fields.Nested(lambda: BookSchema()))
