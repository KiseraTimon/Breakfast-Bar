from typing import Dict, List, Optional, Any
from datetime import datetime

from website.models import User, Order, Favorite, Review
from website.repositories import (
    UserRepository,
    OrderRepository,
    FavoriteRepository,
    ReviewRepository
)
from website.validators import ValidationResult
from utils import errhandler
from database import db


class DashboardService:
    """
    Service for user dashboard operations.
    Orchestrates data from multiple repositories.
    """

    def __init__(
        self,
        user_repo: UserRepository = None,
        order_repo: OrderRepository = None,
        favorite_repo: FavoriteRepository = None,
        review_repo: ReviewRepository = None
    ):
        self.user_repo = user_repo or UserRepository()
        self.order_repo = order_repo or OrderRepository()
        self.favorite_repo = favorite_repo or FavoriteRepository()
        self.review_repo = review_repo or ReviewRepository()

    # User Details
    def get_user_details(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user profile details.
        Returns formatted user information.
        """
        try:
            user = self.user_repo.get_by_id(user_id)

            if not user:
                return None

            return {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'phone': user.phone,
                'is_verified': user.is_verified,
                'is_active': getattr(user, 'is_active', True),
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
            }
        except Exception as e:
            errhandler(e, log="dashboard_service", path="services")
            return None

    def update_user_profile(
        self,
        user_id: int,
        first_name: str = None,
        last_name: str = None,
        phone: str = None
    ) -> ValidationResult:
        """
        Update user profile information.
        """
        try:
            user = self.user_repo.get_by_id(user_id)

            if not user:
                return ValidationResult.fail(
                    "User not found",
                    code="user_not_found"
                )

            # Update fields
            updated_user = self.user_repo.update_profile(
                user=user,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )

            return ValidationResult.ok(
                message="Profile updated successfully",
                code="profile_updated",
                obj=updated_user
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="dashboard_service", path="services")
            return ValidationResult.fail(
                "Failed to update profile",
                code="update_error"
            )

    # User Metrics

    def get_user_metrics(self, user_id: int) -> Dict[str, Any]:
        """
        Get user dashboard metrics.
        Returns aggregated statistics.
        """
        try:
            # Get customer_id (assuming User has customer relationship)
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return self._empty_metrics()

            # TODO: Assuming user has a customer relationship or customer_id. To be adjusted based on the actual model structure
            customer_id = getattr(user, 'customer_id', None) or user.id

            # Get order metrics
            order_metrics = self.order_repo.get_customer_metrics(customer_id)

            # Get favorites count
            favorites_count = self.favorite_repo.count_by_user(user_id)

            # Get reviews count
            reviews_count = self.review_repo.count_by_user(user_id)

            # Get active orders count
            active_orders = len(self.order_repo.get_orders_by_status(
                customer_id,
                OrderStatus.PENDING
            )) + len(self.order_repo.get_orders_by_status(
                customer_id,
                OrderStatus.PREPARING
            ))

            return {
                'total_orders': order_metrics['total_orders'],
                'total_spent': order_metrics['total_spent'],
                'average_order_value': order_metrics['avg_order_value'],
                'favorites_count': favorites_count,
                'reviews_count': reviews_count,
                'active_orders_count': active_orders
            }
        except Exception as e:
            errhandler(e, log="dashboard_service", path="services")
            return self._empty_metrics()

    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            'total_orders': 0,
            'total_spent': 0.0,
            'average_order_value': 0.0,
            'favorites_count': 0,
            'reviews_count': 0,
            'active_orders_count': 0
        }

    # Orders
    def get_user_orders(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """
        Get paginated order history for user.
        """
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return {'orders': [], 'total': 0, 'page': page, 'per_page': per_page}

            customer_id = getattr(user, 'customer_id', None) or user.id

            # Get orders
            orders = self.order_repo.find_by_customer(customer_id, page, per_page)

            # Get total count
            total = self.order_repo.count_by_customer(customer_id)

            # Format orders
            formatted_orders = [
                self._format_order(order) for order in orders
            ]

            return {
                'orders': formatted_orders,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        except Exception as e:
            errhandler(e, log="dashboard_service", path="services")
            return {'orders': [], 'total': 0, 'page': page, 'per_page': per_page}

    def get_recent_orders(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most recent orders for dashboard overview"""
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return []

            customer_id = getattr(user, 'customer_id', None) or user.id

            orders = self.order_repo.get_recent_orders(customer_id, limit)
            return [self._format_order(order) for order in orders]
        except Exception as e:
            errhandler(e, log="dashboard_service", path="services")
            return []

    def get_active_orders(self, user_id: int) -> List[Dict[str, Any]]:
        """Get currently active orders (pending, preparing)"""
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return []

            customer_id = getattr(user, 'customer_id', None) or user.id

            pending = self.order_repo.get_orders_by_status(customer_id, OrderStatus.PENDING)
            preparing = self.order_repo.get_orders_by_status(customer_id, OrderStatus.PREPARING)

            all_active = pending + preparing
            return [self._format_order(order) for order in all_active]
        except Exception as e:
            errhandler(e, log="dashboard_service", path="services")
            return []

    def _format_order(self, order: Order) -> Dict[str, Any]:
        """Format order object for display"""
        return {
            'id': order.id,
            'order_number': order.order_number,
            'total_amount': float(order.total_amount),
            'status': order.status.value,
            'order_type': order.order_type.value,
            'created_at': order.created_at.isoformat(),
            'completed_at': order.completed_at.isoformat() if order.completed_at else None,
            'items': [
                {
                    'id': item.food_item_id,
                    'name': item.food_item.name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'subtotal': float(item.subtotal)
                }
                for item in order.order_items
            ]
        }

    # Favorite Items
    def get_user_favorites(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all user favorites"""
        try:
            favorites = self.favorite_repo.find_by_user(user_id)

            return [
                {
                    'id': fav.food_item_id,
                    'name': fav.food_item.name,
                    'description': fav.food_item.description,
                    'price': float(fav.food_item.price),
                    'image_url': fav.food_item.image_url,
                    'is_available': fav.food_item.is_available,
                    'favorited_at': fav.created_at.isoformat()
                }
                for fav in favorites
            ]
        except Exception as e:
            errhandler(e, log="dashboard_service", path="services")
            return []

    def toggle_favorite(
        self,
        user_id: int,
        food_item_id: int
    ) -> ValidationResult:
        """
        Add or remove item from favorites.
        Returns ValidationResult with action taken.
        """
        try:
            is_favorited = self.favorite_repo.is_favorited(user_id, food_item_id)

            if is_favorited:
                # Remove favorite
                self.favorite_repo.remove_favorite(user_id, food_item_id)
                return ValidationResult.ok(
                    message="Removed from favorites",
                    code="favorite_removed",
                    data={'action': 'removed', 'is_favorited': False}
                )
            else:
                # Add favorite
                self.favorite_repo.add_favorite(user_id, food_item_id)
                return ValidationResult.ok(
                    message="Added to favorites",
                    code="favorite_added",
                    data={'action': 'added', 'is_favorited': True}
                )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="dashboard_service", path="services")
            return ValidationResult.fail(
                "Failed to update favorites",
                code="favorite_error"
            )

    # Reviews
    def get_user_reviews(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all user reviews"""
        try:
            reviews = self.review_repo.find_by_user(user_id)

            return [
                {
                    'id': review.id,
                    'food_item_id': review.food_item_id,
                    'food_item_name': review.food_item.name,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat(),
                    'updated_at': review.updated_at.isoformat() if hasattr(review, 'updated_at') else None
                }
                for review in reviews
            ]
        except Exception as e:
            errhandler(e, log="dashboard_service", path="services")
            return []

    # Complete Dashboard Data
    def get_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get complete dashboard data in one call.
        Optimized to reduce multiple round trips.
        """
        try:
            return {
                'user': self.get_user_details(user_id),
                'metrics': self.get_user_metrics(user_id),
                'recent_orders': self.get_recent_orders(user_id, limit=5),
                'active_orders': self.get_active_orders(user_id),
                'favorites': self.get_user_favorites(user_id),
                'reviews': self.get_user_reviews(user_id)
            }
        except Exception as e:
            errhandler(e, log="dashboard_service", path="services")
            return {
                'user': None,
                'metrics': self._empty_metrics(),
                'recent_orders': [],
                'active_orders': [],
                'favorites': [],
                'reviews': []
            }