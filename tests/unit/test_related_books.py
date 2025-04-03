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


@pytest.mark.parametrize('num_related_books', [5, 10, 20, 30])
def test_get_related_books(book_factory, author_factory, genre_factory, client, num_related_books):
    """ Test retrieving related books """
    genres = genre_factory.create_batch(5)
    assert (len(set(genres)) == 5)
    authors = author_factory.create_batch(5)
    initial_book = book_factory.create(genres=genres, authors=authors)
    assert all([genre in initial_book.genres for genre in genres])
    assert all([author in initial_book.authors for author in authors])
    related_books_by_author = book_factory.create_batch(num_related_books, authors=authors)
    related_books_by_genre = book_factory.create_batch(num_related_books, genres=genres)
    books = set(related_books_by_author + related_books_by_genre)
    response = client.get(url_for('api.books.get_related_books', book_id=initial_book.id, per_page=len(books)))
    assert response.status_code == 200
    data = response.get_json()
    assert 'books' in data
    assert 'pagination' in data
    response_books = data['books']
    assert isinstance(response_books, list)
    assert len(response_books) >= len(books)
    # make  sure that the response books containe either the authors or genres of the initial book
    for book in response_books:
        assert book['id'] != initial_book.id
        book_authors_ids = [author['id'] for author in book['authors']]
        book_genres_ids = [genre['id'] for genre in book['genres']]
        has_author = any(author in book_authors_ids for author in [author.id for author in authors])
        has_genre = any(genre in book_genres_ids for genre in [genre.id for genre in genres])
        if not has_author and not has_genre:
            # if the book is not related to the initial book, it should be excluded from the response
            print(genres)
            print(authors)
            print(f"Book {book['id']} is not related to the initial book")
            pprint(book)
        assert has_author or has_genre
