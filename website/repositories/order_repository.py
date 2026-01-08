# repositories/order_repository.py
from typing import List, Dict, Optional
from datetime import date, datetime
from sqlalchemy import select, func, desc
from sqlalchemy.orm import joinedload
from website.models import Order, OrderStatus, OrderItem, FoodItem
from . import BaseRepository
from database import db

class OrderRepository(BaseRepository[Order]):

    def __init__(self):
        super().__init__(Order)

    def get_by_order_number(self, order_number: str) -> Order | None:
        """Get order by order number"""
        stmt = select(Order).where(Order.order_number == order_number)
        return db.session.execute(stmt).scalar_one_or_none()

    def find_by_customer(
        self,
        customer_id: int,
        page: int = 1,
        per_page: int = 10
    ) -> List[Order]:
        """Get orders for a specific customer with pagination"""
        stmt = (
            select(Order)
            .where(Order.customer_id == customer_id)
            .options(joinedload(Order.order_items).joinedload(OrderItem.food_item))
            .order_by(desc(Order.created_at))
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        return db.session.execute(stmt).scalars().unique().all()

    def get_orders_by_status(
        self,
        customer_id: int,
        status: OrderStatus
    ) -> List[Order]:
        """Get orders by status for a customer"""
        stmt = (
            select(Order)
            .where(
                Order.customer_id == customer_id,
                Order.status == status
            )
            .options(joinedload(Order.order_items).joinedload(OrderItem.food_item))
            .order_by(desc(Order.created_at))
        )
        return db.session.execute(stmt).scalars().unique().all()

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

    def count_by_customer(self, customer_id: int) -> int:
        """Count total orders for a customer"""
        return db.session.query(func.count(Order.id)).filter(
            Order.customer_id == customer_id
        ).scalar() or 0

    def get_customer_metrics(self, customer_id: int) -> Dict[str, any]:
        """
        Get aggregated metrics for a customer.
        Returns total orders, total spent, average order value.
        """
        result = db.session.query(
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_spent'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(
            Order.customer_id == customer_id,
            Order.status == OrderStatus.COMPLETED
        ).first()

        return {
            'total_orders': result.total_orders or 0,
            'total_spent': float(result.total_spent or 0),
            'avg_order_value': float(result.avg_order_value or 0)
        }

    def get_recent_orders(
        self,
        customer_id: int,
        limit: int = 5
    ) -> List[Order]:
        """Get most recent orders for a customer"""
        stmt = (
            select(Order)
            .where(Order.customer_id == customer_id)
            .options(joinedload(Order.order_items).joinedload(OrderItem.food_item))
            .order_by(desc(Order.created_at))
            .limit(limit)
        )
        return db.session.execute(stmt).scalars().unique().all()

    def get_order_history_summary(
        self,
        customer_id: int,
        days: int = 30
    ) -> List[Dict[str, any]]:
        """
        Get order history summary grouped by date.
        Returns list of {date, count, total} for last N days.
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        results = db.session.query(
            func.date(Order.created_at).label('order_date'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_amount')
        ).filter(
            Order.customer_id == customer_id,
            Order.created_at >= cutoff_date,
            Order.status == OrderStatus.COMPLETED
        ).group_by(
            func.date(Order.created_at)
        ).order_by(
            func.date(Order.created_at)
        ).all()

        return [
            {
                'date': str(r.order_date),
                'count': r.order_count,
                'total': float(r.total_amount)
            }
            for r in results
        ]