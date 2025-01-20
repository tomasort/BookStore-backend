import pytest
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
        db.session.commit()
        yield app
        # Drop the database after tests are done
        db.session.remove()
        db.drop_all()


# @pytest.fixture
# def db_session(app):
#     # Begin a transaction
#     connection = db.engine.connect()
#     transaction = connection.begin()
#     options = {"bind": connection, "binds": {}}
#     # session = db.create_scoped_session(options=options)
#     session = db._make_scoped_session(options=options)
#     db.session = session

#     yield session  # Provide this session to the test

#     session.remove()  # Cleanup session
#     transaction.rollback()  # Rollback the transaction
#     connection.close()  # Close the connection


# @pytest.fixture(autouse=True)
# def db_session(app):
#     """Create a new database session for a test."""
#     with app.app_context():
#         connection = db.engine.connect()
#         transaction = connection.begin()

#         # Create a new session factory bound to the connection
#         session_factory = sessionmaker(bind=connection)
#         # Create a new scoped session
#         Session = scoped_session(session_factory)

#         # Override the default session with our test session
#         old_session = db.session
#         db.session = Session()

#         yield db.session

#         # Rollback the transaction and restore the default session
#         transaction.rollback()
#         connection.close()
#         Session.remove()
#         db.session = old_session


@pytest.fixture()
def client(app):
    # Use the test client for HTTP requests in your tests
    return app.test_client()


@pytest.fixture()
def runner(app):
    # Use the CLI runner for command line tests
    return app.test_cli_runner()


@pytest.fixture
def admin_user(user_factory):
    user = user_factory.create(role="admin")
    return user


@pytest.fixture
def regular_user(user_factory):
    user = user_factory.create(role="user")
    return user


@pytest.fixture
def user_token(regular_user):
    return create_access_token(identity=str(regular_user.id), additional_claims={"role": "user"})


@pytest.fixture
def user_csrf_token(user_token):
    return get_csrf_token(user_token)


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(identity=str(admin_user.id), additional_claims={"role": "admin"})


@pytest.fixture
def admin_csrf_token(admin_token):
    return get_csrf_token(admin_token)


@pytest.fixture
def cleanup_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
