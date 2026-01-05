"""
Importing all models here to ensure they're registered with SQLAlchemy.
This is required for Alembic to detect and generate migrations.
"""

from models.user import User
from models.category import Category
from models.food_item import FoodItem
from models.ingredient import Ingredient
from models.customer import Customer
from models.order import Order, OrderType, OrderStatus
from models.order_item import OrderItem
from models.payment import Payment, PaymentMethod, PaymentStatus
from models.favorite import Favorite
from models.review import Review
from models.daily_sales_summary import DailySalesSummary

# Event listeners must be imported to register
from models import events

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