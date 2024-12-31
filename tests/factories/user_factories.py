import factory
from app.auth.models import User
from app import db
import random


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    active = factory.Faker('boolean')
    # Automatically create a list of orders when creating a user
    orders = factory.RelatedFactoryList("tests.factories.order_factories.OrderFactory", factory_related_name='user', size=3)
    password_hash = factory.PostGenerationMethodCall('set_password', "password")

    @factory.post_generation
    def role(self, create, extracted, **kwargs):
        if extracted:
            self.role = extracted

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if extracted:
            self.set_password(extracted)

    # @factory.post_generation
    # def orders(self, create, extracted, **kwargs):
    #     if not create:
    #         return

    #     if extracted:
    #         # If orders are passed in, use those
    #         for order in extracted:
    #             order.user = self
    #     else:
    #         # Otherwise create 3 orders
    #         from tests.factories.order_factories import OrderFactory
    #         OrderFactory.create_batch(size=3, user=self)
