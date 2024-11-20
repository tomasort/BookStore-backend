from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

# Define many-to-many relationship tables using Typed ORM style
book_genres = sa.Table(
    "book_genres",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey(
        "book.id"), primary_key=True),
    sa.Column("genre_id", sa.Integer, sa.ForeignKey(
        "genre.id"), primary_key=True),
)

book_languages = sa.Table(
    "book_languages",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey(
        "book.id"), primary_key=True),
    sa.Column(
        "language_id", sa.Integer,
        sa.ForeignKey("language.id"), primary_key=True
    ),
)

book_series = sa.Table(
    "book_series",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey(
        "book.id"), primary_key=True),
    sa.Column("series_id", sa.Integer, sa.ForeignKey(
        "series.id"), primary_key=True),
)

book_authors = sa.Table(
    "book_authors",
    db.metadata,
    sa.Column("book_id", sa.Integer, sa.ForeignKey(
        "book.id"), primary_key=True),
    sa.Column("author_id", sa.Integer, sa.ForeignKey(
        "author.id"), primary_key=True),
)


class Author(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    birth_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    death_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    biography: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    # Define the relationship with books
    books: so.WriteOnlyMapped[list["Book"]] = so.relationship(
        "Book", secondary=book_authors, back_populates="authors"
    )

    def __repr__(self) -> str:
        return f"<Author(id={self.id}, name='{self.name}', birth_date='{self.birth_date}')>"


class Book(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    isbn_10: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String, unique=True, index=True
    )
    isbn_13: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String, unique=True, index=True
    )
    publish_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    cover_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    current_price: so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
    previous_price: so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
    physical_format: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    number_of_pages: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    editorial: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    alejandria_isbn: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String, unique=True, index=True
    )
    publisher_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.Integer, sa.ForeignKey("publisher.id")
    )
    physical_dimensions: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    weight: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    publish_place: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    edition_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    subtitle: so.Mapped[Optional[str]] = so.mapped_column(sa.String)

    # Define the relationships
    authors: so.WriteOnlyMapped[list["Author"]] = so.relationship(
        "Author", secondary=book_authors,
        back_populates="books", passive_deletes=True
    )
    genres: so.WriteOnlyMapped[list["Genre"]] = so.relationship(
        "Genre", secondary=book_genres,
        back_populates="books", passive_deletes=True
    )
    publisher: so.Mapped[Optional["Publisher"]] = so.relationship(
        "Publisher", back_populates="books",
        passive_deletes=True
    )
    languages: so.WriteOnlyMapped[list["Language"]] = so.relationship(
        "Language", secondary=book_languages,
        back_populates="books", passive_deletes=True
    )
    series: so.WriteOnlyMapped[list["Series"]] = so.relationship(
        "Series", secondary=book_series,
        back_populates="books", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}', publish_date='{self.publish_date}')>"


class Genre(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.WriteOnlyMapped[list["Book"]] = so.relationship(
        "Book", secondary=book_genres, back_populates="genres"
    )

    def __repr__(self) -> str:
        return f"<Genre(id={self.id}, name='{self.name}')>"


class Publisher(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.WriteOnlyMapped['Book'] = so.relationship(
        "Book", back_populates="publisher"
    )

    def __repr__(self) -> str:
        return f"<Publisher(id={self.id}, name='{self.name}')>"


class Language(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.WriteOnlyMapped[list["Book"]] = so.relationship(
        "Book", secondary=book_languages, back_populates="languages"
    )

    def __repr__(self) -> str:
        return f"<Language(id={self.id}, name='{self.name}')>"


class Series(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.WriteOnlyMapped[list["Book"]] = so.relationship(
        "Book", secondary=book_series, back_populates="series"
    )

    def __repr__(self) -> str:
        return f"<Series(id={self.id}, name='{self.name}')>"
