from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from website.models import Favorite, FoodItem
from .base_repository import BaseRepository
from database import db


class FavoriteRepository(BaseRepository[Favorite]):
    """Repository for Favorite database operations"""

    def __init__(self):
        super().__init__(Favorite)

    def find_by_user(self, user_id: int) -> List[Favorite]:
        """Get all favorites for a user"""
        stmt = (
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .options(joinedload(Favorite.food_item))
            .order_by(Favorite.created_at.desc())
        )
        return db.session.execute(stmt).scalars().unique().all()

    def find_by_user_and_item(
        self,
        user_id: int,
        food_item_id: int
    ) -> Optional[Favorite]:
        """Check if user has favorited a specific item"""
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.food_item_id == food_item_id
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def add_favorite(self, user_id: int, food_item_id: int) -> Favorite:
        """Add item to favorites"""
        favorite = Favorite(
            user_id=user_id,
            food_item_id=food_item_id
        )
        return self.create(favorite)

    def remove_favorite(self, user_id: int, food_item_id: int) -> bool:
        """Remove item from favorites"""
        favorite = self.find_by_user_and_item(user_id, food_item_id)
        if favorite:
            self.delete(favorite)
            return True
        return False

    def is_favorited(self, user_id: int, food_item_id: int) -> bool:
        """Check if item is in user's favorites"""
        return self.find_by_user_and_item(user_id, food_item_id) is not None

    def count_by_user(self, user_id: int) -> int:
        """Count total favorites for a user"""
        return db.session.query(func.count(Favorite.id)).filter(
            Favorite.user_id == user_id
        ).scalar() or 0