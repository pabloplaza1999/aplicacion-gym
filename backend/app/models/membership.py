"""Membership model."""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Boolean
from app.models.base import Base


class Membership(Base):
    """Membership model for member subscriptions."""

    __tablename__ = "memberships"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False, index=True)

    # Fields
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="active", nullable=False, index=True)
    freeze_days = Column(Integer, default=0, nullable=False)
    # Manual on/off switch, independent of dates and of the member's own state.
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    # Entries granted by a voucher membership (valera). NULL = date-based membership.
    entries_total = Column(Integer, nullable=True)
    # Freeze/pause support: set when membership is frozen; cleared on unfreeze.
    frozen_at = Column(DateTime, nullable=True)
    frozen_days_remaining = Column(Integer, nullable=True)
    # Counts completed freeze cycles for this membership (incremented on each unfreeze).
    freeze_count = Column(Integer, default=0, nullable=False)
    # Internal notification control: set by the notification job when an expiry alert is sent.
    # Never written by membership services, routes, or frontend.
    last_notified_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Membership(id={self.id}, member_id={self.member_id}, "
            f"plan_id={self.plan_id}, status='{self.status}')>"
        )
