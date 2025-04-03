from app.models import User, AccountStatus, Role
from marshmallow import fields
from app import ma


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

    id = ma.auto_field(dump_only=True)
    orders = fields.Nested('OrderSchema', many=True, exclude=('user', ))
    favorites = fields.Nested('BookSchema', many=True)
    wishlist = fields.Nested('BookSchema', many=True)
    cart = fields.Nested('CartSchema', exclude=('user', ), dump_only=True)
    status = fields.Enum(AccountStatus, by_value=True)
    role = fields.Enum(Role, by_value=True)
    reviews = fields.Nested('ReviewSchema', many=True, exclude=('user', ))
