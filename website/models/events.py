# models/events.py
from sqlalchemy import event
from sqlalchemy.orm import Session
from . import Order, OrderItem
from . import Payment, PaymentStatus
from datetime import datetime, timezone

# Automatically calculate order item subtotal
@event.listens_for(OrderItem, 'before_insert')
@event.listens_for(OrderItem, 'before_update')
def calculate_order_item_subtotal(mapper, connection, target):
    """Automation: Calculate subtotal before save"""
    target.calculate_subtotal()

# Automatically recalculate order total when items change
@event.listens_for(OrderItem, 'after_insert')
@event.listens_for(OrderItem, 'after_update')
@event.listens_for(OrderItem, 'after_delete')
def update_order_total(mapper, connection, target):
    """Automation: Update order total when items change"""
    session = Session.object_session(target)
    if session:
        order = session.get(Order, target.order_id)
        if order:
            order.calculate_total()

# Automatically mark order as completed when payment is completed
@event.listens_for(Payment, 'after_update')
def complete_order_on_payment(mapper, connection, target):
    """Automation: Complete order when payment is successful"""
    if target.status == PaymentStatus.COMPLETED:
        session = Session.object_session(target)
        if session:
            order = session.get(Order, target.order_id)
            if order and order.status != OrderStatus.COMPLETED:
                order.mark_completed()