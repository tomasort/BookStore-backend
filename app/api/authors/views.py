from flask import current_app, render_template, request, jsonify, Request
from datetime import datetime
from app import db
from app.api.authors import authors
from app.models import Author
from app.schemas.books import AuthorSchema


# ----------- AUTHOR ROUTES -----------
# TODO: use AuthorSchema to serialize the author data

@authors.route('', methods=['POST'])
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


@authors.route('', methods=['GET'])
def get_authors():
    """Retrieve a list of authors with filtering, pagination, and sorting"""
    authors = db.session.execute(db.select(Author)).scalars()
    return jsonify([AuthorSchema().dump(author) for author in authors])


@authors.route('/<int:author_id>', methods=['GET'])
def get_author(author_id):
    """Retrieve a single author by its ID"""
    author = db.session.execute(
        db.select(Author).where(Author.id == author_id)).scalar()
    if not author:
        return jsonify({"error": "Author not found"}), 404
    return jsonify(AuthorSchema().dump(author))


@authors.route('/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    """Update an author by its ID"""
    author = db.session.execute(db.select(Author).where(Author.id == author_id)).scalar()
    if not author:
        return jsonify({"error": "Author not found"}), 404

    data = request.json
    author.name = data.get("name", author.name)
    author.birth_date = datetime.strptime(
        data.get("birth_date"), "%Y-%m-%d").date() if "birth_date" in data else author.birth_date
    author.death_date = datetime.strptime(
        data.get("death_date"), "%Y-%m-%d").date() if "death_date" in data else author.death_date
    author.biography = data.get("biography", author.biography)

    try:
        db.session.commit()
        return jsonify({"message": "Author updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@authors.route('/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    """Delete an author by its ID"""
    author = db.session.execute(
        db.select(Author).where(Author.id == author_id)).scalar()
    if not author:
        return jsonify({"error": "Author not found"}), 404

    try:
        db.session.delete(author)
        db.session.commit()
        return jsonify({"message": "Author deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@authors.route('/<int:author_id>/books', methods=['GET'])
def get_books_by_author(author_id):
    """Get all books by a specific author"""
    # Query the author by ID
    author = db.session.execute(
        db.select(Author).where(Author.id == author_id)
    ).scalar()

    if not author:
        return jsonify({"error": "Author not found"}), 404

    # Access the books through the relationship
    books = author.books

    # Return the books as JSON
    return jsonify([
        {
            "id": book.id,
            "title": book.title,
            "publish_date": book.publish_date,
            "isbn_10": book.isbn_10,
            "isbn_13": book.isbn_13,
            "number_of_pages": book.number_of_pages,
        }
        for book in books
    ])
