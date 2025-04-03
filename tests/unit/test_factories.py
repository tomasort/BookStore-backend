from pprint import pprint
import json
import pytest
from app import db
from app.models import Book
from app.schemas import BookSchema
from sqlalchemy import select, func
from urllib.parse import quote
from flask import url_for


@pytest.mark.parametrize('num_books', [5, 10, 20, 30])
def test_get_related_books(client, book_factory, author_factory, genre_factory, num_books):
    """ Test retrieving related books """
    book_factory.create_batch(num_books)
    genres = genre_factory.create_batch(num_books)
    authors = author_factory.create_batch(num_books)
    books = book_factory.create_batch(num_books, genres=genres, authors=authors)
    books_with_authors = book_factory.create_batch(num_books, authors=authors)
