from faker import Faker
from flask import url_for
from app.schemas import UserSchema, CartSchema, CartItemSchema
from app.models import Cart
import json
import pytest


def test_get_cart_with_user(client, cart_factory, regular_user, user_token):
    """Test get cart with user access token cookie"""
    cart = cart_factory.create(user=regular_user)
    assert cart.user == regular_user
    assert regular_user.cart == cart
    client.set_cookie("access_token_cookie", user_token)
    response = client.get(url_for('cart.get_cart'))
    data = response.get_json()
    assert response.status_code == 200
    assert data['id'] == cart.id
    assert data['user']['id'] == regular_user.id
    assert 'items' in data


def test_get_cart_without_user(client, cart_factory, user_factory):
    """Test get cart without user access token which means the user is not logged in"""
    cart = cart_factory.create(user=None)
    assert cart.user is None
    # Mock session cart_id
    with client.session_transaction() as session:
        session['cart_id'] = cart.id
    response = client.get(url_for('cart.get_cart'))
    assert response.status_code == 200
    assert response.json['id'] == cart.id


def test_get_cart_new_cart_with_user(client, regular_user, user_token):
    """Test get cart with user access token cookie and no cart in the session"""
    assert regular_user.cart is None
    client.set_cookie("access_token_cookie", user_token)
    response = client.get(url_for('cart.get_cart'))
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 0
    assert data['user']['id'] == regular_user.id
    assert regular_user.cart is not None


def test_get_cart_new_cart_without_user(client):
    """Test get cart without user access token cookie and no cart in the session"""
    response = client.get(url_for('cart.get_cart'))
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 0
    assert data['user'] is None


def check_cart_item_quantity(cart, book, quantity):
    for item in cart.items:
        if item.book == book:
            assert item.quantity == quantity
            return
    assert False


def test_add_to_cart_with_existing_cart_and_user(client, regular_user, user_token, cart_factory, book_factory, user_csrf_token):
    """Test add to cart with existing cart and user access token cookie"""
    fake = Faker()
    cart = cart_factory.create(user=regular_user)
    book = book_factory.create()
    assert book not in [item.book for item in cart.items]
    assert cart.user == regular_user
    cart_item_data = {
        "book_id": book.id,
        "quantity": fake.random_int(min=1, max=10)
    }
    client.set_cookie("access_token_cookie", user_token)
    response = client.post(
        url_for('cart.add_to_cart'),
        data=json.dumps(cart_item_data),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Item added to cart'
    assert 'cart' in data
    check_cart_item_quantity(cart, book, cart_item_data['quantity'])


def test_add_to_cart_with_existing_cart_without_user(client, cart_factory, book_factory):
    """Test add to cart with existing cart and no user access token cookie"""
    fake = Faker()
    cart = cart_factory.create(user=None)
    assert cart.user is None
    with client.session_transaction() as session:
        session['cart_id'] = cart.id
    book = book_factory.create()
    assert book not in [item.book for item in cart.items]
    cart_item_data = {
        "book_id": book.id,
        "quantity": fake.random_int(min=1, max=10)
    }
    response = client.post(
        url_for('cart.add_to_cart'),
        data=json.dumps(cart_item_data),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Item added to cart'
    check_cart_item_quantity(cart, book, cart_item_data['quantity'])


@pytest.mark.parametrize("quantity, change", [(2, 1), (4, 2), (1, -1), (2, -2)])
def test_update_cart_with_existing_cart_and_user(client, regular_user, user_token, cart_factory, cart_item_factory, book_factory, user_csrf_token, quantity, change):
    """Test update cart with existing cart and user access token cookie"""
    cart = cart_factory.create(user=regular_user)
    book = book_factory.create()
    cart_item = cart_item_factory.create(cart=cart, book=book, quantity=quantity)
    assert cart_item.quantity == quantity
    assert cart_item.book == book
    assert cart_item in cart.items
    client.set_cookie("access_token_cookie", user_token)
    response = client.put(
        url_for('cart.update_cart'),
        data=json.dumps({"book_id": book.id, "quantity": quantity + change}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Item added to cart'
    assert 'cart' in data
    if quantity + change > 0:
        assert cart_item.quantity == quantity + change
        for item in data['cart']['items']:
            if item['id'] == cart_item.id:
                assert item['quantity'] == quantity + change
                break
    else:
        assert cart_item not in cart.items


@pytest.mark.parametrize("quantity, change", [(2, 1), (4, 2), (1, -1), (2, -2)])
def test_update_cart_with_existing_cart_no_user(client, cart_factory, cart_item_factory, book_factory, quantity, change):
    cart = cart_factory.create()
    book = book_factory.create()
    cart_item = cart_item_factory.create(cart=cart, book=book, quantity=quantity)
    assert cart_item.quantity == quantity
    assert cart_item.book == book
    assert cart_item in cart.items
    with client.session_transaction() as session:
        session['cart_id'] = cart.id
    response = client.put(
        url_for('cart.update_cart'),
        data=json.dumps({"book_id": book.id, "quantity": quantity + change}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Item added to cart'
    assert 'cart' in data
    if quantity + change > 0:
        assert cart_item.quantity == quantity + change
        for item in data['cart']['items']:
            if item['id'] == cart_item.id:
                assert item['quantity'] == quantity + change
                break
    else:
        assert cart_item not in cart.items


@pytest.mark.parametrize("total_quantity, quantity_to_remove", [(2, 1), (2, 2), (4, 2), (1, 1)])
def test_remove_from_cart_with_existing_cart_and_user(total_quantity, quantity_to_remove, client, regular_user, user_token, cart_factory, cart_item_factory, book_factory, user_csrf_token):
    cart = cart_factory.create(user=regular_user)
    book = book_factory.create()
    cart_item = cart_item_factory.create(cart=cart, book=book, quantity=total_quantity)
    assert book in [item.book for item in cart.items]
    client.set_cookie("access_token_cookie", user_token)
    response = client.put(
        url_for('cart.remove_from_cart'),
        data=json.dumps({"book_id": book.id, "quantity": quantity_to_remove}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Item removed from cart'
    assert 'cart' in data
    if quantity_to_remove >= total_quantity:
        assert book not in [item.book for item in cart.items]
    else:
        for item in data['cart']['items']:
            if item['id'] == cart_item.id:
                assert item['quantity'] == total_quantity - quantity_to_remove
                break


# TODO: write test for remove_from_cart with no user

# TODO: write test for delete_cart with user and without user
