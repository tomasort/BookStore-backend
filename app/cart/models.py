from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app.api.models import Book
from app.auth.models import User

class CartItem(db.Model):
    __tablename__ = 'cart_item'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    cart_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('shopping_cart.id'))
    book_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('book.id'))
    quantity: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False, default=1)

    # Relationships
    book: so.WriteOnlyMapped['Book'] = so.relationship('Book')
    cart: so.WriteOnlyMapped['ShoppingCart'] = so.relationship('ShoppingCart', back_populates='items')

    def __repr__(self) -> str:
        return f"<CartItem(id={self.id}, book_id={self.book_id}, quantity={self.quantity})>"

class ShoppingCart(db.Model):
    __tablename__ = 'shopping_cart'
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'), unique=True)
    created_at: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(sa.DateTime, default=sa.func.now())
    updated_at: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(sa.DateTime, onupdate=sa.func.now())

    # Relationships
    user: so.WriteOnlyMapped['User'] = so.relationship('User', back_populates='shopping_cart')
    items: so.WriteOnlyMapped[list['CartItem']] = so.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<ShoppingCart(id={self.id}, user_id={self.user_id})>"
