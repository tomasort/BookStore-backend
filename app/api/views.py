from flask import current_app, render_template
from flask_login import login_required
from app.api import api

@api.route('/', methods=['GET'])
def index():
    return "API for book store"
