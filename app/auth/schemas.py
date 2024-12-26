from app import ma
from marshmallow import fields
from app.auth.models import User
from app.orders.models import Order


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field(dump_only=True)
    username = ma.auto_field()
    email = ma.auto_field()
    password_hash = ma.auto_field()
    active = ma.auto_field()
    orders = fields.Nested('OrderSchema', many=True, exclude=('user', ))
