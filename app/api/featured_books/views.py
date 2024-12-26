from flask import jsonify, request
from datetime import datetime
from app import db
from app.api.models import FeaturedBook, Book
from app.api.schemas import FeaturedBookSchema
from app.api.featured_books import featured_books

featured_book_schema = FeaturedBookSchema()


@featured_books.route('', methods=['POST'])
def create_featured_book():
    """Create a new featured_book"""
    data = request.get_json()
    try:
        featured_book_data = featured_book_schema.load(data)
        book = None
        book_id = featured_book_data['book_id']
        if db.session.execute(db.select(FeaturedBook).filter_by(book_id=book_id)).scalar() is not None:
            return jsonify({'error': 'FeaturedBook with this book_id already exists'}), 400
        # find the book with that id and add it as book
        book = db.get_or_404(Book, book_id)
        featured_book = FeaturedBook(**featured_book_data)
        featured_book.book = book
        db.session.add(featured_book)
        db.session.commit()
        return jsonify({"message": "FeaturedBook created successfully",
                        "featured_book_id": featured_book.id}), 201
    except KeyError:
        return jsonify({'error': 'Invalid featured book data'}), 400


@featured_books.route('', methods=['GET'])
def get_featured_books():
    """Retrieve a list of featured_books with filtering, pagination, and sorting"""
    # TODO: get only the featured_books that are not expired
    featured_books = db.session.execute(db.select(FeaturedBook)).scalars()
    return jsonify([featured_book_schema.dump(featured_book) for featured_book in featured_books])


@featured_books.route('/<int:featured_book_id>', methods=['GET'])
def get_featured_book(featured_book_id):
    """Retrieve a single featured_book by its ID"""
    featured_book = db.session.execute(db.select(FeaturedBook).filter_by(id=featured_book_id)).scalar()
    if featured_book is None:
        return jsonify({'error': 'FeaturedBook not found'}), 404
    return jsonify(featured_book_schema.dump(featured_book)), 200


@featured_books.route('/<int:featured_book_id>', methods=['PUT'])
def update_featured_book(featured_book_id):
    """Update a featured_book by its ID"""
    featured_book = db.session.execute(db.select(FeaturedBook).filter_by(id=featured_book_id)).scalar()
    if featured_book is None:
        return jsonify({'error': 'FeaturedBook not found'}), 404
    data = request.get_json()
    try:
        # featured_book.book_id = data.get('book_id', featured_book.book_id)
        if 'book_id' in data:
            # we need to find the book with that id and add it as book
            book = db.get_or_404(Book, data['book_id'])
            featured_book.book = book
        if 'expiry_date' in data:
            featured_book.expiry_date = datetime.strptime(data['expiry_date'], "%Y-%m-%d").date()
        featured_book.priority = data.get('priority', featured_book.priority)
        db.session.commit()
        return jsonify({"message": "FeaturedBook updated successfully"}), 200
    except KeyError:
        return jsonify({'error': 'Invalid featured_book data'}), 400


@featured_books.route('/<int:featured_book_id>', methods=['DELETE'])
def delete_featured_book(featured_book_id):
    """Delete a featured_book by its ID"""
    featured_book = db.session.execute(db.select(FeaturedBook).filter_by(id=featured_book_id)).scalar()
    if featured_book is None:
        return jsonify({'error': 'FeaturedBook not found'}), 404
    db.session.delete(featured_book)
    db.session.commit()
    return jsonify({"message": "FeaturedBook deleted successfully"}), 200
