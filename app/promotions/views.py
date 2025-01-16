from flask import current_app, render_template, request, jsonify, Request
from datetime import datetime
from app import db
from app.promotions import promotions
from app.schemas import PromotionsSchema
from app.models import Promotions


promotions_schema = PromotionsSchema()


@promotions.route("", methods=["POST"])
def create_promotion():
    data = request.json
    try:
        promotion_data = promotions_schema.load(data)
        new_promotion = Promotions(**promotion_data)
        db.session.add(new_promotion)
        db.session.commit()
        return jsonify(
            {"message": "Promotion created successfully",
                "promotion_id": new_promotion.id, "promotion_title": new_promotion.title}
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
