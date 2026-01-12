from typing import Dict, Any, List
from decimal import Decimal

from website.models import User, Order, PointsTransactionType
from website.repositories import UserRepository, PointsRepository
from website.validators import ValidationResult
from utils import errhandler
from database import db


class PointsService:
    """Service for points management"""

    def __init__(
        self,
        user_repo: UserRepository = None,
        points_repo: PointsRepository = None
    ):
        self.user_repo = user_repo or UserRepository()
        self.points_repo = points_repo or PointsRepository()

    # Conversion rates (adjust as needed)
    POINTS_PER_DOLLAR = 10      # Earn 10 points per $1 spent
    POINTS_TO_DOLLAR = 100      # 100 points = $1 discount

    def calculate_points_from_amount(self, amount: Decimal) -> int:
        """Calculate points earned from order amount"""
        return int(float(amount) * self.POINTS_PER_DOLLAR)

    def calculate_discount_from_points(self, points: int) -> Decimal:
        """Calculate discount amount from points"""
        return Decimal(points / self.POINTS_TO_DOLLAR)

    def award_points_for_order(
        self,
        user_id: int,
        order: Order
    ) -> ValidationResult:
        """
        Award points to user after order completion.
        Call this when order status becomes COMPLETED.
        """
        try:
            user = self.user_repo.get_by_id(user_id)

            if not user:
                return ValidationResult.fail(
                    "User not found",
                    code="user_not_found"
                )

            # Calculate points (only on amount paid after discount)
            amount_for_points = order.total_amount - order.discount_amount
            points = self.calculate_points_from_amount(amount_for_points)

            # Award points
            self.user_repo.add_points(user, points)

            # Record transaction
            self.points_repo.create_transaction(
                user_id=user_id,
                transaction_type=PointsTransactionType.EARNED,
                points=points,
                order_id=order.id,
                description=f"Earned from order {order.order_number}"
            )

            # Update order
            order.points_earned = points
            db.session.commit()

            return ValidationResult.ok(
                message=f"Earned {points} points!",
                code="points_awarded",
                data={'points_earned': points, 'new_balance': user.points_balance}
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="points_service", path="services")
            return ValidationResult.fail(
                "Failed to award points",
                code="award_error"
            )

    def apply_points_discount(
        self,
        user_id: int,
        points_to_use: int,
        order_total: Decimal
    ) -> ValidationResult:
        """
        Apply points as discount to an order.
        Call this before order creation/confirmation.
        """
        try:
            user = self.user_repo.get_by_id(user_id)

            if not user:
                return ValidationResult.fail(
                    "User not found",
                    code="user_not_found"
                )

            # Check if user has enough points
            if user.points_balance < points_to_use:
                return ValidationResult.fail(
                    f"Insufficient points. You have {user.points_balance} points.",
                    code="insufficient_points"
                )

            # Calculate discount
            discount = self.calculate_discount_from_points(points_to_use)

            # Ensure discount doesn't exceed order total
            if discount > order_total:
                # Adjust points to match order total
                max_points = int(float(order_total) * self.POINTS_TO_DOLLAR)
                discount = order_total
                points_to_use = max_points

            return ValidationResult.ok(
                message=f"Discount applied: ${discount:.2f}",
                code="discount_applied",
                data={
                    'points_used': points_to_use,
                    'discount_amount': float(discount),
                    'new_balance': user.points_balance - points_to_use
                }
            )
        except Exception as e:
            errhandler(e, log="points_service", path="services")
            return ValidationResult.fail(
                "Failed to apply discount",
                code="discount_error"
            )

    def redeem_points_for_order(
        self,
        user_id: int,
        order: Order,
        points_to_use: int
    ) -> ValidationResult:
        """
        Redeem points for order discount.
        Call this when order is created/confirmed.
        """
        try:
            user = self.user_repo.get_by_id(user_id)

            if not user:
                return ValidationResult.fail(
                    "User not found",
                    code="user_not_found"
                )

            # Redeem points
            success = self.user_repo.redeem_points(user, points_to_use)

            if not success:
                return ValidationResult.fail(
                    "Failed to redeem points",
                    code="redemption_failed"
                )

            # Calculate discount
            discount = self.calculate_discount_from_points(points_to_use)

            # Record transaction
            self.points_repo.create_transaction(
                user_id=user_id,
                transaction_type=PointsTransactionType.REDEEMED,
                points=-points_to_use,  # Negative for redeemed
                order_id=order.id,
                description=f"Redeemed for order {order.order_number}"
            )

            # Update order
            order.points_redeemed = points_to_use
            order.discount_amount = discount
            db.session.commit()

            return ValidationResult.ok(
                message=f"Redeemed {points_to_use} points for ${discount:.2f} discount",
                code="points_redeemed",
                data={
                    'points_redeemed': points_to_use,
                    'discount_amount': float(discount),
                    'new_balance': user.points_balance
                }
            )
        except Exception as e:
            db.session.rollback()
            errhandler(e, log="points_service", path="services")
            return ValidationResult.fail(
                "Failed to redeem points",
                code="redemption_error"
            )

    def get_points_summary(self, user_id: int) -> Dict[str, Any]:
        """Get user's points summary"""
        try:
            user = self.user_repo.get_by_id(user_id)

            if not user:
                return {
                    'points_balance': 0,
                    'lifetime_points': 0,
                    'cash_value': 0.0,
                    'next_reward_points': 0
                }

            # Calculate cash value
            cash_value = user.points_to_cash()

            # Calculate points to next reward tier (example: every 1000 points)
            next_milestone = 1000
            points_to_next = next_milestone - (user.lifetime_points_earned % next_milestone)

            return {
                'points_balance': user.points_balance,
                'lifetime_points': user.lifetime_points_earned,
                'cash_value': round(cash_value, 2),
                'next_reward_points': points_to_next
            }
        except Exception as e:
            errhandler(e, log="points_service", path="services")
            return {
                'points_balance': 0,
                'lifetime_points': 0,
                'cash_value': 0.0,
                'next_reward_points': 0
            }

    def get_points_history(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get user's points transaction history"""
        try:
            transactions = self.points_repo.find_by_user(user_id, limit)

            return [
                {
                    'id': txn.id,
                    'type': txn.transaction_type.value,
                    'points': txn.points,
                    'description': txn.description,
                    'order_number': txn.order.order_number if txn.order else None,
                    'created_at': txn.created_at.isoformat()
                }
                for txn in transactions
            ]
        except Exception as e:
            errhandler(e, log="points_service", path="services")
            return []