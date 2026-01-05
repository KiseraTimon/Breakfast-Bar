# models/food_item.py
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Index, CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
from models.base import TimestampMixin

class FoodItem(db.Model, TimestampMixin):
    __tablename__ = 'food_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        info={'min_value': 0}
    )
    is_available: Mapped[bool] = mapped_column(default=True, nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text)

    # Relationships
    category = relationship('Category', back_populates='food_items')
    ingredients = relationship('Ingredient', back_populates='food_item', cascade='all, delete-orphan')
    order_items = relationship('OrderItem', back_populates='food_item')
    favorites = relationship('Favorite', back_populates='food_item', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='food_item', cascade='all, delete-orphan')

    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
        Index('idx_food_item_category_available', 'category_id', 'is_available'),
    )

    @property
    def average_rating(self) -> float | None:
        """Calculate average rating from reviews"""
        if not self.reviews:
            return None
        return sum(r.rating for r in self.reviews) / len(self.reviews)

    def __repr__(self):
        return f'<FoodItem {self.name}>'