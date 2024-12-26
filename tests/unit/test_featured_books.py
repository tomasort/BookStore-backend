from datetime import datetime
import json
from faker import Faker
from random import choice
import pytest
from app import db
from sqlalchemy import select, func
from urllib.parse import quote
from app.api.models import FeaturedBook
from app.api.schemas import FeaturedBookSchema


def test_create_featured_book(client, book_factory):
    book = book_factory.create()
    featured_book = {
        "book_id": book.id,
        "priority": 1,
        "featured_date": "2023-01-01",
        "expiry_date": "2023-01-31"
    }
    assert db.session.execute(select(FeaturedBook).where(FeaturedBook.book_id == book.id)).scalar() is None
    response = client.post(
        "/api/featured_books",
        data=json.dumps(featured_book),
        content_type="application/json"
    )
    data = response.get_json()
    featured_book_id = data["featured_book_id"]
    assert response.status_code == 201
    assert db.session.execute(select(FeaturedBook).where(FeaturedBook.book_id == book.id)).scalar() is not None
    featured_book_in_db = db.session.execute(select(FeaturedBook).where(FeaturedBook.id == featured_book_id)).scalar()
    assert featured_book_in_db.book == book


def test_get_featured_books(client, featured_book_factory):
    featured_books = featured_book_factory.create_batch(10)
    response = client.get("/api/featured_books")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    # verify that the created featured_books is a subset of the returned featured_books
    created_featured_books_ids = {featured_book.id for featured_book in featured_books}
    response_featured_books_ids = {featured_book["id"] for featured_book in data}
    assert created_featured_books_ids.issubset(response_featured_books_ids)


def test_get_specific_featured_book(client, featured_book_factory):
    featured_books = featured_book_factory.create_batch(10)
    test_featured_book = choice(featured_books)
    response = client.get(f"/api/featured_books/{test_featured_book.id}")
    assert response.status_code == 200
    returned_featured_book = response.get_json()
    assert returned_featured_book["id"] == test_featured_book.id
    assert returned_featured_book["book_id"] == test_featured_book.book_id
    assert returned_featured_book["priority"] == test_featured_book.priority


def test_update_priority_featured_book(client, featured_book_factory):
    fake = Faker()
    featured_books = featured_book_factory.create_batch(10)
    test_featured_book = choice(featured_books)
    new_priority = fake.random_int(min=1, max=10)
    response = client.put(
        f"/api/featured_books/{test_featured_book.id}",
        data=json.dumps({"priority": new_priority}),
        content_type="application/json"
    )
    assert response.status_code == 200
    updated_featured_book = db.session.execute(select(FeaturedBook).where(FeaturedBook.id == test_featured_book.id)).scalar()
    assert updated_featured_book.priority == new_priority


def test_update_expiry_date_featured_book(client, featured_book_factory):
    fake = Faker()
    featured_books = featured_book_factory.create_batch(10)
    test_featured_book = choice(featured_books)
    new_expiry_date = fake.date_between(start_date="today", end_date="+30d").isoformat()
    response = client.put(
        f"/api/featured_books/{test_featured_book.id}",
        data=json.dumps({"expiry_date": new_expiry_date}),
        content_type="application/json"
    )
    assert response.status_code == 200
    updated_featured_book = db.session.execute(select(FeaturedBook).where(FeaturedBook.id == test_featured_book.id)).scalar()
    assert updated_featured_book.expiry_date == datetime.strptime(new_expiry_date, "%Y-%m-%d").date()


def test_delete_featured_book(client, featured_book_factory):
    featured_books = featured_book_factory.create_batch(10)
    test_featured_book = choice(featured_books)
    response = client.delete(f"/api/featured_books/{test_featured_book.id}")
    assert response.status_code == 200
    deleted_featured_book = db.session.execute(select(FeaturedBook).where(FeaturedBook.id == test_featured_book.id)).scalar()
    assert deleted_featured_book is None
