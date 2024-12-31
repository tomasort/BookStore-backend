from app import ma
from app.orders.models import Order, OrderItem
from app.auth.models import User
from app.promotions.models import Promotions
from marshmallow import fields  # Use marshmallow's fields module


class OrderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Order

    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field()
    date = ma.auto_field()
    total = fields.Decimal(as_string=True)
    items = fields.List(fields.Nested(lambda: OrderItemSchema()))
    status = ma.auto_field()
    user = fields.Nested('UserSchema', exclude=('orders', ), allow_none=True)


class OrderItemSchema(ma.SQLAlchemySchema):
    class Meta:
        model = OrderItem

    id = ma.auto_field(dump_only=True)
    order_id = ma.auto_field(dump_only=True)
    book_id = ma.auto_field()
    quantity = ma.auto_field()
    price = fields.Decimal(as_string=True)
