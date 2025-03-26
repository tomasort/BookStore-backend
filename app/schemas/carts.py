from marshmallow import fields
from app import ma
from app.models import Cart, CartItem


class CartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cart

    id = ma.auto_field(dump_only=True)
    user = fields.Nested('UserSchema', only=['id', 'username', 'email', 'shipping_address', 'shipping_city', 'shipping_country', 'shipping_postal_code', 'shipping_state'], dump_only=True)
    items = fields.Nested('CartItemSchema', many=True, dump_only=True, exclude=('cart',))


class CartItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CartItem

    id = ma.auto_field(dump_only=True)
    book = fields.Nested('BookSchema', only=('id', 'title', 'subtitle', 'isbn_10', 'isbn_13', 'authors', 'series', 'publishers', 'genres', 'previous_price', 'current_price', 'cover_url', 'rating'), dump_only=True)
    cart = fields.Nested('CartSchema', exclude=('items',))
