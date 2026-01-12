from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
from .base import TimestampMixin
import enum


class PointsTransactionType(enum.Enum):
    EARNED = "earned"      # Points earned from order
    REDEEMED = "redeemed"  # Points used for discount
    BONUS = "bonus"        # Bonus points (promotions, etc)
    ADJUSTED = "adjusted"  # Manual adjustment


class PointsTransaction(db.Model, TimestampMixin):
    __tablename__ = 'points_transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey('orders.id'), index=True)

    transaction_type: Mapped[PointsTransactionType] = mapped_column(
        SQLEnum(PointsTransactionType),
        nullable=False
    )
    points: Mapped[int] = mapped_column(nullable=False)  # Positive for earned, negative for redeemed
    description: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    user = relationship('User')
    order = relationship('Order')

    def __repr__(self):
        return f'<PointsTransaction {self.transaction_type.value}: {self.points} points>'