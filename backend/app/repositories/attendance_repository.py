"""Attendance repository — data access for check-ins.

The attendances table is the single source of truth for voucher consumption:
entries used = COUNT(attendances for the membership). No duplicate counters.
"""

from datetime import datetime, date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.attendance import Attendance


class AttendanceRepository:
    """Repository for attendance data access operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        member_id: int,
        membership_id: int,
        check_in_at: datetime,
        check_in_date: date,
    ) -> Attendance:
        """Create a new attendance record."""
        attendance = Attendance(
            member_id=member_id,
            membership_id=membership_id,
            check_in_at=check_in_at,
            check_in_date=check_in_date,
        )
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        return attendance

    def count_by_membership(self, membership_id: int) -> int:
        """Number of entries consumed by a membership (source of truth)."""
        return (
            self.db.query(func.count(Attendance.id))
            .filter(Attendance.membership_id == membership_id)
            .scalar()
        ) or 0

    def exists_for_member_on_date(self, member_id: int, day: date) -> bool:
        """True if the member already has an attendance on the given day."""
        return (
            self.db.query(Attendance.id)
            .filter(
                Attendance.member_id == member_id,
                Attendance.check_in_date == day,
            )
            .first()
            is not None
        )

    def list_by_membership(self, membership_id: int) -> list[Attendance]:
        """All attendances of a membership, most recent first."""
        return (
            self.db.query(Attendance)
            .filter(Attendance.membership_id == membership_id)
            .order_by(Attendance.check_in_at.desc())
            .all()
        )
