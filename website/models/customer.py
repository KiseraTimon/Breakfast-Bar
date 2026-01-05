# models/customer.py
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
from models.base import TimestampMixin

class Customer(db.Model, TimestampMixin):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id'),
        unique=True,
        index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    user = relationship('User')
    orders = relationship('Order', back_populates='customer')

    def __repr__(self):
        return f'<Customer {self.name}>'