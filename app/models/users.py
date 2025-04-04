import sqlalchemy as sa
import enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import sqlalchemy.orm as so
from typing import Optional, List
from app import db


class AccountStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class Role(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    STAFF = "staff"


favorite_books = sa.Table(
    'favorite_books',
    db.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
    sa.Column('book_id', sa.Integer, sa.ForeignKey('book.id', ondelete="CASCADE"), primary_key=True)
)

wishlist_books = sa.Table(
    'wishlist_books',
    db.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
    sa.Column('book_id', sa.Integer, sa.ForeignKey('book.id', ondelete="CASCADE"), primary_key=True)
)

user_promotions = sa.Table(
    'user_promotions',
    db.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
    sa.Column('promotion_id', sa.Integer, sa.ForeignKey('promotions.id', ondelete="CASCADE"), primary_key=True)
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
    verified: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    role: so.Mapped[Role] = so.mapped_column(db.Enum(Role), nullable=False, default=Role.USER)
    status: so.Mapped[AccountStatus] = so.mapped_column(db.Enum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE)
    newsletter_subscription: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == Role.ADMIN

    def is_staff(self):
        return self.role == Role.STAFF
