import pdb
from flask import jsonify, request
from app.models import Review, Book
from app.schemas import ReviewSchema
from app import db
from app.api.reviews import reviews
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies
from flask_wtf.csrf import generate_csrf


@reviews.route('', methods=['GET'])
def get_reviews():
    all_reviews = db.session.query(Review).all()
    reviews_schema = ReviewSchema(many=True)
    return jsonify(reviews_schema.dump(all_reviews)), 200


@reviews.route('/<int:book_id>', methods=['GET'])
def get_reviews_for_book(book_id):
    book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    reviews = book.reviews
    reviews_schema = ReviewSchema(many=True)
    return jsonify(reviews_schema.dump(reviews)), 200


@reviews.route('/<int:book_id>', methods=['POST'])
@jwt_required()
def add_review(book_id):
    book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    user_id = get_jwt_identity()
    user_review = db.session.query(Review).filter_by(user_id=user_id, book_id=book_id).first()
    if user_review:
        return jsonify({'message': 'You have already reviewed this book'}), 400
    data = request.json
    comment = data.get('comment')
    rating = data.get('rating')
    if not comment or not rating:
        return jsonify({'message': 'Comment and rating are required'}), 400
    review_schema = ReviewSchema()
    review_data = review_schema.load({
        'comment': comment,
        'rating': rating,
        'book_id': book_id,
        'user_id': int(user_id)
    })
    review = Review(**review_data)
    db.session.add(review)
    book.reviews.append(review)
    db.session.commit()
    return jsonify({'message': 'Review added successfully'}), 201


@reviews.route('/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_review(book_id):
    book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    user_id = get_jwt_identity()
    review = db.session.query(Review).filter_by(user_id=user_id, book_id=book_id).first()
    if not review:
        return jsonify({'message': 'Review not found'}), 404
    data = request.json
    comment = data.get('comment', review.comment)
    rating = data.get('rating', review.rating)
    review.comment = comment
    review.rating = rating
    db.session.commit()
    return jsonify({'message': 'Review updated successfully'}), 200


@reviews.route('/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_review(book_id):
    book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    user_id = get_jwt_identity()
    review = db.session.query(Review).filter_by(user_id=user_id, book_id=book_id).first()
    if not review:
        return jsonify({'message': 'Review not found'}), 404
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted successfully'}), 200
