from typing import Optional
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class Review(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    book_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('book.id'))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'))
    rating: so.Mapped[int] = so.mapped_column(sa.Integer)  # 1-5 stars
    comment: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    # Relationships
    book: so.Mapped["Book"] = so.relationship("Book", back_populates="reviews")
    user: so.Mapped["User"] = so.relationship("User", back_populates="reviews")
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=sa.func.now())

    def __repr__(self):
        return f'<Review(id={self.id}, comment={self.comment})>'
