"""Repository for membership_correction_logs (immutable audit records)."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.membership_correction import MembershipCorrectionLog


class MembershipCorrectionRepository:
    """Data access for membership_correction_logs.

    Records are immutable: no update or delete methods are exposed.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        membership_id: int,
        member_id: int,
        old_start_date: datetime,
        new_start_date: datetime,
        old_end_date: datetime,
        new_end_date: datetime,
        old_frozen_days_remaining: Optional[int],
        new_frozen_days_remaining: Optional[int],
        reason: str,
    ) -> MembershipCorrectionLog:
        """Insert a correction audit record. Caller owns the commit."""
        log = MembershipCorrectionLog(
            membership_id=membership_id,
            member_id=member_id,
            old_start_date=old_start_date,
            new_start_date=new_start_date,
            old_end_date=old_end_date,
            new_end_date=new_end_date,
            old_frozen_days_remaining=old_frozen_days_remaining,
            new_frozen_days_remaining=new_frozen_days_remaining,
            reason=reason,
            corrected_at=datetime.utcnow(),
        )
        self.db.add(log)
        self.db.flush()
        return log

    def get_latest_for_membership(self, membership_id: int) -> Optional[MembershipCorrectionLog]:
        """Return the most recent correction log for a membership, or None."""
        return (
            self.db.query(MembershipCorrectionLog)
            .filter(MembershipCorrectionLog.membership_id == membership_id)
            .order_by(MembershipCorrectionLog.corrected_at.desc())
            .first()
        )
