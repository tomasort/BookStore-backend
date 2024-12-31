from typing import Optional
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableList
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

# Define many-to-many relationship tables using Typed ORM style
book_genres = sa.Table(
    "book_genres",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id"), primary_key=True),
    sa.Column("genre_id", sa.Integer, sa.ForeignKey("genre.id"), primary_key=True),
)

book_languages = sa.Table(
    "book_languages",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id"), primary_key=True),
    sa.Column("language_id", sa.Integer, sa.ForeignKey("language.id"), primary_key=True),
)

book_series = sa.Table(
    "book_series",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id"), primary_key=True),
    sa.Column("series_id", sa.Integer, sa.ForeignKey("series.id"), primary_key=True),
)

book_publishers = sa.Table(
    "book_publishers",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id"), primary_key=True),
    sa.Column("publisher_id", sa.Integer, sa.ForeignKey("publisher.id"), primary_key=True),
)

book_providers = sa.Table(
    "book_providers",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id"), primary_key=True),
    sa.Column("provider_id", sa.Integer, sa.ForeignKey("provider.id"), primary_key=True),
)

book_authors = sa.Table(
    "book_authors",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id"), primary_key=True),
    sa.Column("author_id", sa.Integer, sa.ForeignKey("author.id"), primary_key=True),
)


class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self):
        dict_ = {}
        for column in self.__table__.c:
            if "date" in column.name:
                dict_[column.name] = str(getattr(self, column.name))
            else:
                dict_[column.name] = getattr(self, column.name)
        return dict_


class Author(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    birth_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    birth_date_str: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    death_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    death_date_str: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    biography: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    other_names: so.Mapped[Optional[list[str]]] = so.mapped_column(MutableList.as_mutable(sa.JSON))
    photo_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    open_library_id: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    casa_del_libro_id: so.Mapped[Optional[str]] = so.mapped_column(sa.String)

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship(
        "Book", secondary=book_authors, back_populates="authors"
    )

    def __repr__(self) -> str:
        return f"<Author(id={self.id}, name='{self.name}', birth_date='{self.birth_date}', death_date='{self.death_date}')>"


class Book(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    isbn_10: so.Mapped[Optional[str]] = so.mapped_column(sa.String, unique=True, index=True)
    isbn_13: so.Mapped[Optional[str]] = so.mapped_column(sa.String, unique=True, index=True)
    publish_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    cover_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    current_price: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    previous_price: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    price_alejandria: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    iva: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    cost: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    cost_supplier: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    average_cost_alejandria: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    last_cost_alejandria: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    stock: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    stock_alejandria: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    stock_consig: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    stock_consig_alejandria: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    physical_format: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    number_of_pages: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    bar_code_alejandria: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    isbn_alejandria: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    code_alejandria: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    physical_dimensions: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    weight: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    publish_places: so.Mapped[Optional[list[str]]] = so.mapped_column(MutableList.as_mutable(sa.JSON))
    edition_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    subtitle: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    discounts: so.Mapped[Optional[list["Discount"]]] = so.relationship("Discount", back_populates="book")

    # Define the relationships
    providers: so.Mapped[list["Provider"]] = so.relationship(
        "Provider", secondary=book_providers, back_populates="books", passive_deletes=True
    )
    publishers: so.Mapped[list["Publisher"]] = so.relationship(
        "Publisher", secondary=book_publishers, back_populates="books", passive_deletes=True
    )
    authors: so.Mapped[list["Author"]] = so.relationship(
        "Author", secondary=book_authors, back_populates="books", passive_deletes=True
    )
    genres: so.Mapped[list["Genre"]] = so.relationship(
        "Genre", secondary=book_genres, back_populates="books", passive_deletes=True
    )
    languages: so.Mapped[list["Language"]] = so.relationship(
        "Language", secondary=book_languages, back_populates="books", passive_deletes=True
    )
    series: so.Mapped[list["Series"]] = so.relationship(
        "Series", secondary=book_series, back_populates="books", passive_deletes=True
    )
    reviews: so.Mapped[list["Review"]] = so.relationship("Review", back_populates="book")

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}', isbn10='{self.isbn_10}', isbn13='{self.isbn_13}')>"


class Genre(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship("Book", secondary=book_genres, back_populates="genres")

    def __repr__(self) -> str:
        return f"<Genre(id={self.id}, name='{self.name}')>"


class Publisher(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped['Book'] = so.relationship("Book", secondary=book_publishers, back_populates="publishers")

    def __repr__(self) -> str:
        return f"<Publisher(id={self.id}, name='{self.name}')>"


class Language(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship("Book", secondary=book_languages, back_populates="languages")

    def __repr__(self) -> str:
        return f"<Language(id={self.id}, name='{self.name}')>"


class Series(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship("Book", secondary=book_series, back_populates="series")

    def __repr__(self) -> str:
        return f"<Series(id={self.id}, name='{self.name}')>"


class Provider(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    alejandria_code: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    cedula: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    url: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    address: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    phone: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    email: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    contact_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    nombre_banco: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    titular_banco: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    rif_banco: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    cod_cuenta: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    books: so.Mapped[list["Book"]] = so.relationship(
        "Book", secondary=book_providers, back_populates="providers"
    )

    def __repr__(self) -> str:
        return f"<Provider(id={self.id}, name='{self.name}')>"


class FeaturedBook(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    book_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("book.id", ondelete="CASCADE"), nullable=False)
    featured_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date, default=sa.func.current_date())
    expiry_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date, nullable=True)
    priority: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True, default=0)  # Lower number = higher priority

    # Relationship to the Book table
    book: so.Mapped["Book"] = so.relationship("Book")

    def __repr__(self) -> str:
        return f"<FeaturedBook(id={self.id}, book_id={self.book_id}, priority={self.priority})>"


class Discount(BaseModel):
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


class Review(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    book_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('book.id'))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'))
    rating: so.Mapped[int] = so.mapped_column(sa.Integer)  # 1-5 stars
    comment: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    # Relationships
    book: so.Mapped["Book"] = so.relationship("Book", back_populates="reviews")
    user: so.Mapped["User"] = so.relationship("User", back_populates="reviews")

    def __repr__(self):
        return f'<Review {self.id}>'
