# repositories/order_repository.py
from typing import List
from datetime import date, datetime
from sqlalchemy import select, func
from models.order import Order, OrderStatus
from models.order_item import OrderItem
from models.food_item import FoodItem
from repositories.base_repository import BaseRepository
from database import db

class OrderRepository(BaseRepository[Order]):

    def __init__(self):
        super().__init__(Order)

    def get_by_order_number(self, order_number: str) -> Order | None:
        """Get order by order number"""
        stmt = select(Order).where(Order.order_number == order_number)
        return db.session.execute(stmt).scalar_one_or_none()

    def get_by_customer(self, customer_id: int, page: int = 1, per_page: int = 20) -> List[Order]:
        """Get all orders for a customer"""
        stmt = (
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        return db.session.execute(stmt).scalars().all()

    def get_by_status(self, status: OrderStatus) -> List[Order]:
        """Get orders by status (for kitchen display)"""
        stmt = (
            select(Order)
            .where(Order.status == status)
            .order_by(Order.created_at.asc())
        )
        return db.session.execute(stmt).scalars().all()

    def get_daily_revenue(self, target_date: date) -> float:
        """Get total revenue for a specific date"""
        stmt = (
            select(func.sum(Order.total_amount))
            .where(
                func.date(Order.completed_at) == target_date,
                Order.status == OrderStatus.COMPLETED
            )
        )
        result = db.session.execute(stmt).scalar()
        return float(result) if result else 0.0

    def get_top_selling_items(self, start_date: date, end_date: date, limit: int = 10) -> List[dict]:
        """Get top selling items in date range"""
        stmt = (
            select(
                FoodItem.id,
                FoodItem.name,
                func.sum(OrderItem.quantity).label('total_quantity'),
                func.sum(OrderItem.subtotal).label('total_revenue')
            )
            .join(OrderItem, OrderItem.food_item_id == FoodItem.id)
            .join(Order, Order.id == OrderItem.order_id)
            .where(
                func.date(Order.completed_at).between(start_date, end_date),
                Order.status == OrderStatus.COMPLETED
            )
            .group_by(FoodItem.id, FoodItem.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )

        results = db.session.execute(stmt).all()
        return [
            {
                'id': r.id,
                'name': r.name,
                'total_quantity': r.total_quantity,
                'total_revenue': float(r.total_revenue)
            }
            for r in results
        ]