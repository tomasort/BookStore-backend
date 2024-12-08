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
        "language_id", sa.Integer, sa.ForeignKey("language.id"), primary_key=True
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
    death_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    biography: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    # Use PickleType for other_names to store a list or other Python objects
    other_names: so.Mapped[Optional[list[str]]] = so.mapped_column(sa.PickleType)
    photo_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String)

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship(
        "Book", secondary=book_authors, back_populates="authors"
    )

    def __repr__(self) -> str:
        return f"<Author(id={self.id}, name='{self.name}', birth_date='{self.birth_date}')>"


class Book(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    isbn_10: so.Mapped[Optional[str]] = so.mapped_column(sa.String, unique=True, index=True)
    isbn_13: so.Mapped[Optional[str]] = so.mapped_column(sa.String, unique=True, index=True)
    publish_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    cover_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    current_price: so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
    previous_price: so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
    cost: so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
    cost_supplier: so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
    physical_format: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    number_of_pages: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    alejandria_isbn: so.Mapped[Optional[str]] = so.mapped_column(sa.String, unique=True, index=True)
    physical_dimensions: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    weight: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    publish_place: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    edition_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    subtitle: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    provider_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, sa.ForeignKey("provider.id"))
    provider: so.Mapped[Optional["Provider"]] = so.relationship(
        "Provider", back_populates="books", passive_deletes=True
    )

    # Define the relationships
    authors: so.Mapped[list["Author"]] = so.relationship(
        "Author", secondary=book_authors, back_populates="books", passive_deletes=True
    )
    genres: so.Mapped[list["Genre"]] = so.relationship(
        "Genre", secondary=book_genres, back_populates="books", passive_deletes=True
    )
    publisher_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, sa.ForeignKey("publisher.id"))
    publisher: so.Mapped[Optional["Publisher"]] = so.relationship(
        "Publisher", back_populates="books", passive_deletes=True
    )
    languages: so.Mapped[list["Language"]] = so.relationship(
        "Language", secondary=book_languages, back_populates="books", passive_deletes=True
    )
    series: so.Mapped[list["Series"]] = so.relationship(
        "Series", secondary=book_series, back_populates="books", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}', publish_date='{self.publish_date}')>"


class Genre(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship(
        "Book", secondary=book_genres, back_populates="genres"
    )

    def __repr__(self) -> str:
        return f"<Genre(id={self.id}, name='{self.name}')>"


class Publisher(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped['Book'] = so.relationship(
        "Book", back_populates="publisher"
    )

    def __repr__(self) -> str:
        return f"<Publisher(id={self.id}, name='{self.name}')>"


class Language(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship(
        "Book", secondary=book_languages, back_populates="languages"
    )

    def __repr__(self) -> str:
        return f"<Language(id={self.id}, name='{self.name}')>"


class Series(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)

    # Define the relationship with books
    books: so.Mapped[list["Book"]] = so.relationship(
        "Book", secondary=book_series, back_populates="series"
    )

    def __repr__(self) -> str:
        return f"<Series(id={self.id}, name='{self.name}')>"


class Provider(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    alejandria_code: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    cedula = so.mapped_column(sa.String, nullable=False)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    url: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    address: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    phone: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    contact_name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    banco: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    titular_banco: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    rif_banco: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    cod_cuenta: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    notes: so.Mapped[str] = so.mapped_column(sa.Text)
    books: so.Mapped[list["Book"]] = so.relationship(
        "Book", back_populates="provider"
    )

    def __repr__(self) -> str:
        return f"<Provider(id={self.id}, name='{self.name}', url='{self.url}')>"
