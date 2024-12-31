import json
from faker import Faker
from random import choice
import pytest
from app import db
from app.api.models import Book
from app.api.schemas import BookSchema
from app.auth.schemas import UserSchema
from sqlalchemy import select, func
from urllib.parse import quote


def test_create_user(client):
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


def test_get_users(client, user_factory):
    users = user_factory.create_batch(3)
    response = client.get("/auth/users")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    created_user_ids = {user.id for user in users}
    response_user_ids = {user["id"] for user in data}
    assert created_user_ids.issubset(response_user_ids)


def test_get_user(client, user_factory):
    user = user_factory.create()
    response = client.get(f"/auth/users/{user.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == user.id
    assert data["username"] == user.username
    assert data["email"] == user.email


def test_get_user_not_found(client):
    response = client.get("/auth/users/1000")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "User not found"


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
    print(UserSchema().dumps(user))
    client.set_cookie("access_token_cookie", admin_token)
    response = client.delete(f"/auth/users/{user.id}", headers={"X-CSRF-TOKEN": admin_csrf_token})
    print(response.get_json())
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "User deleted successfully"


def test_delete_not_admin(client, user_factory, user_token, user_csrf_token):
    user = user_factory.create()
    print(user)
    client.set_cookie("access_token_cookie", user_token)
    response = client.delete(f"/auth/users/{user.id}", headers={"X-CSRF-TOKEN": user_csrf_token})
    assert response.status_code == 403
