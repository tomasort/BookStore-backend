from flask import Blueprint

promotions = Blueprint('promotions', __name__, url_prefix='/promotions')

from app.promotions import views, models, schemas
