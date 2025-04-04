import pytest
from app.models.users import Role
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_jwt_extended import create_access_token, get_csrf_token
from app import create_app, db
from tests.factories import (
    BookFactory,
    AuthorFactory,
    GenreFactory,
    PublisherFactory,
    LanguageFactory,
    SeriesFactory,
    ProviderFactory,
    FeaturedBookFactory,
    OrderFactory,
    OrderItemFactory,
    UserFactory,
    CartFactory,
    CartItemFactory,
    ReviewFactory,
)
from pytest_factoryboy import register

register(BookFactory)
register(AuthorFactory)
register(GenreFactory)
register(PublisherFactory)
register(LanguageFactory)
register(SeriesFactory)
register(ProviderFactory)
register(FeaturedBookFactory)

register(OrderFactory)
register(OrderItemFactory)

register(UserFactory)

register(CartFactory)
register(CartItemFactory)

register(ReviewFactory)


@pytest.fixture(scope="session")
def app():
    # Create the app instance with the testing configuration
    app = create_app("testing")

    # Establish an application context before running the tests
    with app.app_context():
        # Create the database and tables for testing
        db.create_all()
        yield app
        # Drop the database after tests are done
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app, db_session):
    # Start a transaction for the test
    # connection = db.engine.connect()
    # transaction = connection.begin()
    # db.session.bind = connection
    # db.session.begin_nested()

    # Create a test client
    with app.test_client() as client:
        yield client

    # Roll back the transaction after the test
    # db.session.remove()
    # transaction.rollback()
    # connection.close()


@pytest.fixture(scope="function")
def db_session(app):
    # Start a transaction for the test
    connection = db.engine.connect()
    transaction = connection.begin()
    db.session.bind = connection
    db.session.begin_nested()

    yield db.session  # Provide the session to the test

    # Roll back the transaction after the test
    db.session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def runner(app):
    # Use the CLI runner for command line tests
    return app.test_cli_runner()


@pytest.fixture
def admin_user(user_factory):
    user = user_factory.create(role=Role.ADMIN)
    return user


@pytest.fixture
def regular_user(user_factory):
    user = user_factory.create(role=Role.USER)
    return user


@pytest.fixture
def user_token(regular_user):
    return create_access_token(identity=str(regular_user.id), additional_claims={"role": Role.USER.value})


@pytest.fixture
def user_csrf_token(user_token):
    return get_csrf_token(user_token)


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(identity=str(admin_user.id), additional_claims={"role": Role.ADMIN.value})


@pytest.fixture
def admin_csrf_token(admin_token):
    return get_csrf_token(admin_token)


@pytest.fixture
def cleanup_db(app):
    with app.app_context():
        # db.drop_all()
        # db.create_all()
        yield
        # db.session.remove()
        # db.drop_all()
