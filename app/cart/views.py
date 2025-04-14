from app.models import User
from sqlalchemy.exc import SQLAlchemyError
from app.models import Book
from flask import request
from flask import jsonify, session
from app import db
from app.models import Cart, CartItem
from app.schemas import CartSchema, CartItemSchema
from app.cart import cart
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app


cart_schema = CartSchema()


def get_or_create_cart(db_session, flask_session, user_id, logger=None):
    cart = None
    if user_id is not None:
        user_id = int(user_id)
        cart = db_session.query(Cart).filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db_session.add(cart)
            db_session.commit()
    else:
        cart_id = flask_session.get('cart_id')
        if cart_id:
            cart = db_session.query(Cart).filter_by(id=cart_id).first()
        if not cart:
            cart = Cart()
            db_session.add(cart)
            db_session.commit()
            flask_session['cart_id'] = cart.id
    if logger:
        logger.info(f"Cart: {cart}, User ID: {user_id}, Session Cart ID: {flask_session.get('cart_id')}")
    return cart


@cart.route('', methods=['GET'])
@jwt_required(optional=True)
def get_cart():
    user_id = get_jwt_identity()
    cart = None
    if user_id is not None:
        user_id = int(user_id)
        user = db.session.query(User).filter_by(id=user_id).first()
        cart = user.cart
        if cart is None:
            # check if there is a session cart_id
            session_cart_id = session.get('cart_id')
            cart_id = session_cart_id
            if cart_id is not None:
                cart = db.session.query(Cart).filter_by(id=cart_id).first()
            else:
                cart = Cart()
                db.session.add(cart)
            user.cart = cart
    else:
        cart_id = session.get('cart_id')
        if cart_id is not None:
            cart = db.session.query(Cart).filter_by(id=cart_id).first()
        if not cart:
            cart = Cart()
            db.session.add(cart)
            session['cart_id'] = cart.id
    db.session.commit()
    if cart:
        return jsonify(cart_schema.dump(cart)), 200
    current_app.logger.info(f"Cart not found for user ID: {user_id}")
    return jsonify({"message": "Cart not found"}), 404


@cart.route('/add', methods=['POST'])
@jwt_required(optional=True)
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()

    book_id = data.get('book_id')
    quantity = data.get('quantity', 1)  # Default quantity to 1 if not provided

    if not book_id:
        return jsonify({"message": "Book ID is required"}), 400
    if quantity <= 0:
        return jsonify({"message": "Quantity must be greater than zero"}), 400

    try:
        # Check if item exists
        book = db.session.query(Book).filter_by(id=book_id).first()
        if not book:
            return jsonify({"message": "Book not found"}), 404

        # Retrieve or create the cart
        cart = get_or_create_cart(db.session, session, user_id, current_app.logger)

        # Check if item is already in the cart
        cart_item = db.session.query(CartItem).filter_by(cart_id=cart.id, book_id=book_id).first()
        if cart_item:
            cart_item.quantity += quantity  # Update the quantity
        else:
            cart_item = CartItem(cart_id=cart.id, book=book, quantity=quantity)
            db.session.add(cart_item)

        db.session.commit()

        return jsonify({"message": "Item added to cart", "cart": cart_schema.dump(cart)}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@cart.route('/update', methods=['PUT'])
@jwt_required(optional=True)
def update_cart():
    user_id = get_jwt_identity()
    data = request.get_json()

    book_id = data.get('book_id')
    quantity = data.get('quantity', 0)
    try:
        # Check if item exists
        book = db.session.query(Book).filter_by(id=book_id).first()
        if not book:
            return jsonify({"message": "Book not found"}), 404
        # Retrieve or create the cart
        cart = get_or_create_cart(db.session, session, user_id)

        # Check if item is already in the cart
        cart_item = db.session.query(CartItem).filter_by(cart_id=cart.id, book_id=book_id).first()
        if cart_item:
            if quantity > 0:
                cart_item.quantity = quantity
            else:
                db.session.delete(cart_item)
        else:
            cart_item = CartItem(cart_id=cart.id, book=book, quantity=quantity)
            db.session.add(cart_item)

        db.session.commit()

        return jsonify({"message": "Item added to cart", "cart": cart_schema.dump(cart)}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@cart.route('/remove', methods=['PUT'])
@jwt_required(optional=True)
def remove_from_cart():
    user_id = get_jwt_identity()
    data = request.get_json()

    book_id = data.get('book_id')

    if not book_id:
        return jsonify({"message": "Book ID is required"}), 400
    cart = get_or_create_cart(db.session, session, user_id, current_app.logger)
    cart_item = db.session.query(CartItem).filter_by(cart_id=cart.id, book_id=book_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Item removed from cart", "cart": cart_schema.dump(cart)}), 200
    else:
        return jsonify({"message": "Item not found in cart"}), 404


@cart.route('', methods=['DELETE'])
@jwt_required(optional=True)
def delete_cart():
    user_id = get_jwt_identity()
    cart = get_or_create_cart(db.session, session, user_id)
    cart_items = db.session.query(CartItem).filter_by(cart_id=cart.id).all()
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.delete(cart)
    db.session.commit()
    return jsonify({"message": "Cart deleted"}), 200
