# from app import ma
# from app.api.models import Book, Author, Genre, Series, Publisher, Language, Provider, FeaturedBook, Review, Discount
# from marshmallow import fields


# class BookSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Book

#     # Fields for the Book model
#     id = ma.auto_field(dump_only=True)  # Read-only field
#     title = ma.auto_field(required=True)
#     current_price = fields.Decimal(as_string=True)
#     previous_price = fields.Decimal(as_string=True)
#     price_alejandria = fields.Decimal(as_string=True)
#     iva = fields.Decimal(as_string=True)
#     cost = fields.Decimal(as_string=True)
#     cost_supplier = fields.Decimal(as_string=True)
#     average_cost_alejandria = fields.Decimal(as_string=True)
#     last_cost_alejandria = fields.Decimal(as_string=True)

#     # Relationships
#     providers = fields.Nested('ProviderSchema', exclude=['books'], allow_none=True, many=True)
#     publishers = fields.Nested('PublisherSchema', exclude=['books'], allow_none=True, many=True)
#     authors = fields.Nested('AuthorSchema', exclude=['books', 'biography', 'birth_date', 'birth_date_str', 'casa_del_libro_id', 'death_date', 'death_date_str', 'open_library_id', 'other_names'], allow_none=True, many=True)
#     genres = fields.Nested('GenreSchema', exclude=['books'], allow_none=True, many=True)
#     languages = fields.Nested('LanguageSchema', exclude=['books'], allow_none=True, many=True)
#     series = fields.Nested('SeriesSchema', exclude=['books'], allow_none=True, many=True)
#     reviews = fields.Nested('ReviewSchema', exclude=['book'], many=True, allow_none=True)


# class AuthorSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Author

#     id = ma.auto_field(dump_only=True)
#     books = fields.Nested('BookSchema', many=True, exclude=['authors'])


# class GenreSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Genre

#     id = ma.auto_field(dump_only=True)
#     books = fields.Nested('BookSchema', many=True, exclude=['genres'])


# class SeriesSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Series

#     id = ma.auto_field(dump_only=True)
#     books = fields.Nested('BookSchema', many=True, exclude=['series'])


# class PublisherSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Publisher

#     id = ma.auto_field(dump_only=True)
#     books = fields.Nested('BookSchema', many=True, exclude=['publishers'])


# class LanguageSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Language

#     id = ma.auto_field(dump_only=True)
#     books = fields.Nested('BookSchema', many=True, exclude=['languages'])


# class ProviderSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Provider

#     id = ma.auto_field(dump_only=True)
#     books = fields.Nested('BookSchema', many=True, exclude=['providers'])


# class FeaturedBookSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = FeaturedBook
#         include_fk = True

#     id = ma.auto_field(dump_only=True)
#     book = fields.Nested("BookSchema")


# class DiscountSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Discount
#         include_fk = True

#     id = ma.auto_field(dump_only=True)
#     book = fields.Nested("BookSchema")


# class ReviewSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Review
#         include_fk = True

#     id = ma.auto_field(dump_only=True)
#     book = fields.Nested('BookSchema', exclude=['reviews'])
#     user = fields.Nested('UserSchema', exclude=['reviews'])
