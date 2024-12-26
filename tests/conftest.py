import pytest
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


# @pytest.fixture(autouse=True)
# def cleanup_db(app):
#     with app.app_context():
#         yield
#         db.drop_all()
#         db.create_all()
