from pprint import pprint
from app.schemas import UserSchema, CartSchema
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
    cart = cart_factory.create()
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
    pprint(CartSchema().dump(cart))
    assert False
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
