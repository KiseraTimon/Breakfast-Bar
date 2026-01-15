from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.orm import joinedload

from website.models import (
    User, FoodItem, Category, Order, OrderItem,
    Review, PointsTransaction, OrderStatus, UserRole
)
from .base_repository import BaseRepository
from database import db


class AdminRepository(BaseRepository[User]):
    """Repository for admin-specific queries"""

    def __init__(self):
        super().__init__(User)

    # User Management
    def find_all_users(
        self,
        page: int = 1,
        per_page: int = 20,
        role: UserRole = None
    ) -> List[User]:
        """Get all users with optional role filter"""
        conditions = []
        if role:
            conditions.append(User.role == role)

        stmt = select(User)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = (
            stmt
            .order_by(desc(User.created_at))
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        return db.session.execute(stmt).scalars().all()

    def count_users(self, role: UserRole = None) -> int:
        """Count total users"""
        query = db.session.query(func.count(User.id))
        if role:
            query = query.filter(User.role == role)
        return query.scalar() or 0

    def search_users(self, search_term: str) -> List[User]:
        """Search users by name, email, or phone"""
        search_pattern = f'%{search_term}%'
        stmt = (
            select(User)
            .where(
                or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.phone.ilike(search_pattern)
                )
            )
            .limit(50)
        )
        return db.session.execute(stmt).scalars().all()

    # Analytics
    def get_revenue_stats(
        self,
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, Any]:
        """Get revenue statistics for date range"""
        query = db.session.query(
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_revenue'),
            func.avg(Order.total_amount).label('average_order_value'),
            func.sum(Order.discount_amount).label('total_discounts')
        ).filter(Order.status == OrderStatus.COMPLETED)

        if start_date:
            query = query.filter(func.date(Order.completed_at) >= start_date)
        if end_date:
            query = query.filter(func.date(Order.completed_at) <= end_date)

        result = query.first()

        return {
            'total_orders': result.total_orders or 0,
            'total_revenue': float(result.total_revenue or 0),
            'average_order_value': float(result.average_order_value or 0),
            'total_discounts': float(result.total_discounts or 0)
        }

    def get_daily_revenue(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Get daily revenue breakdown"""
        results = db.session.query(
            func.date(Order.completed_at).label('date'),
            func.count(Order.id).label('orders'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.status == OrderStatus.COMPLETED,
            func.date(Order.completed_at).between(start_date, end_date)
        ).group_by(
            func.date(Order.completed_at)
        ).order_by(
            func.date(Order.completed_at)
        ).all()

        return [
            {
                'date': str(r.date),
                'orders': r.orders,
                'revenue': float(r.revenue)
            }
            for r in results
        ]

    def get_top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top customers by total spending"""
        results = db.session.query(
            User.id,
            User.first_name,
            User.last_name,
            User.email,
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_spent')
        ).join(
            Order, Order.customer_id == User.id
        ).filter(
            Order.status == OrderStatus.COMPLETED
        ).group_by(
            User.id, User.first_name, User.last_name, User.email
        ).order_by(
            desc(func.sum(Order.total_amount))
        ).limit(limit).all()

        return [
            {
                'user_id': r.id,
                'name': f"{r.first_name} {r.last_name}",
                'email': r.email,
                'total_orders': r.total_orders,
                'total_spent': float(r.total_spent)
            }
            for r in results
        ]

    def get_popular_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most ordered food items"""
        results = db.session.query(
            FoodItem.id,
            FoodItem.name,
            FoodItem.price,
            func.count(OrderItem.id).label('times_ordered'),
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.subtotal).label('total_revenue')
        ).join(
            OrderItem, OrderItem.food_item_id == FoodItem.id
        ).join(
            Order, Order.id == OrderItem.order_id
        ).filter(
            Order.status == OrderStatus.COMPLETED
        ).group_by(
            FoodItem.id, FoodItem.name, FoodItem.price
        ).order_by(
            desc(func.sum(OrderItem.quantity))
        ).limit(limit).all()

        return [
            {
                'item_id': r.id,
                'name': r.name,
                'price': float(r.price),
                'times_ordered': r.times_ordered,
                'total_quantity': r.total_quantity,
                'total_revenue': float(r.total_revenue)
            }
            for r in results
        ]

    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        total_users = db.session.query(func.count(User.id)).scalar() or 0
        total_orders = db.session.query(func.count(Order.id)).scalar() or 0
        total_items = db.session.query(func.count(FoodItem.id)).scalar() or 0
        total_reviews = db.session.query(func.count(Review.id)).scalar() or 0

        active_users = db.session.query(func.count(User.id)).filter(
            User.is_verified == True
        ).scalar() or 0

        pending_orders = db.session.query(func.count(Order.id)).filter(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING])
        ).scalar() or 0

        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_items': total_items,
            'total_reviews': total_reviews
        }