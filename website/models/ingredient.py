# models/ingredient.py
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db

class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id: Mapped[int] = mapped_column(primary_key=True)
    food_item_id: Mapped[int] = mapped_column(ForeignKey('food_items.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_allergen: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    food_item = relationship('FoodItem', back_populates='ingredients')

    def __repr__(self):
        return f'<Ingredient {self.name}>'