from app.models import Discount
from marshmallow import fields
from app import ma


class DiscountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Discount
        include_fk = True

    id = ma.auto_field(dump_only=True)
    book = fields.Nested("BookSchema")
