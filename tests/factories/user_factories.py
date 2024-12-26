import factory
from app.auth.models import User
# from tests.order_factories import OrderFactory
from app import db
import random


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password_hash = factory.Faker('password')
    active = factory.Faker('boolean')
    # Automatically create a list of orders when creating a user
    # orders = factory.RelatedFactoryList('OrderFactory', factory_related_name='user', size=3)

    # @factory.post_generation
    # def orders(self, create, extracted, **kwargs):
    #     """
    #     Post-generation hook to add orders to the User.

    #     Args:
    #         create (bool): If True, the objects should be created in the DB.
    #         extracted (list): Optional list of Order instances to associate.
    #         **kwargs: Additional parameters passed to the OrderFactory.
    #     """
    #     if not create:
    #         # Skip adding items if we're in "build" mode (no persistence).
    #         return
    #     # If specific items are provided, add them.
    #     if extracted:
    #         for order in extracted:
    #             order.user = self
    #             db.session.add(order)
    #     else:
    #         # Otherwise, generate a random number of items.
    #         for _ in range(random.randint(1, 5)):
    #             OrderFactory(user=self, **kwargs)
    #     # Commit the items to the session.
    #     db.session.commit()
