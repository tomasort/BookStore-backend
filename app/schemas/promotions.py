from app.models import Promotions
from app import ma


class PromotionsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Promotions
        include_fk = True

    id = ma.auto_field(dump_only=True)
