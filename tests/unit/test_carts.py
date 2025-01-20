from pprint import pprint
import pytest
from app.schemas import UserSchema, CartSchema, CartItemSchema
import json


def test_get_cart_with_user(client, cart_factory, regular_user, user_token):
    cart = cart_factory.create(user=regular_user)
    client.set_cookie("access_token_cookie", user_token)
    response = client.get('/cart')
    data = response.get_json()
    assert response.status_code == 200
    assert data['id'] == cart.id
    assert data['user']['id'] == regular_user.id
    assert 'items' in data


def test_get_cart_without_user(client, cart_factory, user_factory):
    # Create a cart without a user
    cart = cart_factory.create(user=None)
    # Mock session cart_id
    with client.session_transaction() as session:
        session['cart_id'] = cart.id
    response = client.get('/cart')
    assert response.status_code == 200
    assert response.json['id'] == cart.id


def test_get_cart_new_cart_with_user(client, regular_user, user_token):
    client.set_cookie("access_token_cookie", user_token)
    response = client.get('/cart')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 0
    assert data['user']['id'] == regular_user.id


def test_get_cart_new_cart_without_user(client):
    response = client.get('/cart')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 0
    assert data['user'] is None


def test_add_to_cart_with_existing_cart_and_user(client, regular_user, user_token, cart_factory, book_factory, user_csrf_token):
    cart = cart_factory.create(user=regular_user)
    book = book_factory.create()
    assert book not in [item.book for item in cart.items]
    assert cart.user == regular_user
    client.set_cookie("access_token_cookie", user_token)
    response = client.post(
        '/cart/add',
        data=json.dumps({"book_id": book.id, "quantity": 2}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Item added to cart'
    assert 'cart' in data
    assert book in [item.book for item in cart.items]


def test_add_to_cart_with_existing_cart_without_user(client, cart_factory, book_factory):
    cart = cart_factory.create(user=None)
    with client.session_transaction() as session:
        session['cart_id'] = cart.id
    book = book_factory.create()
    assert book not in [item.book for item in cart.items]
    response = client.post(
        '/cart/add',
        data=json.dumps({"book_id": book.id, "quantity": 2}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Item added to cart'
    assert book in [item.book for item in cart.items]


def test_update_cart_with_existing_cart_and_user(client, regular_user, user_token, cart_factory, cart_item_factory, book_factory, user_csrf_token):
    cart = cart_factory.create(user=regular_user)
    book = book_factory.create()
    cart_item = cart_item_factory.create(cart=cart, book=book, quantity=2)
    assert cart_item.quantity == 2
    assert cart_item.book == book
    assert cart_item.cart == cart
    client.set_cookie("access_token_cookie", user_token)
    response = client.put(
        '/cart/update',
        data=json.dumps({"book_id": book.id, "quantity": 4}),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": user_csrf_token}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Item added to cart'
    assert 'cart' in data
    assert cart_item.quantity == 4
    for item in data['cart']['items']:
        if item['id'] == cart_item.id:
            assert item['quantity'] == 4
            break


def test_update_cart_with_existing_cart_no_user(client, cart_factory, cart_item_factory, book_factory):
    cart = cart_factory.create()
    book = book_factory.create()
    cart_item = cart_item_factory.create(cart=cart, book=book, quantity=2)
    assert cart_item.quantity == 2
    assert cart_item.book == book
    assert cart_item.cart == cart
    with client.session_transaction() as session:
        session['cart_id'] = cart.id
    response = client.put(
        '/cart/update',
        data=json.dumps({"book_id": book.id, "quantity": 4}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Item added to cart'
    assert 'cart' in data
    assert cart_item.quantity == 4
    for item in data['cart']['items']:
        if item['id'] == cart_item.id:
            assert item['quantity'] == 4
            break


@pytest.mark.parametrize("total_quantity, quantity_to_remove", [(2, 1), (2, 2), (4, 2), (1, 1)])
def test_remove_from_cart_with_existing_cart_and_user(total_quantity, quantity_to_remove, client, regular_user, user_token, cart_factory, cart_item_factory, book_factory, user_csrf_token):
    cart = cart_factory.create(user=regular_user)
    book = book_factory.create()
    cart_item = cart_item_factory.create(cart=cart, book=book, quantity=total_quantity)
    assert book in [item.book for item in cart.items]
    client.set_cookie("access_token_cookie", user_token)
    response = client.delete(
        '/cart/remove',
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
