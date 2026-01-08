from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload

from website.models import Review, FoodItem
from .base_repository import BaseRepository
from database import db


class ReviewRepository(BaseRepository[Review]):
    """Repository for Review database operations"""

    def __init__(self):
        super().__init__(Review)

    def find_by_user(self, user_id: int) -> List[Review]:
        """Get all reviews by a user"""
        stmt = (
            select(Review)
            .where(Review.user_id == user_id)
            .options(joinedload(Review.food_item))
            .order_by(desc(Review.created_at))
        )
        return db.session.execute(stmt).scalars().unique().all()

    def find_by_user_and_item(
        self,
        user_id: int,
        food_item_id: int
    ) -> Optional[Review]:
        """Check if user has reviewed a specific item"""
        stmt = select(Review).where(
            Review.user_id == user_id,
            Review.food_item_id == food_item_id
        )
        return db.session.execute(stmt).scalar_one_or_none()

    def add_review(
        self,
        user_id: int,
        food_item_id: int,
        order_id: int,
        rating: int,
        comment: str = None
    ) -> Review:
        """Add a new review"""
        review = Review(
            user_id=user_id,
            food_item_id=food_item_id,
            order_id=order_id,
            rating=rating,
            comment=comment
        )
        return self.create(review)

    def update_review(
        self,
        review: Review,
        rating: int = None,
        comment: str = None
    ) -> Review:
        """Update an existing review"""
        if rating is not None:
            review.rating = rating
        if comment is not None:
            review.comment = comment

        return self.update(review)

    def count_by_user(self, user_id: int) -> int:
        """Count total reviews by a user"""
        return db.session.query(func.count(Review.id)).filter(
            Review.user_id == user_id
        ).scalar() or 0