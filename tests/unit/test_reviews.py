from app.schemas import BookSchema, ReviewSchema
from app import db
from app.models import Review
import json
from pprint import pprint


def test_get_reviews(client, review_factory):
    review_factory.create_batch(5)
    response = client.get('/api/reviews')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 5


def test_get_reviews_for_book(client, review_factory, book_factory):
    book = book_factory.create()
    review_factory.create_batch(3, book=book)
    review_factory.create_batch(5)
    avg_rating = sum([review.rating for review in book.reviews]) / len(book.reviews)
    response = client.get(f'/api/reviews/{book.id}')
    assert response.status_code == 200
    data = response.get_json()
    print(data)
    assert data['total_count'] == 3
    assert data['average_rating'] == avg_rating


def test_add_review(client, book_factory, regular_user, user_token, user_csrf_token):
    book = book_factory.create()
    assert len(book.reviews) == 0
    client.set_cookie("access_token_cookie", user_token)
    response = client.post(
        f'/api/reviews/{book.id}',
        data=json.dumps({"comment": "Great book", "rating": 5}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Review added successfully'
    assert len(book.reviews) == 1
    assert book.reviews[0].comment == 'Great book'


def test_update_review(client, review_factory, book_factory, regular_user, user_token, user_csrf_token):
    book = book_factory.create()
    review = review_factory.create(book=book, user=regular_user)
    client.set_cookie("access_token_cookie", user_token)
    response = client.put(
        f'/api/reviews/{book.id}',
        data=json.dumps({"comment": "Updated review", "rating": 4}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review updated successfully'
    assert review.comment == 'Updated review'
    assert review.rating == 4


def test_delete_review(client, review_factory, book_factory, regular_user, user_token, user_csrf_token):
    book = book_factory.create()
    review = review_factory.create(book=book, user=regular_user)
    client.set_cookie("access_token_cookie", user_token)
    response = client.delete(
        f'/api/reviews/{book.id}',
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review deleted successfully'
    assert db.session.query(Review).filter_by(id=review.id).first() is None
