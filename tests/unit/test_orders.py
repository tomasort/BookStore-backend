import json
from sqlalchemy import select, func
from app.schemas import OrderSchema, OrderItemSchema
from app.models import Order, OrderItem
from app import db
import pytest


order_schema = OrderSchema()
order_item_schema = OrderItemSchema()


@pytest.mark.parametrize("num_orders", [1, 3, 10])
def test_get_orders(client, order_factory, num_orders):
    orders = order_factory.create_batch(num_orders)
    num_orders_in_db = db.session.execute(select(func.count()).select_from(Order)).scalar()
    response = client.get("/orders")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == num_orders_in_db
    created_order_ids = {order.id for order in orders}
    response_order_ids = {order["id"] for order in data}
    assert created_order_ids.issubset(response_order_ids)


def test_create_order(client, order_factory, user_factory):
    user = user_factory.create()
    order = order_factory.build()
    order.user_id = user.id
    order_data = OrderSchema(exclude=["id", "user"]).dump(order)
    print(order_data)
    response = client.post("/orders", json=order_data)
    print(response.get_json())
    response_json = response.get_json()
    assert response.status_code == 201
    assert response_json["message"] == "Order created successfully"
    assert "order_id" in response_json
    assert db.session.execute(select(Order).where(Order.id == response_json["order_id"])).scalar() is not None


def test_create_order_no_input(client):
    response = client.post("/orders", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "No Input data provided"


def test_create_order_invalid_input(client):
    response = client.post("/orders", json={"customer_id": "invalid"})
    assert response.status_code == 400
    assert "customer_id" in response.get_json()["error"]


def test_get_order_success(client, order_factory):
    order = order_factory.create()
    response = client.get(f"/orders/{order.id}")
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["id"] == order.id
    assert response_json["user_id"] == order.user_id
    assert response_json["status"] == order.status


def test_get_order_not_found(client):
    non_existent_order_id = 9999
    response = client.get(f"/orders/{non_existent_order_id}")
    assert response.status_code == 404
    response_json = response.get_json()
    assert "error" in response_json
    assert response_json["error"] == f"Order {non_existent_order_id} not found"


def test_get_order_invalid_id(client):
    response = client.get("/orders/invalid_id")
    assert response.status_code in {400, 404}


def test_update_order_success(client, order_factory):
    order = order_factory.create()
    updated_data = {"status": "shipped"}
    response = client.put(f"/orders/{order.id}", json=updated_data)
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["message"] == f"Order {order.id} updated successfully"
    updated_order = db.session.execute(select(Order).where(Order.id == order.id)).scalar()
    assert updated_order is not None
    assert updated_order.status == updated_data["status"]


def test_update_order_not_found(client):
    non_existent_order_id = 9999
    updated_data = {"status": "shipped"}
    response = client.put(f"/orders/{non_existent_order_id}", json=updated_data)
    assert response.status_code == 404
    assert response.get_json()["error"] == f"Order {non_existent_order_id} not found"


def test_update_order_invalid_data(client, order_factory):
    order = order_factory.create()
    invalid_data = {"invalid_field": "value"}
    response = client.put(f"/orders/{order.id}", json=invalid_data)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_delete_order_success(client, order_factory):
    order = order_factory.create()
    print(f"/orders/{order.id}")
    response = client.delete(f"/orders/{order.id}")
    print(response)
    print(response.get_json())
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["message"] == f"Order {order.id} deleted successfully"
    assert db.session.execute(select(Order).where(Order.id == order.id)).scalar() is None


def test_delete_order_not_found(client):
    non_existent_order_id = 9999
    response = client.delete(f"/orders/{non_existent_order_id}")
    assert response.status_code == 404
    assert response.get_json()["error"] == f"Order {non_existent_order_id} not found"


def test_get_order_items_success(client, order_factory):
    order = order_factory.create()
    response = client.get(f"/orders/{order.id}/items")
    assert response.status_code == 200
    response_json = response.get_json()
    assert isinstance(response_json, list)
    assert len(response_json) == len(order.items)
    for item, response_item in zip(order.items, response_json):
        assert item.book_id == response_item["book_id"]
        assert item.quantity == response_item["quantity"]
        assert str(item.price) == response_item["price"]


def test_get_order_items_not_found(client):
    non_existent_order_id = 9999
    response = client.get(f"/orders/{non_existent_order_id}/items")
    assert response.status_code == 404
    response_json = response.get_json()
    assert "error" in response_json
    assert response_json["error"] == f"Order {non_existent_order_id} not found"


def test_add_order_item_success(client, order_factory, order_item_factory, book_factory):
    order = order_factory.create()
    old_order_item_count = len(order.items)
    book = book_factory.create()
    order_item = order_item_factory.build()
    order_item.book = book
    order_item.book_id = book.id
    order_item_data = OrderItemSchema(exclude=["id", "order_id"]).dump(order_item)
    response = client.post(f"/orders/{order.id}/items", json=order_item_data)
    assert response.status_code == 201
    response_json = response.get_json()
    assert response_json["message"] == "Order item added successfully"
    assert len(order.items) == old_order_item_count + 1
