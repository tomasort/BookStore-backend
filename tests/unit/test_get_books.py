import json
from pprint import pprint
from faker import Faker
from random import choice
import pytest
from app import db
from app.api.models import Book
from app.api.schemas import BookSchema
from sqlalchemy import select, func
from urllib.parse import quote


# @pytest.mark.parametrize("num_books, limit, page", [(20, 5, 1), (20, 5, 2), (10, 10, 1), (10, 5, 3)])
# def test_get_books_pagination(client, book_factory, num_books, limit, page, cleanup_db):
#     # Create a batch of books
#     book_factory.create_batch(num_books)
#     print(db.session.execute(select(func.count(Book.id))).scalar())
#     # Send a GET request with pagination parameters
#     response = client.get(f"/api/books?limit={limit}&page={page}")
#     assert response.status_code == 200
#     data = response.get_json()
#     assert "books" in data
#     pagination = data["pagination"]
#     assert pagination["pages"] == (num_books // limit) + (num_books % limit > 0)
#     assert isinstance(data["books"], list)
#     assert len(data["books"]) == min(limit, num_books - (page - 1) * limit)  # Ensure pagination works as expected


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
