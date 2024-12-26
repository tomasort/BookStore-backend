from app.auth import auth
from app import db
from app.auth.models import User
from app.auth.schemas import UserSchema
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from marshmallow import ValidationError

user_schema = UserSchema()


@auth.route('/users', methods=['POST'])
def create_user():
    data = request.json
    try:
        # Validate and deserialize input data
        user_data = user_schema.load(data)

        # Create a new user instance
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully", "user_id": new_user.id}), 201

    except ValidationError as ve:
        # Catch validation errors from Marshmallow
        db.session.rollback()
        return jsonify({"error": "Validation failed", "details": ve.messages}), 400
    except IntegrityError as ie:
        # Handle database integrity errors (e.g., unique constraint violations)
        db.session.rollback()
        error_message = str(ie.orig)  # Get the original DB error message

        # More specific error message checking
        if "user.username" in error_message.lower():
            return jsonify({"error": "Username is already taken"}), 400
        elif "user.email" in error_message.lower():
            return jsonify({"error": "Email is already taken"}), 400

        return jsonify({
            "error": "Database integrity error",
            "details": "A unique constraint was violated"
        }), 400

    except Exception as e:
        # Rollback session for any other exception
        db.session.rollback()
        # Log the actual error for debugging
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    finally:
        db.session.close()

    # except IntegrityError as ie:
    #     # Handle database integrity errors (e.g., unique constraint violations)
    #     db.session.rollback()
    #     error_message = str(ie.orig)  # Get the original DB error message

    #     # More specific error message checking
    #     if "user.username" in error_message.lower():
    #         return jsonify({"error": "Username is already taken"}), 400
    #     elif "user.email" in error_message.lower():
    #         return jsonify({"error": "Email is already taken"}), 400

    #     # Log the actual error message for debugging
    #     print(f"IntegrityError: {error_message}")

    #     return jsonify({
    #         "error": "Database integrity error",
    #         "details": "A unique constraint was violated"
    #     }), 400

    # except Exception as e:
    #     # Rollback session for any other exception
    #     db.session.rollback()
    #     # Log the actual error for debugging
    #     print(f"Unexpected error: {str(e)}")
    #     return jsonify({"error": "An unexpected error occurred"}), 500


@auth.route('/users', methods=['GET'])
def get_users():
    users = db.session.execute(db.select(User)).scalars().all()
    serialized_users = user_schema.dump(users, many=True)
    return jsonify(serialized_users)


# @auth.route('/users/<int:user_id>', methods=['GET'])
# def get_user(user_id):
#     return f'Get user with id {user_id}'


# @auth.route('/users/<int:user_id>', methods=['PUT'])
# def update_user(user_id):
#     return f'Update user with id {user_id}'
