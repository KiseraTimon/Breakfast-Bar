# services/order_service.py
from typing import List, Dict
from decimal import Decimal
from . import Order, OrderType, OrderStatus, OrderItem, FoodItem
from website.repositories import OrderRepository
from database import db

class OrderService:

    def __init__(self):
        self.order_repo = OrderRepository()

    def create_order(
        self,
        customer_id: int | None,
        items: List[Dict[str, int]],  # [{'food_item_id': 1, 'quantity': 2}, ...]
        order_type: OrderType,
        notes: str | None = None
    ) -> Order:
        """
        Create a new order with validation
        items: [{'food_item_id': 1, 'quantity': 2}, ...]
        """
        # Validate items availability
        food_item_ids = [item['food_item_id'] for item in items]
        food_items = db.session.query(FoodItem).filter(
            FoodItem.id.in_(food_item_ids),
            FoodItem.is_available == True
        ).all()

        if len(food_items) != len(food_item_ids):
            raise ValueError("Some items are not available")

        # Create food items lookup
        food_items_map = {item.id: item for item in food_items}

        # Create order
        order = Order(
            customer_id=customer_id,
            order_number=Order.generate_order_number(),
            total_amount=Decimal('0.00'),
            order_type=order_type,
            status=OrderStatus.PENDING,
            notes=notes
        )
        db.session.add(order)
        db.session.flush()  # Get order ID

        # Create order items
        for item_data in items:
            food_item = food_items_map[item_data['food_item_id']]
            order_item = OrderItem(
                order_id=order.id,
                food_item_id=food_item.id,
                quantity=item_data['quantity'],
                unit_price=food_item.price,
                subtotal=Decimal('0.00')  # Will be calculated by event
            )
            db.session.add(order_item)

        db.session.commit()
        db.session.refresh(order)  # Refresh to get calculated total

        return order

    def update_order_status(self, order_id: int, new_status: OrderStatus) -> Order:
        """Update order status with validation"""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        # Status transition validation
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.COMPLETED, OrderStatus.CANCELLED],
            OrderStatus.COMPLETED: [],
            OrderStatus.CANCELLED: []
        }

        if new_status not in valid_transitions[order.status]:
            raise ValueError(f"Cannot transition from {order.status} to {new_status}")

        order.status = new_status
        if new_status == OrderStatus.COMPLETED:
            order.mark_completed()

        db.session.commit()
        return order