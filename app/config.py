import os
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


class BaseConfig:
    """Base configuration"""

    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', f'sqlite:///{BASE_DIR}/db.sqlite3')

    # NOTE: use secrets.token_hex(32) to generate a key (real one is in .env)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'f64ac936a2d9b7370c6b55b727f92c18')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'f64ac936a2d9b7370c6b55b727f92c18')
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_TOKEN_EXPIRES = 30000
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', f'sqlite:///{BASE_DIR}/dev_db.sqlite3')


class ProductionConfig(BaseConfig):
    """Production configuration"""
    # TODO: set SQLALCHEMY_DATABASE_URI to a postgresql database
    DEBUG = False
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SERVER_NAME = 'localhost'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', f'sqlite:///{BASE_DIR}/test_db.sqlite3')


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
