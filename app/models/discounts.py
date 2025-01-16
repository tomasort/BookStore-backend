import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional
from app import db


class Discount(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    book_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey("book.id", ondelete="CASCADE"), nullable=True)
    percentage: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(5, 2))  # e.g., 10.00 for 10% off
    fixed_amount: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))  # e.g., $5 off
    start_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date, nullable=True)
    end_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date, nullable=True)

    # Relationship to Book
    book: so.Mapped["Book"] = so.relationship("Book", back_populates="discounts")

    def __repr__(self) -> str:
        return f"<Discount(id={self.id}, book_id={self.book_id}, percentage={self.percentage}, fixed_amount={self.fixed_amount})>"
