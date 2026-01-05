from datetime import datetime, timezone
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database import db

class TimestampMixin:
    """Timestamp tracking"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

class AuditMixin(TimestampMixin):
    """Extended audit trail with user tracking"""
    created_by: Mapped[int | None] = mapped_column(db.ForeignKey('users.id'))
    updated_by: Mapped[int | None] = mapped_column(db.ForeignKey('users.id'))