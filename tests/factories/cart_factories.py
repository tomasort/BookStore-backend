import factory
from datetime import timedelta
from random import randint
from app import db
from tests.factories.user_factories import UserFactory
from tests.factories.book_factories import BookFactory
from app.models import Cart, CartItem
from app.models import Book
from app.models import User


class CartFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Cart
        # Use the SQLAlchemy session for database transactions
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    created_at = factory.Faker('date_this_month')
    updated_at = factory.LazyAttribute(lambda o: o.created_at + timedelta(days=randint(1, 30)))
    user = factory.SubFactory(UserFactory)
    user_id = factory.LazyAttribute(lambda o: o.user.id if o.user else None)

    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        """
        Post-generation hook to add CartItems to the Order.

        Args:
            create (bool): If True, the objects should be created in the DB.
            extracted (list): Optional list of CartItems instances to associate.
            **kwargs: Additional parameters passed to the CartItemFactory.
        """
        if not create:
            # Skip adding items if we're in "build" mode (no persistence).
            return
        # If specific items are provided, add them.
        if extracted:
            for item in extracted:
                item.cart = self
                db.session.add(item)
        else:
            # Otherwise, generate a random number of items.
            for _ in range(randint(1, 5)):
                CartItemFactory(cart=self, **kwargs)
        # Commit the items to the session.
        db.session.commit()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Override the default _create method to handle user or user_id.
        """
        user = kwargs.pop('user', None)
        user_id = kwargs.pop('user_id', None)

        if user:
            kwargs['user'] = user
            kwargs['user_id'] = user.id
        elif user_id:
            kwargs['user_id'] = user_id
            kwargs['user'] = db.session.select(User).filter(User.id == user_id).first()

        return super()._create(model_class, *args, **kwargs)


class CartItemFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = CartItem
        # Use the SQLAlchemy session for database transactions
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    book = factory.SubFactory(BookFactory)
    book_id = factory.LazyAttribute(lambda o: o.book.id)
    cart = factory.SubFactory(CartFactory)
    cart_id = factory.LazyAttribute(lambda o: o.cart.id)
    quantity = factory.Faker('random_int', min=1, max=100)
