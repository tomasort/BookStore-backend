import enum
from datetime import datetime
from app import db
from decimal import Decimal
import sqlalchemy as sa
from typing import Optional
import sqlalchemy.orm as so
from sqlalchemy import Enum


class OrderStatus(enum.Enum):
    PENDING = "Pending"
    PAID = "Paid"
    CONFIRMED = "Confirmed"
    SHIPPED = "Shipped"
    CANCELED = "Canceled"


class PaymentMethod(enum.Enum):
    CARD = "Card"
    PAYPAL = "PayPal"
    STRIPE = "Stripe"
    BANK_TRANSFER = "Bank Transfer"
    CASH_ON_DELIVERY = "Cash on Delivery"


class Order(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    items: so.Mapped[list["OrderItem"]] = so.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, nullable=False, default=datetime.now)
    payment_method: so.Mapped[PaymentMethod] = so.mapped_column(db.Enum(PaymentMethod), nullable=False, default=PaymentMethod.CARD)
    status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    tax: so.Mapped[Decimal] = so.mapped_column(sa.Numeric(10, 2), nullable=False, default=0)
    total: so.Mapped[Decimal] = so.mapped_column(sa.Numeric(10, 2), nullable=False)
    shipping_cost: so.Mapped[Decimal] = so.mapped_column(sa.Numeric(10, 2), nullable=False, default=0)

    tracking_number: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50))

    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'), nullable=True)
    user: so.Mapped["User"] = so.relationship("User", back_populates="orders")

    # Address Information
    shipping_address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))
    shipping_city: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    shipping_state: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    shipping_country: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    shipping_postal_code: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))

    # Billing Information (if different from shipping)
    billing_address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))
    billing_city: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    billing_state: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    billing_country: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    billing_postal_code: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))

    def __repr__(self):
        return f"<Order {self.id}, customer={self.user_id}, total={self.total}, items={self.items}>"


class OrderItem(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    order_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('order.id'), nullable=False)
    order: so.Mapped["Order"] = so.relationship("Order", back_populates="items")
    book: so.Mapped["Book"] = so.relationship("Book")  # Add this relationship
    book_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('book.id'), nullable=False)
    quantity: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    price: so.Mapped[Decimal] = so.mapped_column(sa.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<OrderItem {self.id}, book={self.book}>"
