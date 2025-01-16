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
from flask_login import LoginManager
from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(DeclarativeBase, MappedAsDataclass):
    pass


# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
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
    login.init_app(app)
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

    return app


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "admin":
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
