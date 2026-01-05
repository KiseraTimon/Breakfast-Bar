# repositories/base_repository.py
from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy import select, func
from database import db

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations"""

    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        """Get single record by ID"""
        return db.session.get(self.model, id)

    def get_all(self, page: int = 1, per_page: int = 20) -> List[T]:
        """Get all records with pagination"""
        stmt = select(self.model).limit(per_page).offset((page - 1) * per_page)
        return db.session.execute(stmt).scalars().all()

    def create(self, **kwargs) -> T:
        """Create new record"""
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, instance: T, **kwargs) -> T:
        """Update existing record"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.session.commit()
        return instance

    def delete(self, instance: T) -> None:
        """Delete record"""
        db.session.delete(instance)
        db.session.commit()

    def count(self) -> int:
        """Count total records"""
        return db.session.query(func.count(self.model.id)).scalar()