from pprint import pprint
import pdb
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


def test_create_simple_book(client, book_factory):
    """ Test creating a simple book without authors """
    book = book_factory.build(authors=[])
    book_schema = BookSchema(exclude=["id", "authors", "cover_url"])
    # Send a POST request to create a new book
    response = client.post(
        url_for("api.books.create_book"),
        data=json.dumps(book_schema.dump(book)),
        content_type="application/json"
    )
    # Assert that the request was successful
    assert response.status_code == 201
    response_data = response.get_json()
    assert "book_id" in response_data
    # Verify that the book was created
    assert db.session.execute(select(Book).where(Book.id == response_data["book_id"])).scalar() is not None


@pytest.mark.parametrize("num_books, limit, page", [(10, 5, 1), (10, 5, 2), (15, 5, 3)])
def test_get_books_pagination(client, book_factory, num_books, limit, page):
    """ Test retrieving books with pagination """
    book_factory.create_batch(num_books)
    response = client.get(url_for('api.books.get_books', limit=limit, page=page))
    assert response.status_code == 200
    data = response.get_json()
    assert 'books' in data
    assert 'pagination' in data
    assert 'pages' in data['pagination']
    num_books_in_db = db.session.execute(select(func.count()).select_from(Book)).scalar()
    assert data["pagination"]["pages"] == (num_books_in_db // limit) + (num_books_in_db % limit > 0)
    assert isinstance(data["books"], list)
    assert len(data["books"]) == min(limit, num_books_in_db - (page - 1) * limit)  # Ensure pagination works as expected

# TODO: create tests for pagination with invalid page and limit values


@ pytest.mark.parametrize("num_books", [1, 3])
def test_get_specific_book(client, book_factory, num_books):
    books = book_factory.create_batch(num_books)
    test_book = choice(books)
    response = client.get(url_for('api.books.get_book', book_id=test_book.id))
    assert response.status_code == 200
    returned_book = response.get_json()
    assert returned_book["id"] == test_book.id
    assert returned_book["title"] == test_book.title


# TODO: create tests for books with wrong data

@ pytest.mark.parametrize("num_books", [1, 2])
def test_update_book(client, book_factory, num_books):
    fake = Faker()
    books = book_factory.create_batch(num_books)
    update_data = {
        "title": fake.sentence(),
        "isbn_10": fake.isbn10(separator=""),
        "isbn_13": fake.isbn13(separator=""),
        "subtitle": fake.sentence(),
        "other_isbns": [fake.isbn10(separator="") for _ in range(3)],
        "publish_date": fake.date_this_century().isoformat(),
        "description": fake.paragraph(),
        "current_price": fake.random_number(2),
        "iva": fake.random_number(2),
        "cost": fake.random_number(2),
    }
    book = choice(books)
    update_response = client.put(
        url_for("api.books.update_book", book_id=book.id),
        data=json.dumps(update_data),
        content_type="application/json",
    )
    # Assert that the update was successful
    assert update_response.status_code == 200
    # Verify that the book was updated
    updated_book = db.session.execute(select(Book).where(Book.id == book.id)).scalar()
    assert updated_book is not None
    for key, value in update_data.items():
        if 'date' in key:  # Special case for publish_date
            assert str(getattr(updated_book, key)) == value
        else:
            assert getattr(updated_book, key) == value


@ pytest.mark.parametrize("num_books", [1, 3])
def test_delete_book(client, book_factory, num_books):
    books = book_factory.create_batch(num_books)
    book_to_delete = choice(books)
    delete_response = client.delete(url_for("api.books.delete_book", book_id=book_to_delete.id))
    assert delete_response.status_code == 200
    deleted_book = db.session.execute(select(Book).where(Book.id == book_to_delete.id)).scalar()
    assert deleted_book is None
    remaining_book_ids = {book.id for book in books if book != book_to_delete}
    db_book_ids = {id for id in db.session.execute(select(Book.id)).scalars()}
    assert remaining_book_ids.issubset(db_book_ids)


@ pytest.mark.parametrize("num_books", [1, 5])
def test_search_books_by_title(client, book_factory, num_books):
    books = book_factory.create_batch(num_books)
    searched_book = choice(books)
    search_response = client.get(url_for("api.books.search_books", title=searched_book.title))
    assert search_response.status_code == 200
    data = search_response.get_json()
    assert 'books' in data
    response_books = data['books']
    assert isinstance(response_books, list)
    assert len(response_books) > 0
    assert all(searched_book.title in book["title"] for book in response_books)


# TODO: test for search by isbn when isbn doesn't exist
@ pytest.mark.parametrize("num_books", [1, 5])
def test_search_books_by_isbn(client, book_factory, num_books):
    books = book_factory.create_batch(num_books)
    searched_book = choice(books)
    search_response = client.get(url_for("api.books.search_books", isbn=searched_book.isbn_13))
    assert search_response.status_code == 200
    data = search_response.get_json()
    assert 'books' in data
    response_books = data['books']
    assert isinstance(response_books, list)
    assert len(response_books) > 0
    assert all((book["isbn_10"] == searched_book.isbn_10 or book["isbn_13"] == searched_book.isbn_13) for book in response_books)


def test_search_books_author(client, book_factory, author_factory):
    # Create a batch of books
    book_factory.create_batch(5)
    book_with_author = book_factory.create()
    author = author_factory.create(name="The Great Author")
    book_with_author.authors.append(author)
    search_response = client.get(url_for("api.books.search_books", author="great"))
    assert search_response.status_code == 200
    data = search_response.get_json()
    assert 'books' in data
    response_books = data['books']
    assert isinstance(response_books, list)
    book_ids = {book["id"] for book in response_books}
    assert book_with_author.id in book_ids


def test_search_books_query(client, book_factory, author_factory):
    # Create a batch of books
    book_factory.create_batch(5)
    # book_with_title = book_factory.create(title="The Great Gatsby")
    book_with_description = book_factory.create(description="A tale of great love and loss")
    # book_with_author = book_factory.create()
    # author = author_factory.create(name="The Great Author")
    # book_with_author.authors.append(author)
    search_response = client.get(url_for("api.books.search_books", q="tale"))
    assert search_response.status_code == 200
    # Verify the search results are both books
    data = search_response.get_json()
    pprint(data)
    assert 'books' in data
    response_books = data['books']
    assert isinstance(response_books, list)
    book_ids = {book["id"] for book in response_books}
    # assert book_with_title.id in book_ids
    assert book_with_description.id in book_ids
    # assert book_with_author.id in book_ids


@ pytest.mark.parametrize("num_books", [1, 5])
def test_search_books_no_results(client, book_factory, num_books):
    book_factory.create_batch(num_books)
    # Search for a non-existing book
    search_response = client.get(url_for("api.books.search_books", title="NonExistentTitleOrUnlikelyToExist"))
    assert search_response.status_code == 404
    # Verify the response contains an appropriate message
    data = search_response.get_json()
    assert "message" in data
    assert data["message"] == "No books found matching the search criteria"


@ pytest.mark.parametrize("num_genres", [1, 2])
def test_add_genre_to_book(client, book_factory, genre_factory, num_genres):
    book = book_factory.create()
    book.genres = []  # TODO: create another test for books with existing genres
    genres = genre_factory.create_batch(num_genres)
    # Add genres to the book
    update_book_response = client.put(
        f"/api/books/{book.id}/genres",
        data=json.dumps({"genre_ids": [genre.id for genre in genres]}),
        content_type="application/json",
    )
    assert update_book_response.status_code == 200
    for genre in genres:
        assert genre in book.genres
    updated_book = db.session.execute(select(Book).where(Book.id == book.id)).scalar()
    assert updated_book is not None
    assert len(updated_book.genres) == num_genres


@ pytest.mark.parametrize("num_genres", [1, 2])
def test_remove_genre_from_book(client, book_factory, genre_factory, num_genres):
    book = book_factory.create()
    book.genres = genre_factory.create_batch(num_genres)
    genre_to_remove = choice(book.genres)
    assert genre_to_remove in book.genres
    # Remove the genre from the book
    remove_genre_response = client.delete(
        url_for("api.books.remove_genre_from_book", book_id=book.id, genre_id=genre_to_remove.id),
        content_type="application/json",
    )
    assert remove_genre_response.status_code == 200
    updated_book = db.session.execute(select(Book).where(Book.id == book.id)).scalar()
    assert updated_book is not None
    assert genre_to_remove not in book.genres
    assert len(book.genres) == num_genres - 1


@ pytest.mark.parametrize("num_series", [1, 2])
def test_add_series_to_book(client, book_factory, series_factory, num_series):
    series = series_factory.create_batch(num_series)
    book = book_factory.create()
    book.series = []
    update_book_response = client.put(
        url_for("api.books.add_series_to_book", book_id=book.id),
        data=json.dumps({"series_id": [s.id for s in series]}),
        content_type="application/json",
    )
    assert update_book_response.status_code == 200
    assert len(book.series) == num_series


@ pytest.mark.parametrize("num_series", [1, 2])
def test_remove_series_from_book(client, book_factory, series_factory, num_series):
    book = book_factory.create()
    book.series = series_factory.create_batch(num_series)
    series_to_remove = choice(book.series)
    assert len(book.series) == num_series
    assert series_to_remove in book.series
    # Remove the series from the book
    remove_series_response = client.delete(
        url_for("api.books.remove_series_from_book", book_id=book.id, series_id=series_to_remove.id),
        content_type="application/json",
    )
    assert remove_series_response.status_code == 200
    assert series_to_remove not in book.series
    assert len(book.series) == num_series - 1


# def test_get_popular_books(client, book_factory, ):
#     book = book_factory.create()
#     assert False
