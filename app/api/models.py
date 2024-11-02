from sqlalchemy import Column, String, Integer, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app import db

class Author(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    birth_date = Column(Date)
    biography = Column(Text)

    # Define the relationship with books
    books = relationship('Book', back_populates='author')

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}', birth_date='{self.birth_date}')>"

class Book(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    isbn = Column(String)
    publication_date = Column(Date)
    genre = Column(String)
    description = Column(Text)
    author_id = Column(Integer, ForeignKey('authors.id'))
    cover_url = Column(String)

    # Define the relationship with authors
    author = relationship('Author', back_populates='books')

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', publication_date='{self.publication_date}')>"

