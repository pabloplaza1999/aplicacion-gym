"""Membership service for business logic."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.membership_repository import MembershipRepository
from app.schemas.membership import (
    MembershipCreate,
    MembershipRead,
    MembershipRenew,
    MembershipWithPlanRead,
)


class MembershipService:
    """Service for membership business logic operations."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.repository = MembershipRepository(db)
        self.db = db

    def _calculate_status(self, end_date: datetime, is_active: bool = True) -> str:
        """
        Calculate membership status.

        Rules:
        - inactive: manually deactivated (is_active=False), overrides dates
        - expired: end_date < today
        - expiring: today <= end_date <= today + 5 days
        - active: end_date > today + 5 days

        Args:
            end_date: Membership end date
            is_active: Manual on/off switch

        Returns:
            Status string: 'inactive', 'expired', 'expiring', or 'active'
        """
        if not is_active:
            return "inactive"

        today = datetime.utcnow()
        days_remaining = (end_date - today).days

        if days_remaining < 0:
            return "expired"
        elif days_remaining <= 5:
            return "expiring"
        else:
            return "active"

    def _calculate_end_date(self, start_date: datetime, plan_id: int) -> datetime:
        """
        Calculate end date based on plan duration.

        Rules:
        - Plan Día (plan_type='daily'): vence el mismo día
        - Plans mensuales: 30 días desde start_date

        Args:
            start_date: Membership start date
            plan_id: Plan ID

        Returns:
            Calculated end date
        """
        plan = self.repository.get_plan_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        if plan.plan_type == "daily":
            # Plan Día: vence el mismo día
            return start_date.replace(hour=23, minute=59, second=59)
        else:
            # Plans mensuales: duration_days (30)
            return start_date + timedelta(days=plan.duration_days)

    def _enrich_membership(self, membership, plan=None):
        """
        Enrich membership with calculated status and plan details.

        Args:
            membership: Membership model instance
            plan: Plan model instance (optional, fetched if not provided)

        Returns:
            Dictionary with membership data and calculated fields
        """
        if plan is None:
            plan = self.repository.get_plan_by_id(membership.plan_id)

        data = MembershipRead.from_orm(membership)
        data.status = self._calculate_status(membership.end_date, membership.is_active)

        # Calculate days remaining
        today = datetime.utcnow()
        days_remaining = max(0, (membership.end_date - today).days)

        return {
            **data.model_dump(),
            "days_remaining": days_remaining,
            "plan_name": plan.name if plan else None,
            "plan_price": plan.price if plan else None,
            "plan_duration_days": plan.duration_days if plan else None,
        }

    def create_membership(self, data: MembershipCreate) -> MembershipRead:
        """
        Create a new membership.

        Automatically calculates end_date based on plan duration.

        Args:
            data: Membership creation data

        Returns:
            Created membership with calculated status
        """
        start_date = data.start_date or datetime.utcnow()
        end_date = self._calculate_end_date(start_date, data.plan_id)

        # Voucher memberships snapshot their entry cap from the plan; date-based
        # memberships keep entries_total = None (unchanged behavior).
        plan = self.repository.get_plan_by_id(data.plan_id)
        entries_total = plan.entry_count if plan and plan.plan_type == "voucher" else None

        membership = self.repository.create(
            member_id=data.member_id,
            plan_id=data.plan_id,
            start_date=start_date,
            end_date=end_date,
            entries_total=entries_total,
        )

        result = MembershipRead.from_orm(membership)
        result.status = self._calculate_status(membership.end_date)
        return result

    def get_membership(self, membership_id: int) -> Optional[MembershipWithPlanRead]:
        """Get a membership by ID with plan details."""
        membership = self.repository.get_by_id(membership_id)
        if not membership:
            return None

        plan = self.repository.get_plan_by_id(membership.plan_id)
        enriched = self._enrich_membership(membership, plan)

        return MembershipWithPlanRead(**enriched)

    def get_member_memberships(
        self, member_id: int, skip: int = 0, limit: int = 100
    ) -> dict:
        """
        Get all memberships for a member.

        Args:
            member_id: Member ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Dictionary with total count and list of memberships
        """
        memberships = self.repository.get_by_member_id(member_id, skip=skip, limit=limit)
        total = self.repository.get_by_member_id_count(member_id)

        items = []
        for m in memberships:
            result = MembershipRead.from_orm(m)
            result.status = self._calculate_status(m.end_date, m.is_active)
            items.append(result)

        return {
            "total": total,
            "items": items,
        }

    def get_current_membership(self, member_id: int) -> Optional[MembershipWithPlanRead]:
        """
        Get the current (most recent) membership for a member.

        Args:
            member_id: Member ID

        Returns:
            Current membership with plan details or None
        """
        membership = self.repository.get_active_membership(member_id)
        if not membership:
            return None

        plan = self.repository.get_plan_by_id(membership.plan_id)
        enriched = self._enrich_membership(membership, plan)

        return MembershipWithPlanRead(**enriched)

    def renew_membership(self, membership_id: int, data: MembershipRenew) -> MembershipRead:
        """
        Renew a membership with a new plan.

        Creates a new membership starting from today.

        Args:
            membership_id: Current membership ID (for reference)
            data: Renewal data with new plan_id

        Returns:
            New membership
        """
        old_membership = self.repository.get_by_id(membership_id)
        if not old_membership:
            raise ValueError(f"Membership {membership_id} not found")

        # Create new membership starting today
        start_date = datetime.utcnow()
        end_date = self._calculate_end_date(start_date, data.plan_id)

        new_membership = self.repository.create(
            member_id=old_membership.member_id,
            plan_id=data.plan_id,
            start_date=start_date,
            end_date=end_date,
        )

        result = MembershipRead.from_orm(new_membership)
        result.status = self._calculate_status(new_membership.end_date)
        return result

    def set_membership_active(
        self, membership_id: int, is_active: bool
    ) -> Optional[MembershipWithPlanRead]:
        """
        Manually activate or deactivate a membership.

        Independent of the member's state and of the dates.

        Args:
            membership_id: Membership ID
            is_active: Desired manual state

        Returns:
            Updated membership with plan details or None if not found
        """
        membership = self.repository.set_active(membership_id, is_active)
        if not membership:
            return None

        plan = self.repository.get_plan_by_id(membership.plan_id)
        enriched = self._enrich_membership(membership, plan)
        return MembershipWithPlanRead(**enriched)

    def get_expiring_memberships(self, days: int = 5) -> list[MembershipWithPlanRead]:
        """
        Get memberships expiring within the specified number of days.

        Args:
            days: Number of days to check

        Returns:
            List of expiring memberships with plan details
        """
        memberships = self.repository.get_expiring_soon(days=days)

        results = []
        for m in memberships:
            plan = self.repository.get_plan_by_id(m.plan_id)
            enriched = self._enrich_membership(m, plan)
            results.append(MembershipWithPlanRead(**enriched))

        return results
