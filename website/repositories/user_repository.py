from typing import Optional
from sqlalchemy import select, or_
from website.models import User
from .base_repository import BaseRepository
from database import db


class UserRepository(BaseRepository[User]):
    """Repository for User database operations ONLY"""

    def __init__(self):
        super().__init__(User)

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        stmt = select(User).where(User.email == email)
        return db.session.execute(stmt).scalar_one_or_none()

    def find_by_phone(self, phone: str) -> Optional[User]:
        """Find user by phone"""
        stmt = select(User).where(User.phone == phone)
        return db.session.execute(stmt).scalar_one_or_none()

    def find_by_email_or_phone(self, email: str = None, phone: str = None) -> Optional[User]:
        """Find user by email OR phone"""
        conditions = []
        if email:
            conditions.append(User.email == email)
        if phone:
            conditions.append(User.phone == phone)

        if not conditions:
            return None

        stmt = select(User).where(or_(*conditions))
        return db.session.execute(stmt).scalar_one_or_none()

    def add_points(self, user: User, points: int) -> User:
        """Add points to user balance"""
        user.add_points(points)
        db.session.commit()
        db.session.refresh(user)
        return user

    def redeem_points(self, user: User, points: int) -> bool:
        """Redeem points from user balance"""
        success = user.redeem_points(points)
        if success:
            db.session.commit()
            db.session.refresh(user)
        return success