import factory
from datetime import datetime, timezone
from app.promotions.models import Promotions
import random
from app import db


def generate_condition():
    """Generate a single condition with random values."""
    condition_types = [
        {
            "type": "book_category",
            "value": random.choice(["fiction", "non-fiction", "science", "history", "biography"])
        },
        {
            "type": "min_order_value",
            "value": random.randint(20, 200)
        },
        {
            "type": "user_type",
            "value": random.choice(["regular", "premium", "vip"])
        }
    ]
    return random.choice(condition_types)


def generate_complex_condition():
    """Generate a complex condition with AND/OR logic."""
    num_conditions = random.randint(1, 3)  # Random number of conditions
    conditions = [generate_condition() for _ in range(num_conditions)]

    # Sometimes return a single condition, sometimes a complex one
    if len(conditions) == 1 and random.random() < 0.3:  # 30% chance for single condition
        return conditions[0]

    return {
        "type": random.choice(["and", "or"]),
        "conditions": conditions
    }


class PromotionsFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Promotions
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker('name')
    description = factory.Faker('paragraph')
    discount_type = factory.Faker('random_element', elements=["percentage", "fixed"])
    discount_value = factory.Faker('random_int', min=1, max=100)
    start_date = factory.Faker('past_date')
    end_date = factory.Faker('future_date')
    active = factory.Faker('boolean')
    conditions = factory.LazyFunction(generate_complex_condition)
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
