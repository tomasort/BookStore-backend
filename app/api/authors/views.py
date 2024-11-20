from flask import current_app, render_template, request, jsonify, Request
from datetime import datetime
from app.api.authors import authors
from app import db
from app.api.models import Author


# # ----------- AUTHOR ROUTES -----------

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
    return jsonify(
        [
            {
                "id": author.id,
                "name": author.name,
                "birth_date": author.birth_date,
                "death_date": author.death_date,
                "biography": author.biography,
            }
            for author in authors
        ]
    )


# @authors.route('/authors/<int:author_id>', methods=['GET'])
# def get_author(author_id):
#     """Retrieve a single author by its ID"""
#     # Code to handle retrieving an author by ID
#     pass


# @authors.route('/authors/<int:author_id>', methods=['PUT'])
# def update_author(author_id):
#     """Update an author by its ID"""
#     # Code to handle updating an author by ID
#     pass


# @authors.route('/authors/<int:author_id>', methods=['DELETE'])
# def delete_author(author_id):
#     """Delete an author by its ID"""
#     # Code to handle deleting an author by ID
#     pass


# @authors.route('/authors/<int:author_id>/books', methods=['GET'])
# def get_books_by_author(author_id):
#     """Get all books by a specific author"""
#     # Code to handle retrieving all books by a given author
#     pass
