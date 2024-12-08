import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class ExchangeRate(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    rate: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)  # Exchange rate USD -> VES
    updated_at: so.Mapped[sa.DateTime] = so.mapped_column(
        sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ExchangeRate(id={self.id}, rate={self.rate}, updated_at={self.updated_at})>"
