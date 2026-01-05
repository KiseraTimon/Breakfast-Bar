# models/daily_sales_summary.py
from decimal import Decimal
from datetime import date
from sqlalchemy import Date, Numeric, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
from .base import TimestampMixin

class DailySalesSummary(db.Model, TimestampMixin):
    __tablename__ = 'daily_sales_summary'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    order_count: Mapped[int] = mapped_column(nullable=False, default=0)
    average_order_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    top_selling_item_id: Mapped[int | None] = mapped_column(ForeignKey('food_items.id'))

    # Relationships
    top_selling_item = relationship('FoodItem')

    def __repr__(self):
        return f'<DailySalesSummary {self.date}>'