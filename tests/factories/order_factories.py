import factory
from tests.factories.book_factories import BookFactory
from app.orders.models import Order, OrderItem
from tests.factories.user_factories import UserFactory
from app import db
import random


class OrderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Order
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    date = factory.Faker('date_time_this_decade', before_now=True, after_now=False)
    total = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    status = factory.Faker('random_element', elements=["pending", "completed", "canceled"])
    user = factory.SubFactory(UserFactory)
    user_id = factory.LazyAttribute(lambda o: o.user.id)

    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        """
        Post-generation hook to add OrderItems to the Order.

        Args:
            create (bool): If True, the objects should be created in the DB.
            extracted (list): Optional list of OrderItem instances to associate.
            **kwargs: Additional parameters passed to the OrderItemFactory.
        """
        if not create:
            # Skip adding items if we're in "build" mode (no persistence).
            return
        # If specific items are provided, add them.
        if extracted:
            for item in extracted:
                item.order = self
                db.session.add(item)
        else:
            # Otherwise, generate a random number of items.
            for _ in range(random.randint(1, 5)):
                OrderItemFactory(order=self, **kwargs)
        # Commit the items to the session.
        db.session.commit()


class OrderItemFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = OrderItem
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    order = factory.SubFactory(OrderFactory)

    # Create a book during factory initialization
    book = factory.SubFactory(BookFactory)
    book_id = factory.LazyAttribute(lambda o: o.book.id)

    quantity = factory.Faker('random_int', min=1, max=100)
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
