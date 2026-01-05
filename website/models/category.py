# models/category.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
from models.base import TimestampMixin

class Category(db.Model, TimestampMixin):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool]

    # Relationships
    food_items = relationship('FoodItem', back_populates='category')

    def __repr__(self):
        return f'<Category {self.name}>'