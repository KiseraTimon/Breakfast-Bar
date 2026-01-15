from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from website.models import (
    User, FoodItem, Category, Order, Ingredient,
    OrderStatus, UserRole, PointsTransactionType
)
from website.repositories import (
    AdminRepository,
    UserRepository,
    FoodItemRepository,
    CategoryRepository,
    OrderRepository,
    PointsRepository
)
from website.validators import ValidationResult
from utils import errhandler
from database import db


class AdminService:
    """
    Service for admin operations.
    Handles users, menu, orders, and analytics.
    """

    def __init__(
        self,
        admin_repo: AdminRepository = None,
        user_repo: UserRepository = None,
        food_item_repo: FoodItemRepository = None,
        category_repo: CategoryRepository = None,
        order_repo: OrderRepository = None,
        points_repo: PointsRepository = None
    ):
        self.admin_repo = admin_repo or AdminRepository()
        self.user_repo = user_repo or UserRepository()
        self.food_item_repo = food_item_repo or FoodItemRepository()
        self.category_repo = category_repo or CategoryRepository()
        self.order_repo = order_repo or OrderRepository()
        self.points_repo = points_repo or PointsRepository()

    # Dashboard

    def get_admin_dashboard(self) -> Dict[str, Any]:
        """
        Get complete admin dashboard data.
        Overview of system performance.
        """
        try:
            # System stats
            system_stats = self.admin_repo.get_system_stats()

            # Revenue stats (last 30 days)
            thirty_days_ago = date.today() - timedelta(days=30)
            revenue_stats = self.admin_repo.get_revenue_stats(
                start_date=thirty_days_ago
            )

            # Top customers
            top_customers = self.admin_repo.get_top_customers(limit=5)

            # Popular items
            popular_items = self.admin_repo.get_popular_items(limit=5)

            # Recent orders
            recent_orders = self.get_recent_orders(limit=10)

            return {
                'system_stats': system_stats,
                'revenue_stats': revenue_stats,
                'top_customers': top_customers,
                'popular_items': popular_items,
                'recent_orders': recent_orders
            }
        except Exception as e:
            errhandler(e, log="admin_service", path="services")
            return {
                'system_stats': {},
                'revenue_stats': {},
                'top_customers': [],
                'popular_items': [],
                'recent_orders': []
            }

    def get_analytics_data(
        self,
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, Any]:
        """
        Get detailed analytics for date range.
        """
        try:
            # Default to last 30 days if not specified
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)

            # Revenue stats
            revenue_stats = self.admin_repo.get_revenue_stats(start_date, end_date)

            # Daily breakdown
            daily_revenue = self.admin_repo.get_daily_revenue(start_date, end_date)

            # Top items and customers
            top_customers = self.admin_repo.get_top_customers(limit=10)
            popular_items = self.admin_repo.get_popular_items(limit=10)

            return {
                'date_range': {
                    'start': str(start_date),
                    'end': str(end_date)
                },
                'summary': revenue_stats,
                'daily_revenue': daily_revenue,
                'top_customers': top_customers,
                'popular_items': popular_items
            }
        except Exception as e:
            errhandler(e, log="admin_service", path="services")
            return {
                'date_range': {},
                'summary': {},
                'daily_revenue': [],
                'top_customers': [],
                'popular_items': []
            }

    # User Management

    def get_all_users(
        self,
        page: int = 1,
        per_page: int = 20,
        role: UserRole = None
    ) -> Dict[str, Any]:
        """Get paginated list of users"""
        try:
            users = self.admin_repo.find_all_users(page, per_page, role)
            total = self.admin_repo.count_users(role)

            formatted_users = [
                {
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'phone': user.phone,
                    'role': user.role.value,
                    'is_verified': user.is_verified,
                    'is_active': getattr(user, 'is_active', True),
                    'points_balance': user.points_balance,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ]

            return {
                'users': formatted_users,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        except Exception as e:
            errhandler(e, log="admin_service", path="services")
            return {
                'users': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0
            }

    def get_user_details(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed user information"""
        try:
            user = self.user_repo.get_by_id(user_id)

            if not user:
                return None

            # Get user's order stats
            customer_id = getattr(user, 'customer_id', None) or user.id
            order_stats = self.order_repo.get_customer_metrics(customer_id)

            return {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role.value,
                'is_verified': user.is_verified,
                'is_active': getattr(user, 'is_active', True),
                'points_balance': user.points_balance,
                'lifetime_points': user.lifetime_points_earned,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
                'order_stats': order_stats
            }
        except Exception as e:
            errhandler(e, log="admin_service", path="services")
            return None

    def search_users(self, search_term: str) -> List[Dict[str, Any]]:
        """Search users by name, email, or phone"""
        try:
            users = self.admin_repo.search_users(search_term)

            return [
                {
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'phone': user.phone,
                    'role': user.role.value,
                    'is_verified': user.is_verified
                }
                for user in users
            ]
        except Exception as e:
            errhandler(e, log="admin_service", path="services")
            return []

    def update_user_role(
        self,
        user_id: int,
        new_role: UserRole
    ) -> ValidationResult:
        """Update user's role"""
        try:
            user = self.user_repo.get_by_id(user_id)

            if not user:
                return ValidationResult.fail("User not found", code="user_not_found")

            user.role = new_role
            db.session.commit()

            return ValidationResult.ok(
                message=f"User role updated to {new_role.value}",
                code="role_updated",
                obj=user
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="admin_service", path="services")
            return ValidationResult.fail(
                "Failed to update role",
                code="update_error"
            )

    def toggle_user_status(self, user_id: int) -> ValidationResult:
        """Activate/deactivate user account"""
        try:
            user = self.user_repo.get_by_id(user_id)

            if not user:
                return ValidationResult.fail("User not found", code="user_not_found")

            current_status = getattr(user, 'is_active', True)
            user.update_status(active=not current_status)
            db.session.commit()

            status_text = "activated" if not current_status else "deactivated"

            return ValidationResult.ok(
                message=f"User account {status_text}",
                code="status_updated",
                data={'is_active': not current_status}
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="admin_service", path="services")
            return ValidationResult.fail(
                "Failed to update status",
                code="update_error"
            )

    def adjust_user_points(
        self,
        user_id: int,
        points: int,
        description: str = None
    ) -> ValidationResult:
        """Manually adjust user's points (positive or negative)"""
        try:
            user = self.user_repo.get_by_id(user_id)

            if not user:
                return ValidationResult.fail("User not found", code="user_not_found")

            # Update balance
            if points > 0:
                user.add_points(points)
            else:
                user.redeem_points(abs(points))

            # Record transaction
            self.points_repo.create_transaction(
                user_id=user_id,
                transaction_type=PointsTransactionType.ADJUSTED,
                points=points,
                description=description or f"Admin adjustment: {points} points"
            )

            db.session.commit()

            return ValidationResult.ok(
                message=f"Points adjusted by {points}",
                code="points_adjusted",
                data={'new_balance': user.points_balance}
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="admin_service", path="services")
            return ValidationResult.fail(
                "Failed to adjust points",
                code="adjustment_error"
            )

    # Food Item Management

    def get_all_food_items(
        self,
        page: int = 1,
        per_page: int = 20,
        category_id: int = None
    ) -> Dict[str, Any]:
        """Get all food items with pagination"""
        try:
            if category_id:
                items = self.food_item_repo.find_by_category(
                    category_id=category_id,
                    available_only=False,
                    page=page,
                    per_page=per_page
                )
                total = self.food_item_repo.count_by_category(category_id, available_only=False)
            else:
                items = self.food_item_repo.find_all_available(page, per_page)
                total = self.food_item_repo.count_available()

            formatted_items = [
                {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'price': float(item.price),
                    'category_id': item.category_id,
                    'category_name': item.category.name,
                    'is_available': item.is_available,
                    'image_url': item.image_url,
                    'created_at': item.created_at.isoformat() if item.created_at else None
                }
                for item in items
            ]

            return {
                'items': formatted_items,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        except Exception as e:
            errhandler(e, log="admin_service", path="services")
            return {
                'items': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0
            }

    def create_food_item(
        self,
        name: str,
        description: str,
        price: Decimal,
        category_id: int,
        image_url: str = None,
        ingredients: List[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Create new food item"""
        try:
            # Validate category exists
            category = self.category_repo.get_by_id(category_id)
            if not category:
                return ValidationResult.fail(
                    "Category not found",
                    code="category_not_found"
                )

            # Create food item
            food_item = FoodItem(
                name=name,
                description=description,
                price=price,
                category_id=category_id,
                image_url=image_url,
                is_available=True
            )

            # Add ingredients if provided
            if ingredients:
                for ing_data in ingredients:
                    ingredient = Ingredient(
                        name=ing_data['name'],
                        is_allergen=ing_data.get('is_allergen', False)
                    )
                    food_item.ingredients.append(ingredient)

            created_item = self.food_item_repo.create(food_item)

            return ValidationResult.ok(
                message="Food item created successfully",
                code="item_created",
                obj=created_item
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="admin_service", path="services")
            return ValidationResult.fail(
                "Failed to create food item",
                code="create_error"
            )

    def update_food_item(
        self,
        item_id: int,
        name: str = None,
        description: str = None,
        price: Decimal = None,
        category_id: int = None,
        image_url: str = None,
        is_available: bool = None
    ) -> ValidationResult:
        """Update existing food item"""
        try:
            item = self.food_item_repo.get_by_id(item_id)

            if not item:
                return ValidationResult.fail("Item not found", code="item_not_found")

            # Update fields
            if name is not None:
                item.name = name
            if description is not None:
                item.description = description
            if price is not None:
                item.price = price
            if category_id is not None:
                item.category_id = category_id
            if image_url is not None:
                item.image_url = image_url
            if is_available is not None:
                item.is_available = is_available

            updated_item = self.food_item_repo.update(item)

            return ValidationResult.ok(
                message="Food item updated successfully",
                code="item_updated",
                obj=updated_item
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="admin_service", path="services")
            return ValidationResult.fail(
                "Failed to update food item",
                code="update_error"
            )

    def delete_food_item(self, item_id: int) -> ValidationResult:
        """Delete food item"""
        try:
            item = self.food_item_repo.get_by_id(item_id)

            if not item:
                return ValidationResult.fail("Item not found", code="item_not_found")

            self.food_item_repo.delete(item)

            return ValidationResult.ok(
                message="Food item deleted successfully",
                code="item_deleted"
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="admin_service", path="services")
            return ValidationResult.fail(
                "Failed to delete food item",
                code="delete_error"
            )

    # Category Management

    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        try:
            categories = self.category_repo.find_all_active()

            return [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'description': cat.description,
                    'sort_order': cat.sort_order,
                    'is_active': cat.is_active
                }
                for cat in categories
            ]
        except Exception as e:
            errhandler(e, log="admin_service", path="services")
            return []

    def create_category(
        self,
        name: str,
        description: str = None,
        sort_order: int = 0
    ) -> ValidationResult:
        """Create new category"""
        try:
            category = Category(
                name=name,
                description=description,
                sort_order=sort_order,
                is_active=True
            )

            created_category = self.category_repo.create(category)

            return ValidationResult.ok(
                message="Category created successfully",
                code="category_created",
                obj=created_category
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="admin_service", path="services")
            return ValidationResult.fail(
                "Failed to create category",
                code="create_error"
            )

    def update_category(
        self,
        category_id: int,
        name: str = None,
        description: str = None,
        sort_order: int = None,
        is_active: bool = None
    ) -> ValidationResult:
        """Update existing category"""
        try:
            category = self.category_repo.get_by_id(category_id)

            if not category:
                return ValidationResult.fail("Category not found", code="category_not_found")

            if name is not None:
                category.name = name
            if description is not None:
                category.description = description
            if sort_order is not None:
                category.sort_order = sort_order
            if is_active is not None:
                category.is_active = is_active

            updated_category = self.category_repo.update(category)

            return ValidationResult.ok(
                message="Category updated successfully",
                code="category_updated",
                obj=updated_category
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="admin_service", path="services")
            return ValidationResult.fail(
                "Failed to update category",
                code="update_error"
            )

    # Order Management

    def get_all_orders(
        self,
        page: int = 1,
        per_page: int = 20,
        status: OrderStatus = None
    ) -> Dict[str, Any]:
        """Get all orders with optional status filter"""
        try:
            # This would need a method in OrderRepository
            # For now, using a simple query
            query = db.session.query(Order)

            if status:
                query = query.filter(Order.status == status)

            total = query.count()

            orders = (
                query
                .order_by(desc(Order.created_at))
                .limit(per_page)
                .offset((page - 1) * per_page)
                .all()
            )

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
            errhandler(e, log="admin_service", path="services")
            return {
                'orders': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0
            }

    def get_recent_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent orders"""
        try:
            orders = (
                db.session.query(Order)
                .order_by(desc(Order.created_at))
                .limit(limit)
                .all()
            )

            return [self._format_order(order) for order in orders]
        except Exception as e:
            errhandler(e, log="admin_service", path="services")
            return []

    def update_order_status(
        self,
        order_id: int,
        new_status: OrderStatus
    ) -> ValidationResult:
        """Update order status"""
        try:
            order = self.order_repo.get_by_id(order_id)

            if not order:
                return ValidationResult.fail("Order not found", code="order_not_found")

            old_status = order.status
            order.status = new_status

            # If completed, mark timestamp
            if new_status == OrderStatus.COMPLETED:
                order.mark_completed()

                # Award points if not already awarded
                if order.points_earned == 0:
                    from website.services import PointsService
                    points_service = PointsService()
                    points_service.award_points_for_order(
                        user_id=order.customer_id,
                        order=order
                    )

            db.session.commit()

            return ValidationResult.ok(
                message=f"Order status updated from {old_status.value} to {new_status.value}",
                code="status_updated",
                obj=order
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="admin_service", path="services")
            return ValidationResult.fail(
                "Failed to update order status",
                code="update_error"
            )

    def _format_order(self, order: Order) -> Dict[str, Any]:
        """Format order for display"""
        return {
            'id': order.id,
            'order_number': order.order_number,
            'customer_name': f"{order.customer.name}" if order.customer else "Walk-in",
            'total_amount': float(order.total_amount),
            'discount_amount': float(order.discount_amount),
            'status': order.status.value,
            'order_type': order.order_type.value,
            'created_at': order.created_at.isoformat(),
            'completed_at': order.completed_at.isoformat() if order.completed_at else None,
            'items_count': len(order.order_items)
        }