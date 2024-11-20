import pytest
from app import create_app, db


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


@pytest.fixture()
def client(app):
    # Use the test client for HTTP requests in your tests
    return app.test_client()


@pytest.fixture()
def runner(app):
    # Use the CLI runner for command line tests
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def cleanup_db(app):
    with app.app_context():
        yield
        db.session.remove()
        db.drop_all()
        db.create_all()

# @pytest.fixture()
# def db_session(app):
#     """
#     Creates a new database session for a test.
#     Rolls back any changes to the database after the test completes.
#     """
#     # Start a transaction
#     with app.app_context():
#         connection = db.engine.connect()
#         transaction = connection.begin()

#         # Bind the session to the connection
#         db.session.bind = connection

#         yield db.session

#         # Rollback the transaction after the test
#         transaction.rollback()
#         connection.close()
#         db.session.remove()


@pytest.fixture()
def test_book_data():
    return {
        "title": "Test Book",
        "isbn_10": "1234567890",
        "isbn_13": "1234567890123",
        "publish_date": "2024-01-01",
        "description": "A test book description",
        "current_price": 19.99,
        "number_of_pages": 350,
        "editorial": "Test Editorial",
        "subtitle": "Test Subtitle",
    }


@pytest.fixture()
def test_authors_data():
    return [
        {
            "name": "Test Author 1",
            "birth_date": "1980-01-01",
            "biography": "A test author 1 biography",
        },
        {
            "name": "Test Author 2",
            "birth_date": "1985-01-01",
            "death_date": "2020-01-01",
            "biography": "A test author 2 biography",
        },
        {
            "name": "Test Author 3",
            "birth_date": "1990-01-01",
            "biography": "A test author 3 biography",
        },
    ]
