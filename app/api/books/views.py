from urllib.parse import unquote
from sqlalchemy import or_
from marshmallow.exceptions import ValidationError
from flask import request, jsonify
from flask import current_app, render_template, request, jsonify, Request
from datetime import datetime
from flask_login import login_required
from app import db
from app.models import Book, Author, Genre, Series
from app.api.books import books
from app.schemas import BookSchema, AuthorSchema
from app.models import OrderItem
from sqlalchemy import func, case

book_schema = BookSchema()


# TODO: use longin required for create, update, delete routes


# TODO: let the user add a book with authors. The author should already be created and the user should provide the author's ID
@books.route("", methods=["POST"])
def create_book():
    data = request.json
    try:
        book_data = BookSchema().load(data)
        print(book_data)
        new_book: Book = Book(**book_data)
        db.session.add(new_book)
        db.session.commit()
        return jsonify(
            {"message": "Book created successfully", "book_id": new_book.id, "book_title": new_book.title}
        ), 201
    except ValidationError as err:
        db.session.rollback()
        return jsonify({"error": "Validation error", "details": err.messages}), 400
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
        validated_data = BookSchema().load(data, partial=True)
        # Update book object with validated data
        for key, value in validated_data.items():
            setattr(book, key, value)
        db.session.commit()
        return jsonify({"message": "Book updated successfully"}), 200
    except ValidationError as err:
        db.session.rollback()
        return jsonify({"error": "Validation error", "details": err.messages}), 400
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

    simple_book_schema = BookSchema(only=["id", "title", "subtitle", "isbn_10", "isbn_13", "authors", "series", "genres", "publishers", "current_price", "cover_url", "previous_price", "rating"])

    # Return JSON response with pagination information
    return jsonify({
        "books": [simple_book_schema.dump(book) for book in pagination.items],
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
    keywords = request.args.get('q', '', type=str)

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    # sort_by = request.args.get('sort_by', 'relevance', type=str)

    current_app.logger.info(f"Searching for books with title: {title}, ISBN: {isbn}, author: {author_name}, query: {keywords}")

    # Build the query
    query = db.select(Book)
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))
    if isbn:
        query = query.filter((Book.isbn_10 == isbn) | (Book.isbn_13 == isbn))
    if author_name:
        query = query.join(Book.authors).filter(Author.name.ilike(f'%{author_name}%'))
    if keywords:
        query = query.join(Book.authors).filter(
            (Book.title.ilike(f'%{keywords}%')) |
            (Book.description.ilike(f'%{keywords}%')) |
            (Author.name.ilike(f'%{keywords}%'))
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


@books.route('/suggestions', methods=['GET'])
def suggestions():
    query = request.args.get('q', '')
    if not query or len(query) < 2:  # Require at least 2 characters to search
        return jsonify({
            'books': [],
            'authors': []
        })

    # Search for books
    books = suggest_books(query)

    # Search for authors
    authors = suggest_authors(query)

    return jsonify({
        'books': books,
        'authors': authors
    })


def suggest_books(query):
    # Create a search pattern with wildcards for partial matches
    search_pattern = f"%{query}%"

    # Search in multiple fields with relevance scoring
    book_results = db.session.query(
        Book,
        # Calculate relevance score
        (
            # Exact ISBN matches get highest score (10)
            func.cast(Book.isbn_10 == query, db.Integer) * 10 +
            func.cast(Book.isbn_13 == query, db.Integer) * 10 +
            # Exact title matches get highest score (10)
            func.cast(func.lower(Book.title) == query.lower(), db.Integer) * 10 +
            # Title starts with query gets high score (5)
            func.cast(func.lower(Book.title).like(f"{query.lower()}%"), db.Integer) * 5 +
            # Title contains query gets medium score (3)
            func.cast(func.lower(Book.title).like(search_pattern), db.Integer) * 3
        ).label('relevance_score')
    ).filter(
        or_(
            func.lower(Book.title).like(search_pattern),
            Book.isbn_10.like(search_pattern),
            Book.isbn_13.like(search_pattern),
        )
    ).order_by(
        # Order by relevance score (descending)
        db.desc('relevance_score')
    ).limit(10).all()  # Limit to 10 results for performance

    # Format the results
    return [{**BookSchema(only=["id", "title", "cover_url"]).dump(book), 'score': score} for book, score in book_results]


def suggest_authors(query):
    search_pattern = f"%{query}%"

    author_results = db.session.query(
        Author,
        # Calculate relevance score
        (
            # Exact name matches get highest score (10)
            func.cast(func.lower(Author.name) == query.lower(), db.Integer) * 11 +
            # Name starts with query gets high score (5)
            func.cast(func.lower(Author.name).like(f"{query.lower()}%"), db.Integer) * 5 +
            # Name contains query gets medium score (3)
            func.cast(func.lower(Author.name).like(search_pattern), db.Integer) * 3
        ).label('relevance_score')
    ).filter(
        func.lower(Author.name).like(search_pattern)
    ).order_by(
        db.desc('relevance_score')
    ).limit(5).all()  # Limit to 5 author results

    return [{**AuthorSchema(only=["id", "name", "photo_url"]).dump(author), 'score': score}for author, score in author_results]


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
    return jsonify([book_schema.dump(book) for book in popular_books]), 200


@books.route('/related/<int:book_id>', methods=['GET'])
def get_related_books(book_id):
    """
    Get books related to the book with the given ID.

    Returns books sorted by relevance based on shared authors and genres.
    Authors are weighted more heavily than genres.
    """
    try:
        # Get pagination parameters with defaults
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Get the source book
        book = db.get_or_404(Book, book_id)

        # Extract authors and genres
        author_names = [author.name for author in book.authors or []]
        genre_names = [genre.name for genre in book.genres or []]

        if not author_names and not genre_names:
            return jsonify({"message": "Source book has no authors or genres to match", "data": []}), 200

        # Fixed case() syntax for newer SQLAlchemy versions
        # Define the scoring expressions
        author_score = func.sum(case((Author.name.in_(author_names), 3), else_=0))
        genre_score = func.sum(case((Genre.name.in_(genre_names), 1), else_=0))

        total_score = (author_score + genre_score).label('relevance_score')

        # Build and execute query
        query = db.session.query(Book, total_score).outerjoin(Book.authors).outerjoin(Book.genres)

        # Filter books with matching authors or genres, excluding the original book
        query = query.filter(
            (Book.id != book_id) &  # Exclude the original book
            ((Author.name.in_(author_names)) | (Genre.name.in_(genre_names)))
        ).group_by(Book.id).order_by(total_score.desc())

        # Add pagination
        paginated_results = query.paginate(page=page, per_page=per_page)

        # Extract books from the paginated query result
        books = [book for book, _ in paginated_results.items]

        # Prepare response with pagination metadata
        response = {
            "books": [book_schema.dump(b) for b in books],
            "pagination": {
                "total": paginated_results.total,
                "pages": paginated_results.pages,
                "page": page,
                "per_page": per_page,
                "has_next": paginated_results.has_next,
                "has_prev": paginated_results.has_prev
            }
        }

        return jsonify(response), 200

    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f"Error finding related books: {str(e)}")
        return jsonify({"message": "Failed to retrieve related books"}), 500
