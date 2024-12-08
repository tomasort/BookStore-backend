from sqlalchemy import select
from flask import request, jsonify
from app.orders import orders
from app.orders.models import Order, OrderItem
from app.orders.schemas import OrderSchema, OrderItemSchema
from app import db

order_schema = OrderSchema()
order_item_schema = OrderItemSchema()


@orders.route('', methods=['GET'])
def get_orders():
    orders = db.session.execute(select(Order)).scalars().all()
    serialized_orders = order_schema.dump(orders, many=True)
    return jsonify(serialized_orders)


@orders.route('', methods=['POST'])
def create_order():
    data = request.json
    if not data:
        return jsonify({'error': "No Input data provided"}), 400
    try:
        order_data = order_schema.load(data)
        new_order = Order(**order_data)
        db.session.add(new_order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    return jsonify({'message': "Order created successfully", 'order_id': new_order.id}), 201


@orders.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = db.session.execute(select(Order).where(Order.id == order_id)).scalar()
    if not order:
        return jsonify({'error': f"Order {order_id} not found"}), 404

    serialized_order = order_schema.dump(order)
    return jsonify(serialized_order)


@orders.route('/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    if not data:
        return jsonify({'error': "No Input data provided"}), 400
    try:
        order = db.session.execute(select(Order).where(Order.id == order_id)).scalar()
        if not order:
            return jsonify({'error': f"Order {order_id} not found"}), 404
        order_data = order_schema.load(data, partial=True)
        for key, value in order_data.items():
            setattr(order, key, value)
        db.session.commit()
        return jsonify({'message': f"Order {order_id} updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@orders.route('/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        order = db.session.execute(select(Order).where(Order.id == order_id)).scalar()
        if not order:
            return jsonify({'error': f"Order {order_id} not found"}), 404
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': f"Order {order_id} deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@orders.route('/<int:order_id>/items', methods=['GET'])
def get_order_items(order_id):
    try:
        order = db.session.execute(select(Order).where(Order.id == order_id)).scalar()
        if not order:
            return jsonify({"error": f"Order {order_id} not found"}), 404

        items = order.items
        serialized_items = order_item_schema.dump(items, many=True)
        return jsonify(serialized_items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@orders.route('/<int:order_id>/items', methods=['POST'])
def add_order_item(order_id):
    data = request.json
    if not data:
        return jsonify({'error': "No Input data provided"}), 400
    try:
        order = db.session.execute(select(Order).where(Order.id == order_id)).scalar()
        if not order:
            return jsonify({'error': f"Order {order_id} not found"}), 404
        # TODO: find the book that they are trying to add to the order
        # TODO: check if the book is in stock
        item_data = order_item_schema.load(data)
        new_item = OrderItem(**item_data)
        order.items.append(new_item)
        db.session.commit()
        return jsonify({'message': "Order item added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
