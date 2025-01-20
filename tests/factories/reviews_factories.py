# TODO: create a factory for reviews

import factory
from app.models import Review
from tests.factories.book_factories import BookFactory
from tests.factories.user_factories import UserFactory
from app import db


class ReviewFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Review
        sqlalchemy_session = db.session

    book = factory.SubFactory(BookFactory)
    book_id = factory.LazyAttribute(lambda o: o.book.id)
    user = factory.SubFactory(UserFactory)
    user_id = factory.LazyAttribute(lambda o: o.user.id)
    rating = factory.Faker('random_int', min=1, max=5)
    comment = factory.Faker('paragraph')
    created_at = factory.Faker('date_time_this_decade', before_now=True, after_now=False)
