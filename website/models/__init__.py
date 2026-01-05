"""
Importing all models here to ensure they're registered with SQLAlchemy.
This is required for Alembic to detect and generate migrations.
"""

from .user import User, UserRole
from .category import Category
from .food_item import FoodItem
from .ingredient import Ingredient
from .customer import Customer
from .order import Order, OrderType, OrderStatus
from .order_item import OrderItem
from .payment import Payment, PaymentMethod, PaymentStatus
from .favorite import Favorite
from .review import Review
from .daily_sales_summary import DailySalesSummary

# Event listeners must be imported to register
from . import events

__all__ = [
    'User',
    'Category',
    'FoodItem',
    'Ingredient',
    'Customer',
    'Order',
    'OrderType',
    'OrderStatus',
    'OrderItem',
    'Payment',
    'PaymentMethod',
    'PaymentStatus',
    'Favorite',
    'Review',
    'DailySalesSummary',
]