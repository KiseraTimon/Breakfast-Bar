# models/order_item.py
from decimal import Decimal
from sqlalchemy import Numeric, ForeignKey, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False, index=True)
    food_item_id: Mapped[int] = mapped_column(ForeignKey('food_items.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    vat: Mapped[int | None] = mapped_column(nullable=False, default=0)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    order = relationship('Order', back_populates='order_items')
    food_item = relationship('FoodItem', back_populates='order_items')

    # Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='check_unit_price_positive'),
        CheckConstraint('subtotal >= 0', name='check_subtotal_positive'),
    )

    def calculate_subtotal(self):
        """Calculate subtotal from quantity and unit price"""
        subtotal = self.quantity * self.unit_price
        self.subtotal = subtotal + (subtotal * self.vat)

    def __repr__(self):
        return f'<OrderItem order_id={self.order_id} item_id={self.food_item_id}>'