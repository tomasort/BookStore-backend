from app import create_app
from flask import jsonify
from flask_jwt_extended import unset_jwt_cookies, unset_access_cookies
app = create_app()
