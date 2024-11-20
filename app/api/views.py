from flask import current_app, render_template, request, jsonify, Request
from datetime import datetime
from flask_login import login_required
from app.api import api
from app import db
from app.api.models import Book, Author, Genre, Language, Series


# ----------- BOOK ROUTES ----------- #

# TODO: use longin required for create, update, delete routes

@api.route("/books", methods=["POST"])
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


@api.route("/books/<int:book_id>", methods=["PUT"])
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


@api.route("/books", methods=["GET"])
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


@api.route("/books/<int:book_id>", methods=["GET"])
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


@api.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = db.get_or_404(Book, book_id)
    try:
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@api.route('/books/search', methods=['GET'])
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


@api.route('/books/<int:book_id>/authors', methods=['POST'])
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


# # TODO: remove author to a book
# @api.route('/books/<int:book_id>/authors/<int:author_id>', methods=['DELETE'])
# def remove_author_from_book(book_id, author_id):
#     """Remove an author from a book"""
#     # Code to handle removing an author from a book
#     pass


# # TODO: add genre to a book
# @api.route('/books/<int:book_id>/genres', methods=['POST'])
# def add_genres_to_book(book_id):
#     """Add genres to a book"""
#     # Code to handle adding genres to a book
#     pass


# # TODO: add remove to a book
# @api.route('/books/<int:book_id>/genres/<int:genre_id>', methods=['DELETE'])
# def remove_genre_from_book(book_id, genre_id):
#     """Remove a genre from a book"""
#     # Code to handle removing a genre from a book
#     pass


# # TODO: add series to a book
# @api.route('/books/<int:book_id>/series', methods=['POST'])
# def add_series_to_book(book_id):
#     """Add series to a book"""
#     # Code to handle adding series to a book
#     pass


# # TODO: remove series to a book
# @api.route('/books/<int:book_id>/series/<int:series_id>', methods=['DELETE'])
# def remove_series_from_book(book_id, series_id):
#     """Remove a series from a book"""
#     # Code to handle removing a series from a book
#     pass


# # ----------- AUTHOR ROUTES -----------

@api.route('/authors', methods=['POST'])
def create_author():
    """Create a new author"""
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "Author 'name' is required"}), 400

    author = Author(
        name=name,
        birth_date=datetime.strptime(
            data.get("birth_date"), "%Y-%m-%d").date() if "birth_date" in data else None,
        death_date=datetime.strptime(
            data.get("death_date"), "%Y-%m-%d").date() if "death_date" in data else None,
        biography=data.get("biography")
    )
    try:
        db.session.add(author)
        db.session.commit()
        return jsonify({"author_id": author.id, "message": "Author created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# @api.route('/authors', methods=['GET'])
# def get_authors():
#     """Retrieve a list of authors with filtering, pagination, and sorting"""
#     # Code to handle retrieving authors
#     pass


# @api.route('/authors/<int:author_id>', methods=['GET'])
# def get_author(author_id):
#     """Retrieve a single author by its ID"""
#     # Code to handle retrieving an author by ID
#     pass


# @api.route('/authors/<int:author_id>', methods=['PUT'])
# def update_author(author_id):
#     """Update an author by its ID"""
#     # Code to handle updating an author by ID
#     pass


# @api.route('/authors/<int:author_id>', methods=['DELETE'])
# def delete_author(author_id):
#     """Delete an author by its ID"""
#     # Code to handle deleting an author by ID
#     pass


# @api.route('/authors/<int:author_id>/books', methods=['GET'])
# def get_books_by_author(author_id):
#     """Get all books by a specific author"""
#     # Code to handle retrieving all books by a given author
#     pass

# # ----------- GENRE ROUTES ----------- #


# @api.route('/genres', methods=['POST'])
# def create_genre():
#     """Create a new genre"""
#     # Code to handle creating a genre
#     pass


# @api.route('/genres', methods=['GET'])
# def get_genres():
#     """Retrieve a list of genres with filtering, pagination, and sorting"""
#     # Code to handle retrieving genres
#     pass


# @api.route('/genres/<int:genre_id>', methods=['GET'])
# def get_genre(genre_id):
#     """Retrieve a single genre by its ID"""
#     # Code to handle retrieving a genre by ID
#     pass


# @api.route('/genres/<int:genre_id>', methods=['PUT'])
# def update_genre(genre_id):
#     """Update a genre by its ID"""
#     # Code to handle updating a genre by ID
#     pass


# @api.route('/genres/<int:genre_id>', methods=['DELETE'])
# def delete_genre(genre_id):
#     """Delete a genre by its ID"""
#     # Code to handle deleting a genre by ID
#     pass


# # ----------- GENRE'S BOOKS ROUTE ----------- #

# @api.route('/genres/<int:genre_id>/books', methods=['GET'])
# def get_books_by_genre(genre_id):
#     """Get all books that belong to a specific genre"""
#     # Code to handle retrieving all books associated with a given genre
#     pass

# # ----------- PUBLISHER ROUTES ----------- #


# @api.route('/publishers', methods=['POST'])
# def create_publisher():
#     """Create a new publisher"""
#     # Code to handle creating a publisher
#     pass


# @api.route('/publishers', methods=['GET'])
# def get_publishers():
#     """Retrieve a list of publishers with filtering, pagination, and sorting"""
#     # Code to handle retrieving publishers
#     pass


# @api.route('/publishers/<int:publisher_id>', methods=['GET'])
# def get_publisher(publisher_id):
#     """Retrieve a single publisher by its ID"""
#     # Code to handle retrieving a publisher by ID
#     pass


# @api.route('/publishers/<int:publisher_id>', methods=['PUT'])
# def update_publisher(publisher_id):
#     """Update a publisher by its ID"""
#     # Code to handle updating a publisher by ID
#     pass


# @api.route('/publishers/<int:publisher_id>', methods=['DELETE'])
# def delete_publisher(publisher_id):
#     """Delete a publisher by its ID"""
#     # Code to handle deleting a publisher by ID
#     pass


# # ----------- PUBLISHER'S BOOKS ROUTE ----------- #

# @api.route('/publishers/<int:publisher_id>/books', methods=['GET'])
# def get_books_by_publisher(publisher_id):
#     """Get all books published by a specific publisher"""
#     # Code to handle retrieving all books by a given publisher
#     pass

# # ----------- SERIES ROUTES ----------- #


# @api.route('/series', methods=['POST'])
# def create_series():
#     """Create a new series"""
#     # Code to handle creating a series
#     pass


# @api.route('/series', methods=['GET'])
# def get_series():
#     """Retrieve a list of series with filtering, pagination, and sorting"""
#     # Code to handle retrieving series
#     pass


# @api.route('/series/<int:series_id>', methods=['GET'])
# def get_single_series(series_id):
#     """Retrieve a single series by its ID"""
#     # Code to handle retrieving a series by ID
#     pass


# @api.route('/series/<int:series_id>', methods=['PUT'])
# def update_series(series_id):
#     """Update a series by its ID"""
#     # Code to handle updating a series by ID
#     pass


# @api.route('/series/<int:series_id>', methods=['DELETE'])
# def delete_series(series_id):
#     """Delete a series by its ID"""
#     # Code to handle deleting a series by ID
#     pass


# # ----------- SERIES' BOOKS ROUTE ----------- #

# @api.route('/series/<int:series_id>/books', methods=['GET'])
# def get_books_by_series(series_id):
#     """Get all books that belong to a specific series"""
#     # Code to handle retrieving all books in a given series
#     pass

# # ----------- LANGUAGE ROUTES ----------- #


# @api.route('/languages', methods=['POST'])
# def create_language():
#     """Create a new language"""
#     # Code to handle creating a language
#     pass


# @api.route('/languages', methods=['GET'])
# def get_languages():
#     """Retrieve a list of languages with filtering, pagination, and sorting"""
#     # Code to handle retrieving languages
#     pass


# @api.route('/languages/<int:language_id>', methods=['GET'])
# def get_language(language_id):
#     """Retrieve a single language by its ID"""
#     # Code to handle retrieving a language by ID
#     pass


# @api.route('/languages/<int:language_id>', methods=['PUT'])
# def update_language(language_id):
#     """Update a language by its ID"""
#     # Code to handle updating a language by ID
#     pass


# @api.route('/languages/<int:language_id>', methods=['DELETE'])
# def delete_language(language_id):
#     """Delete a language by its ID"""
#     # Code to handle deleting a language by ID
#     pass


# # ----------- LANGUAGE'S BOOKS ROUTE ----------- #

# @api.route('/languages/<int:language_id>/books', methods=['GET'])
# def get_books_by_language(language_id):
#     """Get all books that are in a specific language"""
#     # Code to handle retrieving all books in a given language
#     pass
