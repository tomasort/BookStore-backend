from flask import current_app, render_template, request, jsonify, Request
from datetime import datetime
from flask_login import login_required
from app import db
from app.api.models import Book, Author, Genre, Series
from app.api.books import books


# TODO: use longin required for create, update, delete routes

@books.route("", methods=["POST"])
def create_book():
    data = request.json
    try:
        new_book: Book = Book(
            title=data.get("title", None),
            isbn_10=data.get("isbn_10"),
            isbn_13=data.get("isbn_13"),
            publish_date=datetime.strptime(
                data.get("publish_date"), "%Y-%m-%d").date(),
            description=data.get("description"),
            author_id=data.get("author_id"),
            cover_url=data.get("cover_url"),
            current_price=data.get("current_price"),
            previous_price=data.get("previous_price"),
            physical_format=data.get("physical_format"),
            number_of_pages=data.get("number_of_pages"),
            editorial=data.get("editorial"),
            alejandria_isbn=data.get("alejandria_isbn"),
            physical_dimensions=data.get("physical_dimensions"),
            weight=data.get("weight"),
            publish_place=data.get("publish_place"),
            edition_name=data.get("edition_name"),
            subtitle=data.get("subtitle"),
        )
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
        book.title = data.get("title", book.title)
        book.isbn_10 = data.get("isbn_10", book.isbn_10)
        book.isbn_13 = data.get("isbn_13", book.isbn_13)
        book.publish_date = data.get("publish_date", book.publish_date)
        book.description = data.get("description", book.description)
        book.author_id = data.get("author_id", book.author_id)
        book.cover_url = data.get("cover_url", book.cover_url)
        book.current_price = data.get("current_price", book.current_price)
        book.previous_price = data.get("previous_price", book.previous_price)
        book.physical_format = data.get(
            "physical_format", book.physical_format)
        book.number_of_pages = data.get(
            "number_of_pages", book.number_of_pages)
        book.editorial = data.get("editorial", book.editorial)
        book.alejandria_isbn = data.get(
            "alejandria_isbn", book.alejandria_isbn)
        book.publisher_id = data.get("publisher_id", book.publisher_id)
        book.physical_dimensions = data.get(
            "physical_dimensions", book.physical_dimensions
        )
        book.weight = data.get("weight", book.weight)
        book.publish_place = data.get("publish_place", book.publish_place)
        book.edition_name = data.get("edition_name", book.edition_name)
        book.subtitle = data.get("subtitle", book.subtitle)

        db.session.commit()
        return jsonify({"message": "Book updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@books.route("", methods=["GET"])
def get_books():
    # TODO: implement query parameters for page, limit, author, genre, language, publisher, series, search, sort
    books = db.session.execute(db.select(Book)).scalars()
    return jsonify(
        [
            {
                "id": book.id,
                "title": book.title,
                "isbn_10": book.isbn_10,
                "isbn_13": book.isbn_13,
                "publish_date": book.publish_date,
                "description": book.description,
                "author_id": book.author_id,
                "cover_url": book.cover_url,
                "current_price": book.current_price,
                "previous_price": book.previous_price,
                "physical_format": book.physical_format,
                "number_of_pages": book.number_of_pages,
                "editorial": book.editorial,
                "alejandria_isbn": book.alejandria_isbn,
                "publisher_id": book.publisher_id,
                "physical_dimensions": book.physical_dimensions,
                "weight": book.weight,
                "publish_place": book.publish_place,
                "edition_name": book.edition_name,
                "subtitle": book.subtitle,
            }
            for book in books
        ]
    )


@books.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """Retrieve a single book by its ID"""
    book = db.get_or_404(Book, book_id)
    return jsonify(
        {
            "id": book.id,
            "title": book.title,
            "isbn_10": book.isbn_10,
            "isbn_13": book.isbn_13,
            "publish_date": book.publish_date,
            "description": book.description,
            "author_id": book.author_id,
            "cover_url": book.cover_url,
            "current_price": book.current_price,
            "previous_price": book.previous_price,
            "physical_format": book.physical_format,
            "number_of_pages": book.number_of_pages,
            "editorial": book.editorial,
            "alejandria_isbn": book.alejandria_isbn,
            "publisher_id": book.publisher_id,
            "physical_dimensions": book.physical_dimensions,
            "weight": book.weight,
            "publish_place": book.publish_place,
            "edition_name": book.edition_name,
            "subtitle": book.subtitle,
            "authors": [{"id": author.id, "name": author.name} for author in book.authors],
        }
    )


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
    """Search for books by title, ISBN, author, etc."""
    # Get search parameters from the query string
    title = request.args.get('title', type=str)
    isbn = request.args.get('isbn', type=str)
    author_name = request.args.get('author', type=str)
    query = db.session.query(Book)
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))
    if isbn:
        query = query.filter((Book.isbn_10 == isbn) | (Book.isbn_13 == isbn))
    if author_name:
        query = query.join(Author).filter(
            Author.name.ilike(f'%{author_name}%'))
    books = query.all()
    # serialize the results
    results = []
    for book in books:
        results.append({
            "id": book.id,
            "title": book.title,
            "isbn_10": book.isbn_10,
            "isbn_13": book.isbn_13,
            "publish_date": book.publish_date,
            "description": book.description,
            "author_id": book.author_id,
            "cover_url": book.cover_url,
            "current_price": book.current_price,
            "previous_price": book.previous_price,
            "physical_format": book.physical_format,
            "number_of_pages": book.number_of_pages,
            "editorial": book.editorial,
            "alejandria_isbn": book.alejandria_isbn,
            "publisher_id": book.publisher_id,
            "physical_dimensions": book.physical_dimensions,
            "weight": book.weight,
            "publish_place": book.publish_place,
            "edition_name": book.edition_name,
            "subtitle": book.subtitle,
        })
    if not books:
        return jsonify({"message": "No books found matching the search criteria"}), 404
    return jsonify(results)


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
