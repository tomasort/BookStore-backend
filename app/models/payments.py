import enum
from abc import ABC, abstractmethod
from app import db
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import inspect


def get_polymorphic_subclasses(parent_class):
    mapper = inspect(parent_class)

    # If this is a polymorphic base
    if hasattr(mapper.polymorphic_map, 'values'):
        # Get all subclass mappers
        subclass_mappers = [m for m in mapper.polymorphic_map.values()
                            if m.class_ != parent_class]
        return [m.class_ for m in subclass_mappers]
    return []


class PaymentStatus(enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELED = "Canceled"


class Payment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    order_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('order.id'), nullable=False)
    order: so.Mapped["Order"] = so.relationship("Order", back_populates="payment", uselist=False)
    type: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "Payment",
        "polymorphic_on": "type",
    }

    @staticmethod
    def get_payment_methods():
        subclasses = get_polymorphic_subclasses(Payment)
        return [s.__mapper_args__.get('polymorphic_identity') for s in subclasses]

    @staticmethod
    def create_payment(payment_type: str, **kwargs) -> "Payment":
        payment_classes = {
            "Zelle": ZellePayment,
            "Pago Movil": PagoMovilPayment,
            # "Stripe": StripePayment,
        }
        if payment_type not in payment_classes:
            raise ValueError(f"Unsupported payment type: {payment_type}")
        return payment_classes[payment_type](**kwargs)

    def process_payment(self):
        raise NotImplementedError("Subclasses must implement a process_payment method.")

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, type={self.type}, status={self.status})>"


class ZellePayment(Payment):
    __tablename__ = "zelle_payment"
    id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("payment.id"), primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    phone_number: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "Zelle",
    }

    def process_payment(self):
        # Implement Zelle payment processing logic here
        print(f"Processing Zelle payment for {self.email} and {self.phone_number}")
        pass


class PagoMovilPayment(Payment):
    __tablename__ = "pago_movil_payment"
    id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("payment.id"), primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    phone_number: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "Pago Movil",
    }

    def process_payment(self):
        # Implement Zelle payment processing logic here
        print(f"Processing Pago Movil for {self.email} and {self.phone_number}")
        pass


class StripePayment(Payment):
    __tablename__ = "stripe_payment"
    id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("payment.id"), primary_key=True)
    stripe_account_id: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "Stripe",
    }


class PayPalPayment(Payment):
    __tablename__ = "paypal_payment"
    id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("payment.id"), primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "PayPal",
    }
