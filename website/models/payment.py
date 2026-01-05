# models/payment.py
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Index, CheckConstraint, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
from .base import TimestampMixin
import enum

class PaymentMethod(enum.Enum):
    MPESA = "mpesa"
    CASH = "cash"
    CARD = "card"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(db.Model, TimestampMixin):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(SQLEnum(PaymentMethod), nullable=False)
    transaction_reference: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.PENDING
    )
    meta: Mapped[dict | None] = mapped_column(JSON)  # For gateway responses

    # Relationships
    order = relationship('Order', back_populates='payments')

    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_payment_amount_positive'),
        Index('idx_payment_status_created', 'status', 'created_at'),
    )

    def __repr__(self):
        return f'<Payment {self.transaction_reference}>'