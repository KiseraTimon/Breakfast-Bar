from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload

from website.models import PointsTransaction, PointsTransactionType
from .base_repository import BaseRepository
from database import db


class PointsRepository(BaseRepository[PointsTransaction]):
    """Repository for Points transactions"""

    def __init__(self):
        super().__init__(PointsTransaction)

    def find_by_user(
        self,
        user_id: int,
        limit: int = None
    ) -> List[PointsTransaction]:
        """Get all points transactions for a user"""
        stmt = (
            select(PointsTransaction)
            .where(PointsTransaction.user_id == user_id)
            .options(joinedload(PointsTransaction.order))
            .order_by(desc(PointsTransaction.created_at))
        )

        if limit:
            stmt = stmt.limit(limit)

        return db.session.execute(stmt).scalars().unique().all()

    def create_transaction(
        self,
        user_id: int,
        transaction_type: PointsTransactionType,
        points: int,
        order_id: int = None,
        description: str = None
    ) -> PointsTransaction:
        """Create a new points transaction"""
        transaction = PointsTransaction(
            user_id=user_id,
            order_id=order_id,
            transaction_type=transaction_type,
            points=points,
            description=description
        )
        return self.create(transaction)