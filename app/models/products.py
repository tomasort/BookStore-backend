from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from typing import Optional, List
from sqlalchemy.ext.mutable import MutableList
from app.models.reviews import Review

product_discounts = sa.Table(
    "product_discounts",
    db.metadata,
    sa.Column("product_id", sa.Integer, sa.ForeignKey("product.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("discount_id", sa.Integer, sa.ForeignKey("discount.id", ondelete="CASCADE"), primary_key=True),
)


class Product(db.Model):
    __tablename__ = "product"
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    type: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)  # Discriminator column
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    price: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    iva: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    cost: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    cost_supplier: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    stock: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    rating: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(4, 2), default=0)
    discounts: so.Mapped[List["Discount"]] = so.relationship(
        "Discount",
        secondary=product_discounts,
        back_populates="products",
    )

    __mapper_args__ = {
        "polymorphic_identity": "product",
        "polymorphic_on": type,
    }

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, type='{self.type}', name='{self.name}')>"
