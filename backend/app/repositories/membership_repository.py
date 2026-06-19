"""Membership repository for data access."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.models.plan import Plan


class MembershipRepository:
    """Repository for membership data access operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create(
        self,
        member_id: int,
        plan_id: int,
        start_date: datetime,
        end_date: datetime,
        entries_total: Optional[int] = None,
    ) -> Membership:
        """
        Create a new membership.

        Args:
            member_id: Member ID
            plan_id: Plan ID
            start_date: Start date
            end_date: End date
            entries_total: Entries granted for voucher memberships (None otherwise)

        Returns:
            Created membership instance
        """
        membership = Membership(
            member_id=member_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            status="active",
            entries_total=entries_total,
        )
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def get_by_id(self, membership_id: int) -> Optional[Membership]:
        """Get membership by ID."""
        return self.db.query(Membership).filter(Membership.id == membership_id).first()

    def get_by_member_id(self, member_id: int, skip: int = 0, limit: int = 100) -> list[Membership]:
        """
        Get all memberships for a member.

        Args:
            member_id: Member ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of memberships
        """
        return (
            self.db.query(Membership)
            .filter(Membership.member_id == member_id)
            .order_by(Membership.start_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_member_id_count(self, member_id: int) -> int:
        """Get count of memberships for a member."""
        return self.db.query(Membership).filter(Membership.member_id == member_id).count()

    def get_active_membership(self, member_id: int) -> Optional[Membership]:
        """
        Get the current (most recent) membership for a member.

        Returns:
            Most recent membership or None if none exists
        """
        return (
            self.db.query(Membership)
            .filter(Membership.member_id == member_id)
            .order_by(Membership.start_date.desc(), Membership.id.desc())
            .first()
        )

    def get_expiring_soon(self, days: int = 5) -> list[Membership]:
        """
        Get memberships expiring within the specified number of days.

        Args:
            days: Number of days to check

        Returns:
            List of expiring memberships
        """
        from datetime import timedelta

        today = datetime.utcnow()
        end_date_threshold = today + timedelta(days=days)

        return (
            self.db.query(Membership)
            .filter(
                Membership.end_date >= today,
                Membership.end_date <= end_date_threshold,
            )
            .order_by(Membership.end_date.asc())
            .all()
        )

    def update(self, membership_id: int, **kwargs) -> Optional[Membership]:
        """
        Update a membership.

        Args:
            membership_id: Membership ID
            **kwargs: Fields to update

        Returns:
            Updated membership or None if not found
        """
        membership = self.get_by_id(membership_id)
        if not membership:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(membership, key):
                setattr(membership, key, value)

        self.db.commit()
        self.db.refresh(membership)
        return membership

    def set_active(self, membership_id: int, is_active: bool) -> Optional[Membership]:
        """Manually set a membership's active flag."""
        membership = self.get_by_id(membership_id)
        if not membership:
            return None
        membership.is_active = is_active
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def freeze(self, membership_id: int, frozen_at: datetime, frozen_days_remaining: int) -> Optional[Membership]:
        """Freeze a membership: store freeze timestamp, days remaining, and deactivate."""
        membership = self.get_by_id(membership_id)
        if not membership:
            return None
        membership.frozen_at = frozen_at
        membership.frozen_days_remaining = frozen_days_remaining
        membership.is_active = False
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def unfreeze(self, membership_id: int, new_end_date: datetime, freeze_days_delta: int) -> Optional[Membership]:
        """Unfreeze a membership: restore end_date, accumulate freeze_days, clear freeze fields."""
        membership = self.get_by_id(membership_id)
        if not membership:
            return None
        membership.end_date = new_end_date
        membership.freeze_days = (membership.freeze_days or 0) + freeze_days_delta
        membership.freeze_count = (membership.freeze_count or 0) + 1
        membership.frozen_at = None
        membership.frozen_days_remaining = None
        membership.is_active = True
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def deactivate_no_commit(self, membership_id: int) -> None:
        """Set is_active=False without committing — caller owns the transaction."""
        membership = self.get_by_id(membership_id)
        if membership:
            membership.is_active = False
            self.db.flush()

    def get_active_voucher_membership(self, member_id: int) -> Optional[Membership]:
        """
        Get the member's most recent ACTIVE voucher membership.

        Filters by plan_type == "voucher" and is_active == True. Date/entry
        validations are left to the service so it can return precise messages.
        """
        return (
            self.db.query(Membership)
            .join(Plan, Membership.plan_id == Plan.id)
            .filter(
                Membership.member_id == member_id,
                Membership.is_active == True,  # noqa: E712
                Plan.plan_type == "voucher",
            )
            .order_by(Membership.start_date.desc())
            .first()
        )

    def get_active_non_voucher_membership(
        self, member_id: int, exclude_id: Optional[int] = None
    ) -> Optional[Membership]:
        """Get the member's most recent active non-voucher (monthly/daily/premium) membership.

        Used to enforce the one-active-non-voucher rule in create_membership and
        set_membership_active. Pass exclude_id to skip the membership being evaluated.
        """
        q = (
            self.db.query(Membership)
            .join(Plan, Membership.plan_id == Plan.id)
            .filter(
                Membership.member_id == member_id,
                Membership.is_active == True,  # noqa: E712
                Plan.plan_type != "voucher",
            )
        )
        if exclude_id is not None:
            q = q.filter(Membership.id != exclude_id)
        return q.order_by(Membership.start_date.desc(), Membership.id.desc()).first()

    def get_plan_by_id(self, plan_id: int) -> Optional[Plan]:
        """Get plan details by ID."""
        return self.db.query(Plan).filter(Plan.id == plan_id).first()

    def get_active_overlapping(
        self,
        member_id: int,
        new_start_dt: datetime,
        new_end_dt: datetime,
        exclude_membership_id: int,
    ) -> Optional[Membership]:
        """Return the first active membership for a member that overlaps [new_start_dt, new_end_dt).

        Used to enforce RN-13: a start_date correction must not create temporal overlap
        with another active membership of the same client.
        """
        return (
            self.db.query(Membership)
            .filter(
                Membership.member_id == member_id,
                Membership.id != exclude_membership_id,
                Membership.is_active == True,  # noqa: E712
                Membership.start_date < new_end_dt,
                Membership.end_date > new_start_dt,
            )
            .first()
        )

    def correct_start_date_no_commit(
        self,
        membership_id: int,
        new_start_dt: datetime,
        new_end_dt: datetime,
        new_frozen_days_remaining: Optional[int],
    ) -> Optional[Membership]:
        """Update start_date, end_date and optionally frozen_days_remaining without committing.

        Caller owns the transaction. Used by MembershipService.correct_start_date so that
        the correction log insert and this update share a single commit.
        """
        membership = self.get_by_id(membership_id)
        if not membership:
            return None
        membership.start_date = new_start_dt
        membership.end_date = new_end_dt
        if new_frozen_days_remaining is not None:
            membership.frozen_days_remaining = new_frozen_days_remaining
        self.db.flush()
        return membership
