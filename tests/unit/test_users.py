import json
from faker import Faker
from random import choice
import pytest
from app import db
from app.api.models import Book
from app.api.schemas import BookSchema
from sqlalchemy import select, func
from urllib.parse import quote


def test_create_user(client):
    fake = Faker()
    response = client.post(
        "/auth/users",
        data=json.dumps({
            "username": fake.user_name(),
            "email": fake.email(),
        }),
        content_type="application/json"
    )
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
            "email": email
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
            "email": fake.email()
        }),
        content_type="application/json"
    )
    print(response.get_json())
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data["error"] == "Username is already taken"


def test_create_user_missing_required_fields(client):
    response = client.post(
        "/auth/users",
        data=json.dumps({
            "email": "missing_username@example.com"
        }),
        content_type="application/json"
    )

    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data["error"] == "Validation failed"
    assert "username" in response_data["details"]


def test_get_users(client, user_factory):
    users = user_factory.create_batch(3)
    response = client.get("/auth/users")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    created_user_ids = {user.id for user in users}
    response_user_ids = {user["id"] for user in data}
    assert created_user_ids.issubset(response_user_ids)
