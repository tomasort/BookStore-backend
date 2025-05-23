from app.models import Review
from marshmallow import fields
from app import ma


class ReviewSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Review
        include_fk = True

    id = ma.auto_field(dump_only=True)
    book = fields.Nested('BookSchema', exclude=['id', 'title'])
    user = fields.Nested('UserSchema', only=['id', 'username', 'email'])
