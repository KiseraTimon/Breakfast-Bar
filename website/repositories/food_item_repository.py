from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import joinedload

from website.models import FoodItem, Category, Ingredient, Review, OrderItem
from .base_repository import BaseRepository
from database import db


class FoodItemRepository(BaseRepository[FoodItem]):
    """Repository for FoodItem database operations"""

    def __init__(self):
        super().__init__(FoodItem)

    def find_by_id_with_details(self, food_item_id: int) -> Optional[FoodItem]:
        """
        Get food item with all related data (ingredients, reviews, category).
        Optimized with eager loading to reduce queries.
        """
        stmt = (
            select(FoodItem)
            .where(FoodItem.id == food_item_id)
            .options(
                joinedload(FoodItem.category),
                joinedload(FoodItem.ingredients),
                joinedload(FoodItem.reviews).joinedload(Review.user)
            )
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def find_all_available(
        self,
        page: int = 1,
        per_page: int = 20
    ) -> List[FoodItem]:
        """Get all available food items with pagination"""
        stmt = (
            select(FoodItem)
            .where(FoodItem.is_available == True)
            .options(joinedload(FoodItem.category))
            .order_by(FoodItem.name)
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        return db.session.execute(stmt).scalars().unique().all()

    def find_by_category(
        self,
        category_id: int,
        available_only: bool = True,
        page: int = 1,
        per_page: int = 20
    ) -> List[FoodItem]:
        """Get food items by category"""
        conditions = [FoodItem.category_id == category_id]

        if available_only:
            conditions.append(FoodItem.is_available == True)

        stmt = (
            select(FoodItem)
            .where(and_(*conditions))
            .options(joinedload(FoodItem.category))
            .order_by(FoodItem.name)
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        return db.session.execute(stmt).scalars().unique().all()

    def search_by_name(
        self,
        search_term: str,
        available_only: bool = True,
        page: int = 1,
        per_page: int = 20
    ) -> List[FoodItem]:
        """Search food items by name"""
        conditions = [FoodItem.name.ilike(f'%{search_term}%')]

        if available_only:
            conditions.append(FoodItem.is_available == True)

        stmt = (
            select(FoodItem)
            .where(and_(*conditions))
            .options(joinedload(FoodItem.category))
            .order_by(FoodItem.name)
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        return db.session.execute(stmt).scalars().unique().all()

    def count_available(self) -> int:
        """Count total available items"""
        return db.session.query(func.count(FoodItem.id)).filter(
            FoodItem.is_available == True
        ).scalar() or 0

    def count_by_category(self, category_id: int, available_only: bool = True) -> int:
        """Count items in a category"""
        conditions = [FoodItem.category_id == category_id]

        if available_only:
            conditions.append(FoodItem.is_available == True)

        return db.session.query(func.count(FoodItem.id)).filter(
            and_(*conditions)
        ).scalar() or 0

    def get_popular_items(self, limit: int = 10) -> List[FoodItem]:
        """
        Get most popular items based on order count.
        """
        stmt = (
            select(FoodItem)
            .join(OrderItem, OrderItem.food_item_id == FoodItem.id)
            .where(FoodItem.is_available == True)
            .group_by(FoodItem.id)
            .order_by(desc(func.count(OrderItem.id)))
            .limit(limit)
        )
        return db.session.execute(stmt).scalars().unique().all()

    def get_top_rated_items(self, limit: int = 10, min_reviews: int = 3) -> List[FoodItem]:
        """
        Get top rated items with minimum number of reviews.
        """
        stmt = (
            select(FoodItem)
            .join(Review, Review.food_item_id == FoodItem.id)
            .where(FoodItem.is_available == True)
            .group_by(FoodItem.id)
            .having(func.count(Review.id) >= min_reviews)
            .order_by(desc(func.avg(Review.rating)))
            .limit(limit)
        )
        return db.session.execute(stmt).scalars().unique().all()

    def get_newest_items(self, limit: int = 10) -> List[FoodItem]:
        """Get newest food items"""
        stmt = (
            select(FoodItem)
            .where(FoodItem.is_available == True)
            .order_by(desc(FoodItem.created_at))
            .limit(limit)
        )
        return db.session.execute(stmt).scalars().all()

    def get_average_rating(self, food_item_id: int) -> float:
        """Get average rating for a food item"""
        avg_rating = db.session.query(
            func.avg(Review.rating)
        ).filter(
            Review.food_item_id == food_item_id
        ).scalar()

        return float(avg_rating) if avg_rating else 0.0

    def get_review_count(self, food_item_id: int) -> int:
        """Get total reviews for a food item"""
        return db.session.query(func.count(Review.id)).filter(
            Review.food_item_id == food_item_id
        ).scalar() or 0