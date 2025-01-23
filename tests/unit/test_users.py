import json
import pdb
from flask_jwt_extended import create_access_token, get_csrf_token
from pprint import pprint
from faker import Faker
from random import choice
import pytest
from app import db
from app.models import Book
from app.schemas import BookSchema
from app.schemas import UserSchema
from sqlalchemy import select, func
from urllib.parse import quote


def test_register_user(client):
    fake = Faker()
    response = client.post(
        "/auth/users",
        data=json.dumps({
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password()
        }),
        content_type="application/json"
    )
    print(response.get_json())
    assert response.status_code == 201
    response_data = response.get_json()
    assert "user_id" in response_data


def test_create_user_no_input(client):
    response = client.post(
        "/auth/users",
        data=json.dumps({}),
        content_type="application/json"
    )
    assert response.status_code == 400


def test_create_user_invalid_input(client):
    response = client.post(
        "/auth/users",
        data=json.dumps({"email": "invalid"}),
        content_type="application/json"
    )
    assert response.status_code == 400


def test_create_user_duplicate_email(client, user_factory):
    # Create a user with the same email
    fake = Faker()
    email = fake.email()
    user_factory.create(email=email)
    response = client.post(
        "/auth/users",
        data=json.dumps({
            "username": fake.user_name(),
            "email": email,
            "password": fake.password()
        }),
        content_type="application/json"
    )
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data["error"] == "Email is already taken"


def test_create_user_duplicate_username(client, user_factory):
    # Create a user with the same username
    fake = Faker()
    username = fake.user_name()
    user_factory.create(username=username)
    response = client.post(
        "/auth/users",
        data=json.dumps({
            "username": username,
            "email": fake.email(),
            "password": fake.password()
        }),
        content_type="application/json"
    )
    print(response.get_json())
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data["error"] == "Username is already taken"


def test_get_users(client, user_factory, admin_token):
    users = user_factory.create_batch(3)
    client.set_cookie("access_token_cookie", admin_token)
    response = client.get("/auth/users")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    created_user_ids = {user.id for user in users}
    response_user_ids = {user["id"] for user in data}
    assert created_user_ids.issubset(response_user_ids)


def test_get_user(client, regular_user, user_token):
    client.set_cookie("access_token_cookie", user_token)
    response = client.get(f"/auth/users/{regular_user.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == regular_user.id
    assert data["username"] == regular_user.username
    assert data["email"] == regular_user.email


def test_login(client, user_factory):
    fake = Faker()
    password = fake.password()
    user = user_factory.create(password=password)
    response = client.post(
        "/auth/login",
        data=json.dumps({
            "username": user.username,
            "password": password
        }),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Login successful"
    assert data["user_id"] == user.id


def test_login_required_pages(client, admin_token):
    client.set_cookie("access_token_cookie", admin_token)
    response = client.get(
        "/auth/protected"
    )
    assert response.status_code == 200


def test_login_required_pages_fail(client, user_token):
    client.set_cookie("access_token_cookie", user_token)
    response = client.get(
        "/auth/protected"
    )
    assert response.status_code == 403


def test_delete_user(client, user_factory, admin_token, admin_csrf_token):
    user = user_factory.create()
    client.set_cookie("access_token_cookie", admin_token)
    response = client.delete(f"/auth/users/{user.id}", headers={"X-CSRF-TOKEN": admin_csrf_token})
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "User deleted successfully"


def test_delete_not_admin(client, user_factory, user_token, user_csrf_token):
    user = user_factory.create()
    client.set_cookie("access_token_cookie", user_token)
    response = client.delete(f"/auth/users/{user.id}", headers={"X-CSRF-TOKEN": user_csrf_token})
    assert response.status_code == 403


@pytest.mark.parametrize("num_of_favorite_books", [1, 3, 5])
def test_get_user_favorites(client, user_factory, book_factory, num_of_favorite_books):
    user = user_factory.create(favorites__size=num_of_favorite_books)
    books = user.favorites
    response = client.get(f"/auth/users/{user.id}/favorites")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == num_of_favorite_books
    assert all(isinstance(book, dict) for book in data)
    # chech that the book ids are the same
    response_book_ids = {book["id"] for book in data}
    created_book_ids = {book.id for book in books}
    assert response_book_ids == created_book_ids


def test_add_user_favorite(client, regular_user, user_token, user_csrf_token, book_factory):
    user = regular_user
    book = book_factory.create()
    num_user_favorites = len(user.favorites)
    client.set_cookie("access_token_cookie", user_token)
    response = client.post(
        f"/auth/users/{user.id}/favorites",
        data=json.dumps({"book_id": book.id}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Book added to favorites successfully"
    assert book in user.favorites
    assert len(user.favorites) == num_user_favorites + 1


def test_add_user_favorite_without_token(client, user_factory, user_token, user_csrf_token, book_factory):
    user = user_factory.create()
    book = book_factory.create()
    client.set_cookie("access_token_cookie", user_token)
    response = client.post(
        f"/auth/users/{user.id}/favorites",
        data=json.dumps({"book_id": book.id}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["error"] == "You are not authorized to perform this action"


@pytest.mark.parametrize("num_of_wishlist_books", [1, 3, 5])
def test_get_user_wishlist(client, user_factory, num_of_wishlist_books):
    user = user_factory.create(wishlist__size=num_of_wishlist_books)
    books = user.wishlist
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": "user"})
    client.set_cookie("access_token_cookie", access_token)
    response = client.get(f"/auth/users/{user.id}/wishlist")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == num_of_wishlist_books
    assert all(isinstance(book, dict) for book in data)
    # chech that the book ids are the same
    response_book_ids = {book["id"] for book in data}
    created_book_ids = {book.id for book in books}
    assert response_book_ids == created_book_ids


def test_get_user_wishlist_no_token(client, user_factory):
    user = user_factory.create()
    response = client.get(f"/auth/users/{user.id}/wishlist")
    assert response.status_code == 401


def test_update_user_personal_info(client, regular_user, user_token, user_csrf_token):
    fake = Faker()
    user = regular_user
    client.set_cookie("access_token_cookie", user_token)
    new_username = fake.user_name()
    new_email = fake.email()
    response = client.put(
        f"/auth/users/{user.id}",
        data=json.dumps({"username": new_username, "email": new_email, 'date_of_birth': '10/29/1995'}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "User updated successfully"
    assert user.username == new_username
    assert user.email == new_email


def test_update_user_personal_info_not_the_right_user(client, regular_user, user_token, user_csrf_token, user_factory):
    fake = Faker()
    user = user_factory.create()
    client.set_cookie("access_token_cookie", user_token)
    new_username = fake.user_name()
    new_email = fake.email()
    response = client.put(
        f"/auth/users/{user.id}",
        data=json.dumps({"username": new_username, "email": new_email}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["error"] == "You are not authorized to perform this action"


def test_update_password(client, regular_user, user_token, user_csrf_token):
    fake = Faker()
    user = regular_user
    user_password = 'password'  # we use the default password for the regular user (and all other users)
    new_password = fake.password()
    client.set_cookie("access_token_cookie", user_token)
    response = client.put(
        f"/auth/users/{user.id}/password",
        data=json.dumps({"current_password": user_password, "new_password": new_password}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "User password updated successfully"
    assert user.check_password(new_password)


def test_update_password_wrong_current_password(client, regular_user, user_token, user_csrf_token):
    fake = Faker()
    user = regular_user
    user_password = 'wrong_password'  # we use the default password for the regular user (and all other users)
    new_password = fake.password()
    client.set_cookie("access_token_cookie", user_token)
    response = client.put(
        f"/auth/users/{user.id}/password",
        data=json.dumps({"current_password": user_password, "new_password": new_password}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Current password is incorrect"
    assert user.check_password('password')  # the password should not have changed
