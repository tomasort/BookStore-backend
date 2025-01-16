import sqlalchemy as sa
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import sqlalchemy.orm as so
from typing import Optional, List
from app import db

favorite_books = sa.Table(
    'favorite_books',
    db.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('book_id', sa.Integer, sa.ForeignKey('book.id'), primary_key=True)
)

wishlist_books = sa.Table(
    'wishlist_books',
    db.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('book_id', sa.Integer, sa.ForeignKey('book.id'), primary_key=True)
)

user_promotions = sa.Table(
    'user_promotions',
    db.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('promotion_id', sa.Integer, sa.ForeignKey('promotions.id'), primary_key=True)
)


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    session_token: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    # Personal Information
    first_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    last_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    phone_number: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    date_of_birth: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime)
    id_number: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    id_type: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))

    # Address Information
    shipping_address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))
    shipping_city: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    shipping_state: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    shipping_country: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    shipping_postal_code: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))

    # Preferences and Settings

    # Account Management
    last_login: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime)

    reviews: so.Mapped[List["Review"]] = so.relationship("Review", back_populates="user", cascade="all, delete-orphan")
    orders: so.Mapped[List["Order"]] = so.relationship("Order", back_populates="user", cascade="all, delete-orphan")
    favorites: so.Mapped[List["Book"]] = so.relationship("Book", secondary=favorite_books)
    wishlist: so.Mapped[List["Book"]] = so.relationship("Book", secondary=wishlist_books)
    promotions: so.Mapped[List["Promotions"]] = so.relationship("Promotions", secondary=user_promotions)
    cart: so.Mapped[Optional["Cart"]] = so.relationship("Cart", back_populates="user")

    preferred_language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(10), default='en')
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.now(timezone.utc))
    role: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20), default='user')  # 'user', 'admin', or 'staff'
    account_type: so.Mapped[str] = so.mapped_column(sa.String(20), default='regular')
    status: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20), default='active')  # 'active', 'inactive', or 'banned'
    newsletter_subscription: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_staff(self):
        return self.role == 'staff'
