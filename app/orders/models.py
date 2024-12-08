import sqlalchemy as sa
from typing import List
import sqlalchemy.orm as so
from datetime import datetime
from decimal import Decimal
from app.api.models import Book
from app import db


class Order(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    customer_id: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, nullable=False, default=datetime.now)
    total: so.Mapped[Decimal] = so.mapped_column(sa.Numeric(10, 2), nullable=False)
    items: so.Mapped[List["OrderItem"]] = so.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status: so.Mapped[str] = so.mapped_column(sa.String, nullable=False, default="pending")

    def __repr__(self):
        return f"<Order {self.id}, customer={self.customer_id}, total={self.total}, items={self.items}>"


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
