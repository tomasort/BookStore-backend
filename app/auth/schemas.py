from app import ma
from marshmallow import fields
from app.auth.models import User
from app.orders.models import Order


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

    id = ma.auto_field(dump_only=True)
    orders = fields.Nested('OrderSchema', many=True, exclude=('user', ))
    favorites = fields.Nested('BookSchema', many=True)
