import os
from functools import wraps
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from logging.handlers import RotatingFileHandler
from app.config import config
import logging
from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request
from flask_jwt_extended import unset_jwt_cookies, unset_access_cookies


# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
ma = Marshmallow()
jwt = JWTManager()
# csrf = CSRFProtect()


def setup_logging(app: Flask) -> None:
    if not os.path.exists(f'{__name__}/logs'):
        os.mkdir(f'{__name__}/logs')
    file_handler = RotatingFileHandler(f'{__name__}/logs/{__name__}.log', maxBytes=10240, backupCount=10)
    format_strign = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    file_handler.setFormatter(logging.Formatter(format_strign))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.info('app startup')


def unauthorized(error):
    response = jsonify({"error": "Unauthorized User for this page"})
    unset_jwt_cookies(response)
    unset_access_cookies(response)
    return response, 401


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    # instantiate the app
    app = Flask(__name__)

    # set config
    app.config.from_object(config[config_name])

    # set up extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    # csrf.init_app(app)

    # register blueprints
    from app.api import api
    app.register_blueprint(api)

    from app.auth import auth
    app.register_blueprint(auth)

    from app.orders import orders
    app.register_blueprint(orders)

    from app.promotions import promotions
    app.register_blueprint(promotions)

    from app.cart import cart
    app.register_blueprint(cart)

    # set up logging
    setup_logging(app)

    app.logger.info(f"App is running in {config_name} mode")
    app.logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    # # app.register_error_handler(401, unauthorized)
    # @app.errorhandler(401)  # or whichever error code you need
    # def handle_unauthorized_access(e):
    #     """
    #     This error handler will unset the JWT cookies,
    #     effectively logging the user out or invalidating their session cookies.
    #     """
    #     app.logger.info("Unauthorized access. Token has been removed.")
    #     response = jsonify({"msg": "Unauthorized access. Token has been removed."})
    #     unset_jwt_cookies(response)
    #     return response, 401

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_data):
        """
        This function is called when an expired JWT token
        attempts to access a protected endpoint.
        jwt_header: dict containing header data
        jwt_data: dict containing JWT claims
        """
        response = jsonify({"msg": "Token has expired"})
        app.logger.info("Unauthorized access. Token has been removed.")
        # Optionally unset cookies (if using cookie-based tokens)
        unset_jwt_cookies(response)
        return response, 401

    return app


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "Admin":
                return jsonify(message="Admin only!"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != role:
                return jsonify(message=f"{role} only!"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
