from flask import jsonify, request
from app import db
from app.api.genres import genres
from app.api.models import Genre

# ----------- GENRE ROUTES ----------- #


@genres.route('', methods=['POST'])
def create_genre():
    """Create a new genre"""
    data = request.get_json()
    try:
        genre = Genre(name=data['name'])
        db.session.add(genre)
        db.session.commit()
        return jsonify({"message": "Genre created successfully",
                "genre_id": genre.id}), 201
    except KeyError:
        return jsonify({'error': 'Invalid genre data'}), 400


@genres.route('', methods=['GET'])
def get_genres():
    """Retrieve a list of genres with filtering, pagination, and sorting"""
    genres = db.session.execute(db.select(Genre)).scalars()
    return jsonify([{"id": genre.id, "name": genre.name} for genre in genres])


@genres.route('/<int:genre_id>', methods=['GET'])
def get_genre(genre_id):
    """Retrieve a single genre by its ID"""
    genre = db.session.execute(db.select(Genre).filter_by(id=genre_id)).scalar()
    if genre is None:
        return jsonify({'error': 'Genre not found'}), 404
    return jsonify({"id": genre.id, "name": genre.name})


@genres.route('/<int:genre_id>', methods=['PUT'])
def update_genre(genre_id):
    """Update a genre by its ID"""
    genre = db.session.execute(db.select(Genre).filter_by(id=genre_id)).scalar()
    if genre is None:
        return jsonify({'error': 'Genre not found'}), 404
    data = request.get_json()
    try:
        genre.name = data['name']
        db.session.commit()
        return jsonify({"message": "Genre updated successfully"}), 200
    except KeyError:
        return jsonify({'error': 'Invalid genre data'}), 400


@genres.route('/<int:genre_id>', methods=['DELETE'])
def delete_genre(genre_id):
    """Delete a genre by its ID"""
    genre = db.session.execute(db.select(Genre).filter_by(id=genre_id)).scalar()
    if genre is None:
        return jsonify({'error': 'Genre not found'}), 404
    db.session.delete(genre)
    db.session.commit()
    return jsonify({"message": "Genre deleted successfully"}), 200
