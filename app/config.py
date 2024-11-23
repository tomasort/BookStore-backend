import os
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


class BaseConfig:
    """Base configuration"""

    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f'sqlite:///{BASE_DIR}/db.sqlite3')

    # NOTE: use secrets.token_hex(32) to generate a key (real one is in .env)
    SECRET_KEY = os.environ.get(
        'SECRET_KEY', 'f64ac936a2d9b7370c6b55b727f92c18')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f'sqlite:///{BASE_DIR}/dev_db.sqlite3')


class ProductionConfig(BaseConfig):
    """Production configuration"""
    # TODO: set SQLALCHEMY_DATABASE_URI to a postgresql database
    DEBUG = False


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', f'sqlite:///{BASE_DIR}/test_db.sqlite3')


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
