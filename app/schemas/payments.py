from app.models import Payment, StripePayment, PayPalPayment, PagoMovilPayment, ZellePayment
from marshmallow import ValidationError, fields
from app import ma


class StripePaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StripePayment

    id = fields.Int(dump_only=True)


class PayPalPaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PayPalPayment

    id = fields.Int(dump_only=True)


class PagoMovilPaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PagoMovilPayment

    id = fields.Int(dump_only=True)


class ZellePaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ZellePayment

    id = fields.Int(dump_only=True)


class PaymentSchema(ma.SQLAlchemyAutoSchema):
    """Polymorphic Payment schema."""

    class Meta:
        model = Payment

    type_map = {
        "Pago Movil": PagoMovilPaymentSchema,
        "Zelle": ZellePaymentSchema,
        "Stripe": StripePaymentSchema,
        "PayPal": PayPalPaymentSchema,
    }

    def dump(self, obj, *, many: bool = None):
        result = []
        errors = {}
        many = self.many if many is None else bool(many)

        if not many:
            return self._dump(obj)

        for idx, value in enumerate(obj):
            try:
                res = self._dump(value)
                result.append(res)
            except ValidationError as error:
                errors[idx] = error.normalized_messages()
                result.append(error.valid_data)

        if errors:
            raise ValidationError(errors, data=obj, valid_data=result)

        return result

    def _dump(self, obj):
        payment_type = getattr(obj, "type", None)
        inner_schema_class = self.type_map.get(payment_type)

        if inner_schema_class is None:
            raise ValidationError(f"Missing schema for payment type '{payment_type}'")

        inner_schema = inner_schema_class()
        return inner_schema.dump(obj)

    def load(self, data, *, many: bool = None, partial: bool = False):
        payment_type = data.get("type")
        inner_schema_class = self.type_map.get(payment_type)

        if inner_schema_class is None:
            raise ValidationError(f"Missing schema for payment type '{payment_type}'")

        inner_schema = inner_schema_class()
        return inner_schema.load(data, many=many, partial=partial)
