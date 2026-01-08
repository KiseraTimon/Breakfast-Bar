from typing import Optional
from sqlalchemy import select, or_
from website.models import Customer
from .base_repository import BaseRepository
from database import db


class CustomerRepository(BaseRepository[Customer]):
    """Repository for Customer database operations ONLY"""

    def __init__(self):
        super().__init__(Customer)

    def find_by_email(self, email: str) -> Optional[Customer]:
        """Find customer by email"""
        stmt = select(Customer).where(Customer.email == email)
        return db.session.execute(stmt).scalar_one_or_none()

    def find_by_phone(self, phone: str) -> Optional[Customer]:
        """Find customer by phone"""
        stmt = select(Customer).where(Customer.phone == phone)
        return db.session.execute(stmt).scalar_one_or_none()

    def find_by_email_or_phone(self, email: str = None, phone: str = None) -> Optional[Customer]:
        """Find customer by email OR phone"""
        conditions = []
        if email:
            conditions.append(Customer.email == email)
        if phone:
            conditions.append(Customer.phone == phone)

        if not conditions:
            return None

        stmt = select(Customer).where(or_(*conditions))
        return db.session.execute(stmt).scalar_one_or_none()

    def find_by_user_id(self, user_id: int) -> Optional[Customer]:
        """Find customer by linked user ID"""
        stmt = select(Customer).where(Customer.user_id == user_id)
        return db.session.execute(stmt).scalar_one_or_none()