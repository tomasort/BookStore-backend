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


def test_suggest_books(client, book_factory):
    """ Test suggesting books from a query """
    books = book_factory.create_batch(2)
    target_book = choice(books)
    target_book.title = " ".join(Faker().words(nb=5))
    query = target_book.title.split()[0]
    response = client.get(url_for('api.books.suggestions', q=quote(query)))
    assert response.status_code == 200
    data = response.get_json()
    assert 'books' in data
    assert isinstance(data['books'], list)
    assert len(data['books']) == 1
    assert 'authors' in data
