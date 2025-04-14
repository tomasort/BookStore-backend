from app import ma
from app.models import Book, Author, Genre, Series, Publisher, Language, Provider, FeaturedBook, Cover, AuthorPhoto
from datetime import datetime
from marshmallow import fields, ValidationError


# Custom DateTime field
class DateTimeField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValidationError("Invalid date format. Expected 'YYYY-MM-DD HH:MM:SS'.")


class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book

    def get_cover_url(self, obj):
        return obj.cover_url

    cover_url = fields.Method("get_cover_url", dump_only=True)
    # Fields for the Book model
    type = ma.auto_field(dump_only=True)  # Read-only field
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
    rating = fields.Decimal(as_string=True)

    # # Example date field
    # publish_date = DateTimeField(allow_none=True)
    # Replace your custom DateTimeField with Marshmallow's Date field
    publish_date = fields.Date(allow_none=True)

    # Relationships
    providers = fields.Nested('ProviderSchema', exclude=['books'], allow_none=True, many=True)
    publishers = fields.Nested('PublisherSchema', exclude=['books'], allow_none=True, many=True)
    authors = fields.Nested('AuthorSchema', exclude=['books', 'biography', 'birth_date', 'birth_date_str', 'casa_del_libro_id', 'death_date', 'death_date_str', 'open_library_id', 'other_names'], allow_none=True, many=True)
    genres = fields.Nested('GenreSchema', exclude=['books'], allow_none=True, many=True)
    languages = fields.Nested('LanguageSchema', exclude=['books'], allow_none=True, many=True)
    series = fields.Nested('SeriesSchema', exclude=['books'], allow_none=True, many=True)
    reviews = fields.Nested('ReviewSchema', exclude=['book'], many=True, allow_none=True)


class CoverSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cover

    id = ma.auto_field(dump_only=True)
    books = fields.Nested('BookSchema', many=True, exclude=['covers'])


class AuthorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Author

    def get_photo_url(self, obj):
        return obj.photo_url

    id = ma.auto_field(dump_only=True)
    books = fields.Nested('BookSchema', many=True, exclude=['authors'])
    photo_url = fields.Method("get_photo_url", dump_only=True)


class AuthorPhotoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AuthorPhoto

    id = ma.auto_field(dump_only=True)
    author = fields.Nested('AuthorSchema', many=True, exclude=['photos'])


class GenreSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Genre

    id = ma.auto_field(dump_only=True)
    books = fields.Nested('BookSchema', many=True, exclude=['genres'])


class SeriesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Series

    id = ma.auto_field(dump_only=True)
    books = fields.Nested('BookSchema', many=True, exclude=['series'])


class PublisherSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Publisher

    id = ma.auto_field(dump_only=True)
    books = fields.Nested('BookSchema', many=True, exclude=['publishers'])


class LanguageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Language

    id = ma.auto_field(dump_only=True)
    books = fields.Nested('BookSchema', many=True, exclude=['languages'])


class ProviderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Provider

    id = ma.auto_field(dump_only=True)
    books = fields.Nested('BookSchema', many=True, exclude=['providers'])


class FeaturedBookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FeaturedBook
        include_fk = True

    id = ma.auto_field(dump_only=True)
    book = fields.Nested("BookSchema")
