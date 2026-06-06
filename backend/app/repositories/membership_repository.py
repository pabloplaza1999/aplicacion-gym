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
            .order_by(Membership.start_date.desc())
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

    def get_plan_by_id(self, plan_id: int) -> Optional[Plan]:
        """Get plan details by ID."""
        return self.db.query(Plan).filter(Plan.id == plan_id).first()
