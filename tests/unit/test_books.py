import json
from faker import Faker
from random import choice
import pytest
from app import db
from app.models import Book
from app.schemas import BookSchema
from sqlalchemy import select, func
from urllib.parse import quote


def test_create_simple_book(client, book_factory):
    book = book_factory.build(authors=[])
    book_schema = BookSchema(exclude=["id", "authors"])
    # Send a POST request to create a new book
    response = client.post(
        "/api/books",
        data=json.dumps(book_schema.dump(book)),
        content_type="application/json"
    )
    # Assert that the request was successful
    assert response.status_code == 201
    response_data = response.get_json()
    assert "book_id" in response_data
    # Verify that the book was created
    assert db.session.execute(select(Book).where(
        Book.id == response_data["book_id"])).scalar() is not None


@pytest.mark.parametrize("num_books, limit, page", [(20, 5, 1), (20, 5, 2), (10, 10, 1), (10, 5, 3)])
def test_get_books_pagination(client, book_factory, num_books, limit, page, cleanup_db):
    # Create a batch of books
    book_factory.create_batch(num_books)
    print(db.session.execute(select(func.count(Book.id))).scalar())
    # Send a GET request with pagination parameters
    response = client.get(f"/api/books?limit={limit}&page={page}")
    assert response.status_code == 200
    data = response.get_json()
    assert "books" in data
    pagination = data["pagination"]
    assert pagination["pages"] == (num_books // limit) + (num_books % limit > 0)
    assert isinstance(data["books"], list)
    assert len(data["books"]) == min(limit, num_books - (page - 1) * limit)  # Ensure pagination works as expected


@pytest.mark.parametrize("num_books", [1, 10, 20])
def test_get_specific_book(client, book_factory, num_books):
    books = book_factory.create_batch(num_books)
    # Send a GET request to retrieve the specific book
    test_book = choice(books)
    response = client.get(f"/api/books/{test_book.id}")
    assert response.status_code == 200
    returned_book = response.get_json()
    assert returned_book["id"] == test_book.id
    assert returned_book["title"] == test_book.title


@pytest.mark.parametrize("num_books", [1, 10, 20])
def test_update_book(client, book_factory, num_books):
    fake = Faker()
    # Create a book to update
    books = book_factory.create_batch(num_books)
    # Update the book's title
    update_data = {"title": fake.sentence(), "isbn_10": fake.isbn10()}
    book = choice(books)
    update_response = client.put(
        f"/api/books/{book.id}",
        data=json.dumps(update_data),
        content_type="application/json",
    )
    # Assert that the update was successful
    assert update_response.status_code == 200
    # Verify that the book was updated
    updated_book = db.session.execute(select(Book).where(Book.id == book.id)).scalar()
    if updated_book is None:
        assert False
    assert updated_book.title == update_data["title"]
    assert updated_book.isbn_10 == update_data["isbn_10"]


@pytest.mark.parametrize("num_books", [1, 10, 20])
def test_delete_book(client, book_factory, num_books):
    # Create a batch of books
    books = book_factory.create_batch(num_books)
    book_to_delete = choice(books)
    delete_response = client.delete(f"/api/books/{book_to_delete.id}")
    assert delete_response.status_code == 200
    deleted_book = db.session.execute(select(Book).where(Book.id == book_to_delete.id)).scalar()
    assert deleted_book is None
    remaining_book_ids = {book.id for book in books if book != book_to_delete}
    db_book_ids = {id for id in db.session.execute(select(Book.id)).scalars()}
    assert remaining_book_ids.issubset(db_book_ids)


@pytest.mark.parametrize("num_books", [1, 10, 20])
def test_search_books_by_title_single_result(client, book_factory, num_books):
    books = book_factory.create_batch(num_books)
    # Search by title
    searched_book = choice(books)
    search_response = client.get(
        f"/api/books/search?title={quote(searched_book.title)}")
    assert search_response.status_code == 200
    # Verify the search results
    data = search_response.get_json()
    if 'books' not in data:
        assert False
    response_books = data['books']
    assert isinstance(response_books, list)
    assert len(response_books) > 0
    assert all(book["title"] == searched_book.title for book in response_books)


@pytest.mark.parametrize("num_books", [1, 10, 20])
def test_search_books_by_isbn_single_result(client, book_factory, num_books):
    books = book_factory.create_batch(num_books)
    # Search by title
    searched_book = choice(books)
    search_response = client.get(
        f"/api/books/search?isbn={quote(searched_book.isbn_13)}")
    assert search_response.status_code == 200
    # Verify the search results
    data = search_response.get_json()
    if 'books' not in data:
        assert False
    response_books = data['books']
    assert isinstance(response_books, list)
    assert len(response_books) > 0
    assert all(
        (book["isbn_10"] == searched_book.isbn_10
            and book["isbn_13"] == searched_book.isbn_13
         ) for book in response_books)


def test_search_books_query(client, book_factory, author_factory):
    # Create a batch of books
    book_with_title = book_factory.create(title="The Great Gatsby")
    book_with_description = book_factory.create(description="A tale of great love and loss")
    book_with_author = book_factory.create()
    author = author_factory.create(name="The Great Author")
    book_with_author.authors.append(author)
    search_response = client.get(
        f"/api/books/search?keyword={quote('great')}")
    assert search_response.status_code == 200
    # Verify the search results are both books
    data = search_response.get_json()
    if 'books' not in data:
        assert False
    response_books = data['books']
    assert isinstance(response_books, list)
    book_ids = {book["id"] for book in response_books}
    assert book_with_title.id in book_ids
    assert book_with_description.id in book_ids
    assert book_with_author.id in book_ids


@pytest.mark.parametrize("num_books", [1, 20])
def test_search_books_no_results(client, book_factory, num_books):
    book_factory.create_batch(num_books)
    # Search for a non-existing book
    search_response = client.get("/api/books/search?title=NonExistentTitle")
    assert search_response.status_code == 404
    # Verify the response contains an appropriate message
    data = search_response.get_json()
    assert "message" in data
    assert data["message"] == "No books found matching the search criteria"


@pytest.mark.parametrize("num_genres", [1, 2, 5])
def test_add_genre_to_book(client, book_factory, genre_factory, num_genres):
    book = book_factory.create()
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
    updated_book = db.session.execute(
        select(Book).where(Book.id == book.id)).scalar()
    if updated_book is None:
        assert False
    assert len(updated_book.genres) == num_genres


@pytest.mark.parametrize("num_genres", [1, 2, 5])
def test_remove_genre_from_book(client, book_factory, genre_factory, num_genres):
    book = book_factory.create()
    genres = genre_factory.create_batch(num_genres)
    genre_to_remove = choice(genres)
    book.genres.extend(genres)
    assert genre_to_remove in book.genres
    # Remove the genre from the book
    remove_genre_response = client.delete(
        f"/api/books/{book.id}/genres/{genre_to_remove.id}",
        content_type="application/json",
    )
    assert remove_genre_response.status_code == 200
    assert genre_to_remove not in book.genres
    assert len(book.genres) == num_genres - 1


@pytest.mark.parametrize("num_series", [1, 2, 5])
def test_add_series_to_book(client, book_factory, series_factory, num_series):
    series = series_factory.create_batch(num_series)
    book = book_factory.create()
    book.series = []
    for s in series:
        # Add the series to the book
        update_book_response = client.put(
            f"/api/books/{book.id}/series",
            data=json.dumps({"series_id": [s.id]}),
            content_type="application/json",
        )
        assert update_book_response.status_code == 200
        assert s in book.series
    assert len(book.series) == num_series


@pytest.mark.parametrize("num_series", [1, 2, 5])
def test_remove_series_from_book(client, book_factory, series_factory, num_series):
    book = book_factory.create()
    series = series_factory.create_batch(num_series)
    series_to_remove = choice(series)
    book.series.extend(series)
    assert len(book.series) == num_series
    assert series_to_remove in book.series
    # Remove the series from the book
    remove_series_response = client.delete(
        f"/api/books/{book.id}/series/{series_to_remove.id}",
        content_type="application/json",
    )
    assert remove_series_response.status_code == 200
    assert series_to_remove not in book.series
    assert len(book.series) == num_series - 1


# def test_get_popular_books(client, book_factory, ):
#     book = book_factory.create()
#     assert False
