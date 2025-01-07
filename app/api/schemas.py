from app import ma
from app.api.models import Book, Author, Genre, Series, Publisher, Language, Provider, FeaturedBook
from marshmallow import fields
from app.auth.models import User


class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book

    # Fields for the Book model
    id = ma.auto_field(dump_only=True)  # Read-only field
    title = ma.auto_field(required=True)
    current_price = fields.Decimal(as_string=True)
    previous_price = fields.Decimal(as_string=True)
    price_alejandria = fields.Decimal(as_string=True)
    iva = fields.Decimal(as_string=True)
    cost = fields.Decimal(as_string=True)
    cost_supplier = fields.Decimal(as_string=True)
    average_cost_alejandria = fields.Decimal(as_string=True)
    last_cost_alejandria = fields.Decimal(as_string=True)

    # Relationships
    proviers = fields.List(fields.Nested(lambda: ProviderSchema(exclude=['books']), allow_none=True))
    publishers = fields.List(fields.Nested(lambda: PublisherSchema(exclude=['books']), allow_none=True))
    authors = fields.List(fields.Nested(lambda: AuthorSchema(exclude=['books', 'biography', 'birth_date', 'birth_date_str', 'casa_del_libro_id', 'death_date', 'death_date_str', 'open_library_id', 'other_names']), allow_none=True))
    genres = fields.List(fields.Nested(lambda: GenreSchema(exclude=['books']), allow_none=True))
    languages = fields.List(fields.Nested(lambda: LanguageSchema(exclude=['books']), allow_none=True))
    series = fields.List(fields.Nested(lambda: SeriesSchema(exclude=['books']), allow_none=True))


class AuthorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Author

    id = ma.auto_field(dump_only=True)
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['authors'])))


class GenreSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Genre

    id = ma.auto_field(dump_only=True)
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['genres'])))


class SeriesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Series

    id = ma.auto_field(dump_only=True)
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['series'])))


class PublisherSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Publisher

    id = ma.auto_field(dump_only=True)
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['publishers'])))


class LanguageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Language

    id = ma.auto_field(dump_only=True)
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['languages'])))


class ProviderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Provider

    id = ma.auto_field(dump_only=True)
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['providers'])))


class FeaturedBookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FeaturedBook
        include_fk = True

    id = ma.auto_field(dump_only=True)
    book = fields.Nested(lambda: BookSchema())


class DiscountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FeaturedBook
        include_fk = True

    id = ma.auto_field(dump_only=True)
    book = fields.Nested(lambda: BookSchema())


class ReviewSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FeaturedBook
        include_fk = True

    id = ma.auto_field(dump_only=True)
    book = fields.Nested(lambda: BookSchema(exclude=['reviews']))
    user = fields.Nested(lambda: UserSchema(exclude=['reviews']))
