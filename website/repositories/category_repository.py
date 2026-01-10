from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from website.models import Category
from .base_repository import BaseRepository
from database import db


class CategoryRepository(BaseRepository[Category]):
    """Repository for Category database operations"""

    def __init__(self):
        super().__init__(Category)

    def find_all_active(self) -> List[Category]:
        """Get all active categories ordered by sort_order"""
        stmt = (
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.sort_order, Category.name)
        )
        return db.session.execute(stmt).scalars().all()

    def find_by_id_with_items(self, category_id: int) -> Optional[Category]:
        """Get category with its food items"""
        stmt = (
            select(Category)
            .where(Category.id == category_id)
            .options(joinedload(Category.food_items))
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def find_by_name(self, name: str) -> Optional[Category]:
        """Find category by name"""
        stmt = select(Category).where(Category.name == name)
        return db.session.execute(stmt).scalar_one_or_none()