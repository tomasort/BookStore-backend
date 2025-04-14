import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional, List
from app import db
from app.models.products import product_discounts


class DiscountCode(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    code: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True, nullable=False)
    discount_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("discount.id"), nullable=False
    )
    discount: so.Mapped["Discount"] = so.relationship(
        "Discount", back_populates="discount_codes"
    )

    def __repr__(self) -> str:
        return f"<DiscountCode(id={self.id}, code={self.code}, discount_id={self.discount_id})>"


class Discount(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    percentage: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(5, 2))  # e.g., 10.00 for 10% off
    fixed_amount: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))  # e.g., $5 off
    start_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date, nullable=True)
    end_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date, nullable=True)
    products: so.Mapped[List["Product"]] = so.relationship(
        "Product",
        secondary=product_discounts,
        back_populates="discounts",
    )
    discount_codes: so.Mapped[List["DiscountCode"]] = so.relationship(
        "DiscountCode", back_populates="discount"
    )

    def __repr__(self) -> str:
        return f"<Discount(id={self.id}, book_id={self.book_id}, percentage={self.percentage}, fixed_amount={self.fixed_amount})>"
