from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from typing import Optional, List
from sqlalchemy.ext.mutable import MutableList
from app.models.reviews import Review
from app.models.products import Product

# Define many-to-many relationship tables using Typed ORM style
book_genres = sa.Table(
    "book_genres",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("genre_id", sa.Integer, sa.ForeignKey("genre.id", ondelete="CASCADE"), primary_key=True),
)

book_languages = sa.Table(
    "book_languages",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("language_id", sa.Integer, sa.ForeignKey("language.id", ondelete="CASCADE"), primary_key=True),
)

book_series = sa.Table(
    "book_series",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("series_id", sa.Integer, sa.ForeignKey("series.id", ondelete="CASCADE"), primary_key=True),
)

book_publishers = sa.Table(
    "book_publishers",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("publisher_id", sa.Integer, sa.ForeignKey("publisher.id", ondelete="CASCADE"), primary_key=True),
)

book_providers = sa.Table(
    "book_providers",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("provider_id", sa.Integer, sa.ForeignKey("provider.id", ondelete="CASCADE"), primary_key=True),
)

book_authors = sa.Table(
    "book_authors",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("author_id", sa.Integer, sa.ForeignKey("author.id", ondelete="CASCADE"), primary_key=True),
)


class Author(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    birth_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    birth_date_str: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    death_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    death_date_str: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    biography: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    other_names: so.Mapped[Optional[List[str]]] = so.mapped_column(MutableList.as_mutable(sa.JSON))
    open_library_id: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    casa_del_libro_id: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    photos: so.Mapped[list["AuthorPhoto"]] = so.relationship("AuthorPhoto", back_populates="author", cascade="all, delete-orphan")

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship(
        "Book", secondary=book_authors, back_populates="authors"
    )

    def __repr__(self) -> str:
        return f"<Author(id={self.id}, name='{self.name}', birth_date='{self.birth_date}', death_date='{self.death_date}')>"

    @property
    def photo_url(self) -> Optional[str]:
        """Returns the URL of the primary photo for backward compatibility."""
        for photo in self.photos:
            if photo.is_primary:
                return photo.url
        return self.photos[0].url if self.photos else None


class AuthorPhoto(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    author_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("author.id", ondelete="CASCADE"), nullable=False)
    url: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    is_primary: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    size: so.Mapped[Optional[str]] = so.mapped_column(sa.String)  # e.g., "small", "medium", "large"
    created_at: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now())

    author: so.Mapped["Author"] = so.relationship("Author", back_populates="photos")

    def __repr__(self) -> str:
        return f"<AuthorPhoto(url={self.url}, is_primary={self.is_primary})>"


class Book(Product):
    id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("product.id"), primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    subtitle: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    isbn_10: so.Mapped[Optional[str]] = so.mapped_column(sa.String, unique=True, index=True)
    isbn_13: so.Mapped[Optional[str]] = so.mapped_column(sa.String, unique=True, index=True)
    other_isbns: so.Mapped[Optional[List[str]]] = so.mapped_column(MutableList.as_mutable(sa.JSON))
    publish_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    # description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    current_price: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    previous_price: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    price_alejandria: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    average_cost_alejandria: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    last_cost_alejandria: so.Mapped[Optional[float]] = so.mapped_column(sa.Numeric(10, 2))
    # stock: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
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

    # Add the new relationship to the Cover model
    covers: so.Mapped[list["Cover"]] = so.relationship("Cover", back_populates="book", cascade="all, delete-orphan")

    __mapper_args__ = {
        "polymorphic_identity": "book",
    }

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}', isbn10='{self.isbn_10}', isbn13='{self.isbn_13}')>"

    # Helper property to easily get the primary cover
    @property
    def primary_cover(self) -> Optional["Cover"]:
        """Returns the primary cover for the book, or the first cover if no primary is set."""
        for cover in self.covers:
            if cover.is_primary:
                return cover
        return self.covers[0] if self.covers else None

    @property
    def cover_url(self) -> Optional[str]:
        """Returns the URL of the primary cover for backward compatibility."""
        cover = self.primary_cover
        return cover.url if cover else None

    @property
    def price(self):
        """
        Gets the current price of the book.
        """
        return self.current_price

    @price.setter
    def price(self, new_price: float):
        """
        Sets the current price of the book while keeping a record of the previous price.

        Args:
            new_price (float): The new price to set for the book.
        """
        if self.current_price != new_price:
            self.previous_price = self.current_price
            self.current_price = new_price

    @hybrid_property
    def average_rating(self):
        """Calculate the average rating for the book at the Python level."""
        if not self.reviews:
            return 0.0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

    @average_rating.expression
    def average_rating(cls):
        """Calculate the average rating for the book at the SQL level."""
        return (
            db.session.query(func.avg(Review.rating))
            .filter(Review.book_id == cls.id)
            .correlate(cls)
            .as_scalar()
        )


class Cover(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    book_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("book.id", ondelete="CASCADE"), nullable=False)
    url: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    is_primary: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    cover_type: so.Mapped[Optional[str]] = so.mapped_column(sa.String)  # e.g., "front", "back", "spine"
    size: so.Mapped[Optional[str]] = so.mapped_column(sa.String)  # e.g., "small", "medium", "large"
    created_at: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now())

    # Define the relationship back to the Book model
    book: so.Mapped["Book"] = so.relationship("Book", back_populates="covers")

    def __repr__(self) -> str:
        return f"<Cover(id={self.id}, book_id={self.book_id}, is_primary={self.is_primary}, url={self.url})>"


class Genre(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship("Book", secondary=book_genres, back_populates="genres")

    def __repr__(self) -> str:
        return f"<Genre(id={self.id}, name='{self.name}')>"


class Publisher(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped['Book'] = so.relationship("Book", secondary=book_publishers, back_populates="publishers")

    def __repr__(self) -> str:
        return f"<Publisher(id={self.id}, name='{self.name}')>"


class Language(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship("Book", secondary=book_languages, back_populates="languages")

    def __repr__(self) -> str:
        return f"<Language(id={self.id}, name='{self.name}')>"


class Series(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship("Book", secondary=book_series, back_populates="series")

    def __repr__(self) -> str:
        return f"<Series(id={self.id}, name='{self.name}')>"


class Provider(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
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


class FeaturedBook(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    book_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("book.id", ondelete="CASCADE"), nullable=False)
    expiry_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date, nullable=True)

    # Relationship to the Book table
    book: so.Mapped["Book"] = so.relationship("Book")

    # Default arguments
    priority: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True, default=0)  # Lower number = higher priority
    featured_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date, default=sa.func.current_date())

    def __repr__(self) -> str:
        return f"<FeaturedBook(id={self.id}, book_id={self.book_id}, priority={self.priority})>"
