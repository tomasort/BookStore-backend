from flask import request, jsonify
from app import db
from app.models import Provider
from app.schemas import ProviderSchema
from app.api.providers import providers

provider_schema = ProviderSchema()


@providers.route("", methods=["POST"])
def create_provider():
    data = request.json
    try:
        provider_data = provider_schema.load(data)
        new_provider: Provider = Provider(**provider_data)
        db.session.add(new_provider)
        db.session.commit()
        return jsonify(
            {"message": "Provider created successfully",
                "provider_id": new_provider.id, "provider_name": new_provider.name}
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
