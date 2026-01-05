# models/review.py
from sqlalchemy import String, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
from .base import TimestampMixin

class Review(db.Model, TimestampMixin):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    food_item_id: Mapped[int] = mapped_column(ForeignKey('food_items.id'), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str | None] = mapped_column(String(1000))

    # Relationships
    user = relationship('User', back_populates='reviews')
    food_item = relationship('FoodItem', back_populates='reviews')
    order = relationship('Order')

    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        Index('idx_review_food_item_rating', 'food_item_id', 'rating'),
    )

    def __repr__(self):
        return f'<Review {self.rating}/5 by user {self.user_id}>'