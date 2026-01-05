# models/favorite.py
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
from models.base import TimestampMixin

class Favorite(db.Model, TimestampMixin):
    __tablename__ = 'favorites'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    food_item_id: Mapped[int] = mapped_column(ForeignKey('food_items.id'), nullable=False)

    # Relationships
    user = relationship('User', back_populates='favorites')
    food_item = relationship('FoodItem', back_populates='favorites')

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'food_item_id', name='uq_user_food_item'),
    )

    def __repr__(self):
        return f'<Favorite user_id={self.user_id} item_id={self.food_item_id}>'