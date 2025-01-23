from app.auth import auth
from flask import session
from app import db, admin_required
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies
from flask_wtf.csrf import generate_csrf
from app.models import Book
from app.models import User
from app.schemas import UserSchema


user_schema = UserSchema()


@auth.route('/users', methods=['POST'])
def register_user():
    data = request.json
    # Ensure required fields are provided
    for field in ['username', 'password', 'email']:
        if field not in data:
            return jsonify({"error": f"{field.capitalize()} is required"}), 400
    try:
        # Validate and deserialize input data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        new_user = User(username=username, email=email)

        # Set the password using the hashing function
        new_user.set_password(password)

        # Add and commit the new user
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "User created successfully",
            "user_id": new_user.id
        }), 201

    except IntegrityError as ie:
        db.session.rollback()
        error_message = str(ie.orig)

        if "user.username" in error_message.lower():
            return jsonify({"error": "Username is already taken"}), 400
        elif "user.email" in error_message.lower():
            return jsonify({"error": "Email is already taken"}), 400

        return jsonify({
            "error": "Database integrity error",
            "details": "A unique constraint was violated"
        }), 400

    except Exception as e:
        db.session.rollback()
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

    finally:
        db.session.close()


@auth.route('/users', methods=['GET'])
@admin_required()
def get_users():
    users = db.session.execute(db.select(User)).scalars().all()
    serialized_users = user_schema.dump(users, many=True)
    return jsonify(serialized_users)


@auth.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user = int(get_jwt_identity())
    if user_id != current_user:
        return jsonify({"error": "You can't access this user's information!"}), 403
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    if user is None:
        return jsonify({"error": "User not found"}), 405

    serialized_user = user_schema.dump(user)
    return jsonify(serialized_user)


@auth.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.json
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    current_user = get_jwt_identity()
    if user_id != int(current_user):
        return jsonify({"error": "You are not authorized to perform this action"}), 403
    schema = UserSchema(only=['first_name', 'last_name', 'phone_number', 'email', 'username', 'shipping_address', 'shipping_city', 'shipping_state', 'shipping_country', 'shipping_postal_code'])
    update_data = schema.load({
        'first_name': data.get('first_name', user.first_name),
        'last_name': data.get('last_name', user.last_name),
        'phone_number': data.get('phone_number', user.phone_number),
        'email': data.get('email', user.email),
        'username': data.get('username', user.username),
        'shipping_address': data.get('shipping_address', user.shipping_address),
        'shipping_city': data.get('shipping_city', user.shipping_city),
        'shipping_state': data.get('shipping_state', user.shipping_state),
        'shipping_country': data.get('shipping_country', user.shipping_country),
        'shipping_postal_code': data.get('shipping_postal_code', user.shipping_postal_code)
    })
    for key, value in update_data.items():
        setattr(user, key, value)
    db.session.commit()
    return jsonify({"message": "User updated successfully"})


@auth.route('/users/<int:user_id>/password', methods=['PUT'])
@jwt_required()
def update_user_password(user_id):
    data = request.json
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    current_user = get_jwt_identity()
    if user_id != int(current_user):
        return jsonify({"error": "You are not authorized to perform this action"}), 403
    if 'current_password' not in data:
        return jsonify({"error": "Current password is required"}), 400
    if not user.check_password(data['current_password']):
        return jsonify({"error": "Current password is incorrect"}), 400
    if user.check_password(data['new_password']):
        return jsonify({"error": "New password cannot be the same as the current password"}), 400
    if 'new_password' in data:
        user.set_password(data['new_password'])
    else:
        return jsonify({"error": "New password is required"}), 400
    db.session.commit()
    return jsonify({"message": "User password updated successfully"})


@auth.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})


@auth.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_schema.dump(user)['favorites'])


@auth.route('/users/<int:user_id>/favorites', methods=['POST'])
@jwt_required()
def add_user_favorite(user_id):
    # check if the user exists
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    # check that the user is the same as the one making the request
    current_user = get_jwt_identity()
    if user_id != int(current_user):
        return jsonify({"error": "You are not authorized to perform this action"}), 403
    data = request.json
    book_id = data.get('book_id')
    if book_id is None:
        return jsonify({"error": "Book ID is required"}), 400
    # check if the book exists
    book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    # check if the book is already in the user's favorites
    if book in user.favorites:
        return jsonify({"error": "Book is already in favorites"}), 400
    user.favorites.append(book)
    db.session.commit()
    return jsonify({"message": "Book added to favorites successfully"}), 201


@auth.route('/users/<int:user_id>/wishlist', methods=['GET'])
@jwt_required()
def get_user_wishlist(user_id):
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_schema.dump(user)['wishlist'])


@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = db.session.execute(db.select(User).where(User.username == username)).scalar()
    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401
    # Generate and set CSRF token after successful login
    # csrf_token = generate_csrf()
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    response = jsonify({"message": "Login successful", "user_id": user.id})
    set_access_cookies(response, access_token)
    # response.headers['X-CSRF-Token'] = csrf_token
    user.last_login = db.func.now()
    return response, 200


@auth.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def logout():
    # Expire/remove the JWT cookies
    response = jsonify({"message": "Successfully logged out"})
    response.set_cookie('access_token_cookie', '', expires=0)
    response.set_cookie('csrf_access_token', '', expires=0)
    session.clear()
    return response, 200


# TODO: we might have to refactor this so that the user routes are in a separate file


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@auth.route("/protected", methods=["GET"])
@admin_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@auth.route('/get-csrf-token', methods=['GET'])
@jwt_required()
def get_csrf_token():
    token = generate_csrf()
    response = jsonify({'msg': 'CSRF token generated'})
    response.headers['X-CSRF-Token'] = token
    return response
