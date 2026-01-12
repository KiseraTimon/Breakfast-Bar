from sqlalchemy import String, Enum as SQLEnum, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from .base import TimestampMixin
import enum
from datetime import datetime, timezone

from flask_login import UserMixin

class UserRole(enum.Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"

class User(db.Model, TimestampMixin, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.CUSTOMER
    )
    is_verified: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    points_balance: Mapped[int] = mapped_column(default=0, nullable=False)
    lifetime_points_earned: Mapped[int] = mapped_column(default=0, nullable=False)

    # Relationships
    favorites = relationship('Favorite', back_populates='user', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='user', cascade='all, delete-orphan')

    # Indexes for performance
    __table_args__ = (
        Index('idx_user_role_active', 'role', 'is_verified'),
    )

    def set_password(self, password: str):
        """Hash password for security"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Track user activity"""
        self.last_login_at = datetime.now(timezone.utc)
        db.session.commit()

    def update_status(self, active: bool = False):
        """Modifies User Account Status"""
        self.is_verified = active
        db.session.commit()

    def add_points(self, points: int) -> None:
        """Add points to user balance"""
        self.points_balance += points
        self.lifetime_points_earned += points

    def redeem_points(self, points: int) -> bool:
        """Redeem points (returns False if insufficient balance)"""
        if self.points_balance >= points:
            self.points_balance -= points
            return True
        return False

    def points_to_cash(self, points: int = None) -> float:
        """
        Convert points to cash value.
        Default: 100 points = KES 100
        """
        points_to_convert = points if points is not None else self.points_balance
        return points_to_convert / 100.0  # 100 points = KES 100

    def __repr__(self):
        return f'<User {self.email}>'