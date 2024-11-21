from flask import current_app, render_template, request, jsonify, Request
from app import db
from app.api.models import Language
from app.api.languages import languages

# ----------- LANGUAGE ROUTES ----------- #


@languages.route('', methods=['POST'])
def create_language():
    """Create a new language"""
    try:
        language = Language(
            name=request.json.get("name"),
        )
        db.session.add(language)
        db.session.commit()
        return jsonify({"language_id": language.id, "message": "Language created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@languages.route('', methods=['GET'])
def get_languages():
    """Retrieve a list of languages with filtering, pagination, and sorting"""
    languages = db.session.execute(db.select(Language)).scalars()
    return jsonify(
        [
            {
                "id": language.id,
                "name": language.name,
            }
            for language in languages
        ]
    )


@languages.route('/<int:language_id>', methods=['GET'])
def get_language(language_id):
    """Retrieve a single language by its ID"""
    language = db.session.execute(
        db.select(Language).where(Language.id == language_id)).scalar()
    if not language:
        return jsonify({"error": "Language not found"}), 404
    return jsonify(
        {
            "id": language.id,
            "name": language.name,
        }
    )


@languages.route('/<int:language_id>', methods=['PUT'])
def update_language(language_id):
    """Update a language by its ID"""
    language = db.session.execute(
        db.select(Language).where(Language.id == language_id)).scalar()
    if not language:
        return jsonify({"error": "Language not found"}), 404

    data = request.json
    language.name = data.get("name", language.name)
    try:
        db.session.commit()
        return jsonify({"message": "Language updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@languages.route('/<int:language_id>', methods=['DELETE'])
def delete_language(language_id):
    """Delete a language by its ID"""
    language = db.session.execute(
        db.select(Language).where(Language.id == language_id)).scalar()
    if not language:
        return jsonify({"error": "Language not found"}), 404

    db.session.delete(language)
    db.session.commit()
    return jsonify({"message": "Language deleted successfully"}), 200
