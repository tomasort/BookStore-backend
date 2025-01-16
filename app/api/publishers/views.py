from flask import request, jsonify
from app import db
from app.models import Publisher
from app.api.publishers import publishers


@publishers.route('', methods=['POST'])
def create_publisher():
    """Create a new publisher"""
    publisher = Publisher(name=request.json['name'])
    try:
        db.session.add(publisher)
        db.session.commit()
        return jsonify({"message": "Publisher created successfully",
                        "publisher_id": publisher.id}), 201
    except KeyError:
        return jsonify({'error': 'Invalid publisher data'}), 400


@publishers.route('', methods=['GET'])
def get_publishers():
    """Retrieve a list of publishers with filtering, pagination, and sorting"""
    publishers = db.session.execute(db.select(Publisher)).scalars()
    try:
        return jsonify([{"id": publisher.id, "name": publisher.name} for publisher in publishers])
    except KeyError:
        return jsonify({'error': 'Invalid publisher data'}), 400


@publishers.route('/<int:publisher_id>', methods=['GET'])
def get_publisher(publisher_id):
    """Retrieve a single publisher by its ID"""
    publisher = db.session.execute(db.select(Publisher).filter_by(id=publisher_id)).scalar()
    if publisher is None:
        return jsonify({'error': 'Publisher not found'}), 404
    return jsonify({"id": publisher.id, "name": publisher.name})


@publishers.route('/<int:publisher_id>', methods=['PUT'])
def update_publisher(publisher_id):
    """Update a publisher by its ID"""
    publisher = db.session.execute(db.select(Publisher).filter_by(id=publisher_id)).scalar()
    if publisher is None:
        return jsonify({'error': 'Publisher not found'}), 404
    data = request.json
    try:
        publisher.name = data['name']
        db.session.commit()
        return jsonify({"message": "Publisher updated successfully"}), 200
    except KeyError:
        return jsonify({'error': 'Invalid publisher data'}), 400


@publishers.route('/<int:publisher_id>', methods=['DELETE'])
def delete_publisher(publisher_id):
    """Delete a publisher by its ID"""
    publisher = db.session.execute(db.select(Publisher).filter_by(id=publisher_id)).scalar()
    if publisher is None:
        return jsonify({'error': 'Publisher not found'}), 404
    db.session.delete(publisher)
    db.session.commit()
    return jsonify({"message": "Publisher deleted successfully"}), 200
