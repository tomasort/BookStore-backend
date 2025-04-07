from pprint import pprint
from flask import url_for
from faker import Faker
import json
from random import choice, sample, randint
from app import db
from app.models import Author
from app.schemas import AuthorSchema
from sqlalchemy import select, func
import pytest


def test_process_checkout_not_logged_in(client, cart_factory):
    cart = cart_factory.create()
    # Make sure the books in the cart are in stock
    for item in cart.items:
        book = item.book
        book.stock = item.quantity + 1
    cart.user = None
    response = client.post(
        url_for("checkout.process_checkout"),
        data=json.dumps({
            "cart_id": cart.id,
            "payment_method": "stripe",
        }),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Checkout successful'


def test_process_checkout_logged_in(client, cart_factory, regular_user, user_token, user_csrf_token):
    cart = cart_factory.create()
    # Make sure the books in the cart are in stock
    for item in cart.items:
        book = item.book
        book.stock = item.quantity + 1
    cart.user = regular_user
    print(f"User: {regular_user.id}")
    client.set_cookie("access_token_cookie", user_token)
    response = client.post(
        url_for("checkout.process_checkout"),
        data=json.dumps({
            "cart_id": cart.id,
            "payment_method": "stripe",
        }),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    print(response.data)
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Checkout successful'


def test_process_checkout_empty_cart(client, cart_factory):
    cart = cart_factory.create()
    cart.items = []
    cart.user = None
    response = client.post(
        url_for("checkout.process_checkout"),
        data=json.dumps({
            "cart_id": cart.id,
            "payment_method": "stripe",
        }),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Cart is empty'

def test_process_checkout_item_out_of_stock(client, cart_factory):
    cart = cart_factory.create()
    item_out_of_stock = choice(cart.items)
    item_out_of_stock.book.stock = 0
    cart.user = None
    response = client.post(
        url_for("checkout.process_checkout"),
        data=json.dumps({
            "cart_id": cart.id,
            "payment_method": "stripe",
        }),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == f"Book '{item_out_of_stock.book.title}' is out of stock"
