"""MembershipCorrectionLog model — immutable audit trail for start_date corrections."""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from app.models.base import Base


class MembershipCorrectionLog(Base):
    """Immutable audit record written each time a membership's start_date is corrected."""

    __tablename__ = "membership_correction_logs"

    id = Column(Integer, primary_key=True, index=True)
    membership_id = Column(Integer, ForeignKey("memberships.id"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    old_start_date = Column(DateTime, nullable=False)
    new_start_date = Column(DateTime, nullable=False)
    old_end_date = Column(DateTime, nullable=False)
    new_end_date = Column(DateTime, nullable=False)
    # Only populated for frozen memberships (RN-10).
    old_frozen_days_remaining = Column(Integer, nullable=True)
    new_frozen_days_remaining = Column(Integer, nullable=True)
    reason = Column(String, nullable=False)
    corrected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
