import json
from random import choice, sample, randint
from app import db
from app.api.models import Author
from sqlalchemy import select, func
import pytest


def test_create_author(client, author_factory):
    author = author_factory.build()
    response = client.post(
        "/api/authors",
        data=json.dumps(author.to_dict()),
        content_type="application/json"
    )
    assert response.status_code == 201
    data = response.get_json()
    if "author_id" not in data:
        assert False
    book_in_db = db.session.execute(select(Author).where(
        Author.id == data["author_id"])).scalar()
    if book_in_db is None:
        assert False
    assert data["author_id"] == book_in_db.id
    assert data["message"] == "Author created successfully"


@pytest.mark.parametrize("num_authors", [1, 3, 10, 20])
def test_add_authors_to_book(client, book_factory, author_factory, num_authors):
    book = book_factory.create()
    authors = author_factory.create_batch(num_authors)
    for author in authors:
        assert author not in book.authors
    # Send a PUT request to add authors to the book
    add_authors_response = client.put(
        f"/api/books/{book.id}/authors",
        data=json.dumps({"author_ids": [author.id for author in authors]}),
        content_type="application/json"
    )
    # Verify that the response is successful
    assert add_authors_response.status_code == 200
    data = add_authors_response.get_json()
    assert data["message"] == "Authors added successfully"
    # Verify that the authors were correctly added to the book
    for author in authors:
        assert author in book.authors


def test_remove_authors_from_book(client, book_factory):
    book = book_factory.create()
    authors = book.authors
    num_authors = len(authors)
    author_to_delete = choice(authors)
    # Send a DELETE request to remove the authors from the book
    remove_authors_response = client.delete(
        f"/api/books/{book.id}/authors/{author_to_delete.id}",
        content_type="application/json"
    )
    # Verify that the response is successful
    assert remove_authors_response.status_code == 200
    data = remove_authors_response.get_json()
    assert data["message"] == "Author removed successfully"
    # Verify that the authors were correctly removed from the book
    assert author_to_delete not in book.authors
    assert len(book.authors) == num_authors - 1


@pytest.mark.parametrize("num_authors", [1, 3, 10])
def test_get_authors(client, author_factory, num_authors):
    authors = author_factory.create_batch(num_authors)
    # Send a GET request to retrieve all authors
    response = client.get("/api/authors")
    # Assert that the request was successful
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)  # Should return a list of authors
    created_author_ids = {author.id for author in authors}
    response_author_ids = {author['id'] for author in data}
    # Assert that all created authors are in the response
    assert created_author_ids.issubset(response_author_ids)


@pytest.mark.parametrize("num_authors", [1, 3, 10])
def test_get_author(client, author_factory, num_authors):
    authors = author_factory.create_batch(num_authors)
    author_to_get = choice(authors)
    # Send a GET request to retrieve the author
    response = client.get(f"/api/authors/{author_to_get.id}")
    # Assert that the request was successful
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == author_to_get.name
    # Check that the author id is in the response
    assert data["id"] == author_to_get.id


@pytest.mark.parametrize("num_authors", [1, 3, 10])
def test_update_author(client, author_factory, num_authors):
    authors = author_factory.create_batch(num_authors)
    author_to_update = choice(authors)
    # Send a PUT request to update the author
    new_data = {
        "name": "New Name",
        "birth_date": "1990-01-01",
        "biography": "New Biography"
    }
    response = client.put(
        f"/api/authors/{author_to_update.id}",
        data=json.dumps(new_data),
        content_type="application/json"
    )
    # Assert that the request was successful
    assert response.status_code == 200
    assert author_to_update.name == new_data["name"]
    assert author_to_update.biography == new_data["biography"]


@pytest.mark.parametrize("num_authors", [1, 10, 20])
def test_delete_author(client, author_factory, num_authors):
    # Create a batch of authors
    authors = author_factory.create_batch(num_authors)
    author_to_delete = choice(authors)

    # Send a DELETE request to delete the author
    response = client.delete(f"/api/authors/{author_to_delete.id}")

    # Assert that the request was successful
    assert response.status_code == 200

    # Check that the author was deleted
    deleted_author = db.session.execute(select(Author).where(Author.id == author_to_delete.id)).scalar()
    assert deleted_author is None

    # Verify the remaining authors still exist by comparing their IDs
    remaining_author_ids = {author.id for author in authors if author != author_to_delete}
    db_author_ids = {id for id in db.session.execute(select(Author.id)).scalars()}

    # Assert that all remaining authors are still in the database
    assert remaining_author_ids.issubset(db_author_ids)


@pytest.mark.parametrize("num_authors,author_books,total_books", [
    (1, 4, 20),
    (2, 3, 6),  # Adjusted to make the test realistic
    (5, 4, 20)  # Adjusted parameters for clarity
])
def test_get_author_books(client, author_factory, book_factory, num_authors, author_books, total_books):
    authors = author_factory.create_batch(num_authors)
    books = book_factory.create_batch(total_books)
    # Choose an author to assign a specific number of books
    author_with_books = choice(authors)
    # Assign `author_books` to `author_with_books`
    books_to_assign = sample(books, author_books)
    author_with_books.books.extend(books_to_assign)
    db.session.commit()
    # Randomly assign remaining books to other authors
    for author in authors:
        if author != author_with_books:
            author.books.extend(sample(books, randint(1, len(books) - 1)))
            db.session.commit()
    # Send a GET request to retrieve the author's books
    response = client.get(f"/api/authors/{author_with_books.id}/books")
    # Assert that the request was successful
    assert response.status_code == 200
    data = response.get_json()
    # Validate that the data returned is correct
    assert isinstance(data, list)  # Should return a list of books
    # The list should have the correct number of books
    assert len(data) == len(books_to_assign)
