from sqlalchemy import select
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from app.checkout import checkout
from app.models import Order, OrderItem, Cart, User, Payment
from app.schemas import OrderSchema, OrderItemSchema
from app import db


@checkout.route('/methods', methods=['GET'])
def get_checkout_methods():
    return jsonify(Payment.get_payment_methods()), 200


# TODO: use celery to process the payment in the background
@checkout.route('', methods=['POST'])
@jwt_required(optional=True)
def process_checkout():
    try:
        user_id = get_jwt_identity()

        if user_id is not None:
            user_id = int(user_id)

        data = request.json

        payment_method = data.get('payment_method', '')
        cart_id = data.get('cart_id')

        # # Validate Payment Method
        # valid_payment_methods = [pm.value for pm in PaymentMethod]
        # if payment_method not in valid_payment_methods:
        #     return jsonify({'error': 'Invalid payment method'}), 400

        # Validate cart
        if not cart_id:
            return jsonify({'error': 'Cart ID is required'}), 400
        cart = db.session.query(Cart).filter_by(id=cart_id).first()
        if not cart:
            return jsonify({'error': 'Cart not found'}), 404
        if cart.user_id and cart.user_id != user_id:
            return jsonify({'error': 'Unauthorized access to cart'}), 403
        if len(cart.items) == 0:
            return jsonify({'error': 'Cart is empty'}), 400

        # Validate cart items
        total = 0
        for item in cart.items:
            if item.book.stock < item.quantity:
                return jsonify({'error': f"Book '{item.book.title}' is out of stock"}), 400
            total += item.book.price * item.quantity

        # Handle payment
        if payment_method == 'zelle':
            # Zelle: Manual payment (user sends payment manually)
            payment_status = 'pending'
            payment_instructions = "Please send the total amount to our Zelle account: example@zelle.com"
        elif payment_method == 'stripe':
            # Stripe: Automated payment (mocked here)
            payment_success = True  # Replace with actual Stripe integration
            payment_status = 'completed' if payment_success else 'failed'
            if payment_status == 'failed':
                return jsonify({'error': 'Stripe payment failed'}), 400

        # Create order
        new_order = Order(user_id=user_id, total=total)
        db.session.add(new_order)
        db.session.flush()  # Get the order ID before committing

        # for item in cart:
        #     order_item = OrderItem(order_id=new_order.id, quantity=item.quantity)
        #     item.book.stock -= item['quantity']  # Deduct stock
        #     db.session.add(order_item)
        #     new_order.items.append(order_item)

        db.session.commit()

        response = {
            'message': 'Checkout successful',
            'order_id': new_order.id,
            'payment_status': payment_status
        }
        if payment_method == 'zelle':
            response['payment_instructions'] = payment_instructions

        return jsonify(response), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
