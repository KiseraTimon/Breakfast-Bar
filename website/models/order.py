# models/order.py
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Numeric, ForeignKey, Index, CheckConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
from .base import TimestampMixin
import enum

class OrderType(enum.Enum):
    DINE_IN = "dine-in"
    TAKEOUT = "takeout"
    DELIVERY = "delivery"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Order(db.Model, TimestampMixin):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey('customers.id'), index=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    order_type: Mapped[OrderType] = mapped_column(SQLEnum(OrderType), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
        index=True
    )
    notes: Mapped[str | None] = mapped_column(String(500))
    completed_at: Mapped[datetime | None]

    points_earned: Mapped[int] = mapped_column(default=0, nullable=False)
    points_redeemed: Mapped[int] = mapped_column(default=0, nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    # Relationships
    customer = relationship('Customer', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    payments = relationship('Payment', back_populates='order', cascade='all, delete-orphan')

    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='check_total_amount_positive'),
        Index('idx_order_status_created', 'status', 'created_at'),
        Index('idx_order_completed_at', 'completed_at'),
    )

    @staticmethod
    def generate_order_number() -> str:
        """Generate unique order number: BR-YYYYMMDD-XXX"""
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')

        # Get today's order count
        count = db.session.query(Order).filter(
            Order.order_number.like(f'BR-{today}-%')
        ).count()

        return f'BR-{today}-{count + 1:03d}'

    def calculate_total(self):
        """Recalculate total from order items"""
        self.total_amount = sum(item.subtotal for item in self.order_items)

    def mark_completed(self):
        """Mark order as completed with timestamp"""
        self.status = OrderStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)

    def calculate_points_earned(self) -> int:
        """
        Calculate points earned from this order.
        Rule: Every KES 100 spent = 10 points
        """
        # Only earn points on the amount actually paid (after discount)
        amount_paid = self.total_amount - self.discount_amount
        return int(amount_paid * 10)  # KES 100 = 10 points

    def __repr__(self):
        return f'<Order {self.order_number}>'
