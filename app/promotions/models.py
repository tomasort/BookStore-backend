from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime, timezone
from app import db

# NOTE: we need to add the implementation of the conditions to the documentation. For example, a
# condition might look like this:
# {
#   "type": "and",
#   "conditions": [
#     {
#       "type": "min_order_value",
#       "value": 50
#     },
#     {
#       "type": "book_category",
#       "value": "fiction"
#     }
#   ]
# }


class Promotions(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))
    discount_type: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=False, default='percentage')  # 'percentage' or 'fixed'
    discount_value: so.Mapped[Optional[int]] = so.mapped_column(sa.Numeric(10, 2), nullable=False)
    start_date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, nullable=False)
    end_date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, nullable=False)
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.now(timezone.utc))
    updated_at: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime, default=datetime.now(timezone.utc))
    conditions: so.Mapped[Optional[dict]] = so.mapped_column(sa.JSON, nullable=True)

    def is_active(self):
        """
        Check if the promotion is currently active based on start and end dates.
        """
        now = datetime.utcnow()
        return self.start_date <= now <= self.end_date

    def evaluate_conditions(self, user=None, order=None, book=None):
        """
        Evaluate whether the promotion conditions are met.

        :param user: The User object (optional)
        :param order: The Order object (optional)
        :param book: The Book object (optional)
        :return: Boolean indicating if the promotion is applicable
        """
        if not self.conditions:
            return True  # No conditions, always applicable

        condition_type = self.conditions.get('type')
        condition_value = self.conditions.get('value')
        if condition_type == "book_category":
            return book and book.category == condition_value
        if condition_type == "book_id":
            return book and book.id == condition_value
        if condition_type == "min_order_value":
            return order and order.total_price >= condition_value
        if condition_type == "user_type":
            return user and user.user_type == condition_value
        if condition_type == "and":
            return all(
                Promotion._evaluate_single_condition(cond, user, order, book)
                for cond in self.conditions.get('conditions', [])
            )
        if condition_type == "or":
            return any(
                Promotion._evaluate_single_condition(cond, user, order, book)
                for cond in self.conditions.get('conditions', [])
            )
        return False  # Default to not applicable if conditions are not met

    @staticmethod
    def _evaluate_single_condition(condition, user=None, order=None, book=None):
        """
        Evaluate a single condition. Used for nested conditions in AND/OR logic.

        :param condition: A single condition dictionary
        :param user: The User object (optional)
        :param order: The Order object (optional)
        :param book: The Book object (optional)
        :return: Boolean indicating if the condition is met
        """
        condition_type = condition.get('type')
        condition_value = condition.get('value')
        if condition_type == "book_category":
            return book and book.category == condition_value
        if condition_type == "min_order_value":
            return order and order.total_price >= condition_value
        if condition_type == "user_type":
            return user and user.user_type == condition_value
        return False
