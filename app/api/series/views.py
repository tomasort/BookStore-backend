from flask import request, jsonify
from app import db
from app.models import Series
from app.api.series import series


@series.route('', methods=['POST'])
def create_series():
    """Create a new series"""
    data = request.get_json()
    try:
        series = Series(name=data['name'])
        db.session.add(series)
        db.session.commit()
        return jsonify({"message": "Series created successfully",
                        "series_id": series.id}), 201
    except KeyError:
        return jsonify({'error': 'Invalid series data'}), 400


@series.route('', methods=['GET'])
def get_series():
    """Retrieve a list of series with filtering, pagination, and sorting"""
    series = db.session.execute(db.select(Series)).scalars()
    return jsonify([{"id": series.id, "name": series.name} for series in series])


@series.route('/<int:series_id>', methods=['GET'])
def get_single_series(series_id):
    """Retrieve a single series by its ID"""
    series = db.session.execute(
        db.select(Series).filter_by(id=series_id)).scalar()
    if series is None:
        return jsonify({'error': 'Series not found'}), 404
    return jsonify({"id": series.id, "name": series.name})


@series.route('/<int:series_id>', methods=['PUT'])
def update_series(series_id):
    """Update a series by its ID"""
    series = db.session.execute(
        db.select(Series).filter_by(id=series_id)).scalar()
    if series is None:
        return jsonify({'error': 'Series not found'}), 404
    data = request.get_json()
    try:
        series.name = data['name']
        db.session.commit()
        return jsonify({"message": "Series updated successfully"}), 200
    except KeyError:
        return jsonify({'error': 'Invalid series data'}), 400


@series.route('/<int:series_id>', methods=['DELETE'])
def delete_series(series_id):
    """Delete a series by its ID"""
    series = db.session.execute(
        db.select(Series).filter_by(id=series_id)).scalar()
    if series is None:
        return jsonify({'error': 'Series not found'}), 404
    db.session.delete(series)
    db.session.commit()
    return jsonify({"message": "Series deleted successfully"}), 200
