from marshmallow import EXCLUDE
from pprint import pprint
import json
from faker import Faker
from random import choice
import pytest
from app import db
from app.models import Book
from app.schemas import BookSchema
from sqlalchemy import select, func
from urllib.parse import quote
from flask import url_for


def test_get_related_books(book_factory, client):
    """ Test retrieving related books """
    initial_book = book_factory.create()
    genres = initial_book.genres
    authors = initial_book.authors
    related_books_by_author = book_factory.create_batch(3, authors=authors)
    related_books_by_genre = book_factory.create_batch(3, genres=genres)
    books = set(related_books_by_author + related_books_by_genre)
    response = client.get(url_for('api.books.get_related_books', book_id=initial_book.id))
    assert response.status_code == 200
    data = response.get_json()
    assert 'books' in data
    response_books = data['books']
    assert isinstance(response_books, list)
    assert len(response_books) >= len(books)
    response_books_ids = [book['id'] for book in response_books]
    assert all([book.id in response_books_ids for book in books])
