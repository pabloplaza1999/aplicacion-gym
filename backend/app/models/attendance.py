"""Attendance model — one check-in per membership per day for voucher memberships."""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Date, ForeignKey, UniqueConstraint
from app.models.base import Base


class Attendance(Base):
    """Attendance (check-in) record. Single source of truth for voucher consumption."""

    __tablename__ = "attendances"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    membership_id = Column(Integer, ForeignKey("memberships.id"), nullable=False, index=True)

    # Timestamps
    check_in_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    check_in_date = Column(Date, nullable=False, index=True)

    # Max one attendance per membership per calendar day (scoped to membership, not member globally).
    __table_args__ = (
        UniqueConstraint("membership_id", "check_in_date", name="uq_attendance_membership_day"),
    )

    def __repr__(self) -> str:
        return (
            f"<Attendance(id={self.id}, member_id={self.member_id}, "
            f"membership_id={self.membership_id}, date={self.check_in_date})>"
        )
