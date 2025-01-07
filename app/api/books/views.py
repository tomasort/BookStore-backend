from sqlalchemy import or_
from flask import request, jsonify
from flask import current_app, render_template, request, jsonify, Request
from datetime import datetime
from flask_login import login_required
from app import db
from app.api.models import Book, Author, Genre, Series
from app.api.books import books
from app.api.schemas import BookSchema, AuthorSchema, GenreSchema, SeriesSchema
from app.orders.models import OrderItem
from sqlalchemy import func

book_schema = BookSchema()

# TODO: use longin required for create, update, delete routes


# TODO: let the user add a book with authors. The author should already be created and the user should provide the author's ID
@books.route("", methods=["POST"])
def create_book():
    data = request.json
    try:
        book_data = book_schema.load(data)
        new_book: Book = Book(**book_data)
        db.session.add(new_book)
        db.session.commit()
        return jsonify(
            {"message": "Book created successfully",
                "book_id": new_book.id, "book_title": new_book.title}
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@books.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.json
    book = db.get_or_404(Book, book_id)
    if data is None:
        return jsonify({"error": "No data provided"}), 400
    try:
        # Update fields based on incoming data
        for key, value in book.to_dict().items():
            if "date" in key:
                setattr(book, key, datetime.strptime(
                    data.get(key, value), "%Y-%m-%d").date())
                continue
            setattr(book, key, data.get(key, value))
        db.session.commit()
        return jsonify({"message": "Book updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@books.route("", methods=["GET"])
def get_books():
    # Extract query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("limit", 10, type=int)

    # Create pagination object
    pagination = db.paginate(
        db.select(Book),
        page=page,
        per_page=per_page,
        max_per_page=100,  # Optional: limit maximum items per page
        error_out=False    # Don't raise 404 when page is out of range
    )

    # Return JSON response with pagination information
    return jsonify({
        "books": [book_schema.dump(book) for book in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    })


@books.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """Retrieve a single book by its ID"""
    book = db.get_or_404(Book, book_id)
    return jsonify(book_schema.dump(book)), 200


@books.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = db.get_or_404(Book, book_id)
    try:
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@books.route('/search', methods=['GET'])
def search_books():
    """Search for books by title, ISBN, author, etc., with pagination."""
    # Get search parameters from the query string
    title = request.args.get('title', type=str)
    isbn = request.args.get('isbn', type=str)
    author_name = request.args.get('author', type=str)
    keyword = request.args.get('keyword', type=str)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    # Build the query
    query = db.select(Book)
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))
    if isbn:
        query = query.filter((Book.isbn_10 == isbn) | (Book.isbn_13 == isbn))
    if author_name:
        query = query.join(Book.authors).filter(Author.name.ilike(f'%{author_name}%'))
    if keyword:
        query = query.join(Book.authors).filter(
            (Book.title.ilike(f'%{keyword}%')) |
            (Book.description.ilike(f'%{keyword}%')) |
            (Author.name.ilike(f'%{keyword}%'))
        )

    # Create pagination object
    pagination = db.paginate(
        query,
        page=page,
        per_page=limit,
        max_per_page=100,  # Optional: limit maximum items per page
        error_out=False    # Don't raise 404 when page is out of range
    )

    # Return JSON response with pagination information
    if not pagination.items:
        return jsonify({"message": "No books found matching the search criteria"}), 404

    return jsonify({
        "books": [book.to_dict() for book in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    })


@books.route('/<int:book_id>/authors', methods=['PUT'])
def add_authors_to_book(book_id):
    """Associate existing authors to a book using author IDs"""
    # Retrieve the book by its ID
    book = db.get_or_404(Book, book_id)

    # Retrieve author IDs from the request body
    author_ids = request.json.get('author_ids')
    if not author_ids or not isinstance(author_ids, list):
        return jsonify({"error": "Invalid or missing 'author_ids' data"}), 400

    try:
        # Fetch authors by their IDs and add them to the book
        authors = Author.query.filter(Author.id.in_(author_ids)).all()
        if not authors:
            return jsonify({"error": "No valid authors found"}), 404

        for author in authors:
            if author not in book.authors:
                book.authors.append(author)
        db.session.commit()
        return jsonify({"message": f"Authors added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@books.route('/<int:book_id>/authors/<int:author_id>', methods=['DELETE'])
def remove_author_from_book(book_id, author_id):
    """Remove an author from a book"""
    # Retrieve the book by its ID
    book = db.get_or_404(Book, book_id)

    # Retrieve the author by their ID
    author = db.get_or_404(Author, author_id)

    try:
        # Remove the author from the book
        book.authors.remove(author)
        db.session.commit()
        return jsonify({"message": f"Author removed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@books.route('/<int:book_id>/genres', methods=['PUT'])
def add_genres_to_book(book_id):
    """Add genres to a book"""
    book = db.get_or_404(Book, book_id)
    genre_ids = request.json.get('genre_ids')
    if not genre_ids or not isinstance(genre_ids, list):
        return jsonify({"error": "Invalid or missing 'genre_ids' data"}), 400
    try:
        genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
        for genre in genres:
            if genre not in book.genres:
                book.genres.append(genre)
        db.session.commit()
        return jsonify({"message": "Genres added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@books.route('/<int:book_id>/genres/<int:genre_id>', methods=['DELETE'])
def remove_genre_from_book(book_id, genre_id):
    """Remove a genre from a book"""
    book = db.get_or_404(Book, book_id)
    genre = db.get_or_404(Genre, genre_id)
    try:
        book.genres.remove(genre)
        db.session.commit()
        return jsonify({"message": "Genre removed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@books.route('/<int:book_id>/series', methods=['PUT'])
def add_series_to_book(book_id):
    """Add series to a book"""
    book = db.get_or_404(Book, book_id)
    data = request.json
    series = data.get("series_id")
    if not series or not isinstance(series, list):
        return jsonify({"error": "Invalid or missing 'series' data"}), 400
    try:
        for s in series:
            book_series = db.get_or_404(Series, s)
            if book_series not in book.series:
                book.series.append(book_series)
        db.session.commit()
        return jsonify({"message": "Series added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@books.route('/<int:book_id>/series/<int:series_id>', methods=['DELETE'])
def remove_series_from_book(book_id, series_id):
    """Remove a series from a book"""
    book = db.get_or_404(Book, book_id)
    series = db.get_or_404(Series, series_id)
    try:
        book.series.remove(series)
        db.session.commit()
        return jsonify({"message": "Series removed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@books.route('/popular', methods=['GET'])
def get_popular_books():
    """Get the most popular books"""
    # Get the top 10 most popular books
    popular_books = db.session.query(Book).join(OrderItem).group_by(OrderItem.book_id).order_by(func.count(OrderItem.book_id).desc()).limit(10).all()
    if not popular_books:
        return jsonify({"message": "No popular books found"}), 404
    return jsonify([book.to_dict() for book in popular_books]), 200
