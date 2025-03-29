from flask import url_for
from faker import Faker
import json
from random import choice, sample, randint
from app import db
from app.models import Author
from app.schemas import AuthorSchema
from sqlalchemy import select, func
import pytest

author_schema = AuthorSchema()


def test_create_author(client, author_factory):
    author = author_factory.build()
    response = client.post(
        url_for("api.authors.create_author"),
        data=json.dumps(author_schema.dump(author)),
        content_type="application/json"
    )
    assert response.status_code == 201
    data = response.get_json()
    if "author_id" not in data:
        assert False
    book_in_db = db.session.execute(select(Author).where(Author.id == data["author_id"])).scalar()
    assert book_in_db is not None
    assert data["author_id"] == book_in_db.id
    assert data["message"] == "Author created successfully"


# NOTE: The following test is for a book route
@pytest.mark.parametrize("num_authors", [1, 3, 5])
def test_add_authors_to_book(client, book_factory, author_factory, num_authors):
    book = book_factory.create()
    authors = author_factory.create_batch(num_authors)
    num_authors_before = len(book.authors)
    for author in authors:
        assert author not in book.authors
    add_authors_response = client.put(
        url_for("api.books.add_authors_to_book", book_id=book.id),
        data=json.dumps({"author_ids": [author.id for author in authors]}),
        content_type="application/json"
    )
    assert add_authors_response.status_code == 200
    data = add_authors_response.get_json()
    assert data["message"] == "Authors added successfully"
    assert len(book.authors) == num_authors_before + num_authors
    # Verify that the authors were correctly added to the book
    for author in authors:
        assert author in book.authors


# NOTE: The following test is for a book route
def test_remove_authors_from_book(client, book_factory):
    book = book_factory.create()
    authors = book.authors
    assert len(authors) > 0
    num_authors = len(authors)
    author_to_delete = choice(authors)
    remove_authors_response = client.delete(
        url_for("api.books.remove_author_from_book", book_id=book.id, author_id=author_to_delete.id),
    )
    assert remove_authors_response.status_code == 200
    data = remove_authors_response.get_json()
    assert data["message"] == "Author removed successfully"
    # Verify that the authors were correctly removed from the book
    assert author_to_delete not in book.authors
    assert len(book.authors) == num_authors - 1


@pytest.mark.parametrize("num_authors", [1, 5])
def test_get_authors(client, author_factory, num_authors):
    authors = author_factory.create_batch(num_authors)
    response = client.get(url_for("api.authors.get_authors"))
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    created_author_ids = {author.id for author in authors}
    response_author_ids = {author['id'] for author in data}
    # Assert that all created authors are in the response
    assert created_author_ids.issubset(response_author_ids)


@pytest.mark.parametrize("num_authors", [1, 3])
def test_get_author(client, author_factory, num_authors):
    authors = author_factory.create_batch(num_authors)
    author_to_get = choice(authors)
    response = client.get(url_for("api.authors.get_author", author_id=author_to_get.id))
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == author_to_get.name
    assert data["id"] == author_to_get.id
    assert data["birth_date"] == str(author_to_get.birth_date)


def test_update_author(client, author_factory):
    fake = Faker()
    author = author_factory.create()
    new_data = {
        "name": fake.name(),
        "birth_date": fake.date_this_century().isoformat(),
        "biography": fake.paragraph()
    }
    response = client.put(
        url_for("api.authors.update_author", author_id=author.id),
        data=json.dumps(new_data),
        content_type="application/json"
    )
    # Assert that the request was successful
    assert response.status_code == 200
    assert author.name == new_data["name"]
    assert author.biography == new_data["biography"]
    assert str(author.birth_date) == new_data["birth_date"]


@pytest.mark.parametrize("num_authors", [1, 2, 3])
def test_delete_author(client, author_factory, num_authors):
    # Create a batch of authors
    authors = author_factory.create_batch(num_authors)
    author_to_delete = choice(authors)
    num_authors_in_db = db.session.execute(select(func.count()).select_from(Author)).scalar()
    response = client.delete(url_for("api.authors.delete_author", author_id=author_to_delete.id))
    # Assert that the request was successful
    assert response.status_code == 200
    # Check that the author was deleted
    deleted_author = db.session.execute(select(Author).where(Author.id == author_to_delete.id)).scalar()
    assert deleted_author is None
    # Verify the remaining authors still exist
    assert db.session.execute(select(func.count()).select_from(Author)).scalar() == num_authors_in_db - 1


# TODO: change the factory so that the authors have books already
@pytest.mark.parametrize("num_authors,author_books,total_books", [(1, 4, 10), (2, 3, 6), (5, 4, 10)])
def test_get_author_books(client, author_factory, book_factory, num_authors, author_books, total_books):
    authors = author_factory.create_batch(num_authors)
    books = book_factory.create_batch(total_books)
    # Choose an author to assign a specific number of books
    author_with_books = choice(authors)
    # Assign `author_books` to `author_with_books`
    books_to_assign = sample(books, author_books)
    author_with_books.books = books_to_assign
    # Randomly assign remaining books to other authors
    for author in authors:
        if author != author_with_books:
            author.books.extend(sample(books, randint(1, len(books) - 1)))
            db.session.commit()
    response = client.get(url_for("api.authors.get_books_by_author", author_id=author_with_books.id))
    # Assert that the request was successful
    assert response.status_code == 200
    data = response.get_json()
    # Validate that the data returned is correct
    assert isinstance(data, list)  # Should return a list of books
    # The list should have the correct number of books
    assert len(data) == len(books_to_assign)
