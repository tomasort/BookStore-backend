import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from typing import Optional


class Cart(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'), unique=True)

    # Relationships
    user: so.Mapped[Optional['User']] = so.relationship('User', back_populates='cart')
    items: so.Mapped[list['CartItem']] = so.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

    updated_at: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(sa.DateTime, onupdate=sa.func.now())
    created_at: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(sa.DateTime, default=sa.func.now())

    def __repr__(self) -> str:
        return f"<Cart(id={self.id}, user_id={self.user_id})>"


class CartItem(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    cart_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('cart.id'))
    book_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('book.id'))

    # Relationships
    book: so.Mapped['Book'] = so.relationship('Book')
    cart: so.Mapped['Cart'] = so.relationship('Cart', back_populates='items')
    quantity: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False, default=1)
    in_stock: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'book' in kwargs:
            self.in_stock = kwargs['book'].stock > 0

    def __repr__(self) -> str:
        return f"<CartItem(id={self.id}, book_id={self.book_id}, quantity={self.quantity})>"
