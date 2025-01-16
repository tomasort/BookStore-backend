from datetime import datetime
from app import db
from decimal import Decimal
import sqlalchemy as sa
from typing import Optional
import sqlalchemy.orm as so


class Order(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    total: so.Mapped[Decimal] = so.mapped_column(sa.Numeric(10, 2), nullable=False)
    items: so.Mapped[list["OrderItem"]] = so.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    tracking_number: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50))

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

    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    user: so.Mapped["User"] = so.relationship("User", back_populates="orders")

    tax: so.Mapped[Decimal] = so.mapped_column(sa.Numeric(10, 2), nullable=False, default=0)
    status: so.Mapped[str] = so.mapped_column(sa.String, nullable=False, default="pending")
    date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, nullable=False, default=datetime.now)

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
