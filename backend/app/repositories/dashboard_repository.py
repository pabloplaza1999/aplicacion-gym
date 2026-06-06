"""Dashboard repository — aggregated queries for KPI endpoint."""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.member import Member
from app.models.membership import Membership
from app.models.payment import Payment
from app.models.plan import Plan


class DashboardRepository:
    """Efficient aggregated queries for dashboard KPIs."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    # Members                                                              #
    # ------------------------------------------------------------------ #

    def get_active_members_count(self) -> int:
        """Total members with is_active=True."""
        return self.db.query(Member).filter(Member.is_active == True).count()

    # ------------------------------------------------------------------ #
    # Memberships by status                                                #
    # ------------------------------------------------------------------ #

    def get_memberships_by_status(self) -> dict:
        """Count each member's CURRENT membership by status.

        Only the most recent membership per member is considered, so historical
        rows (previous renewals / replaced plans) are not counted as active.
        Status is derived from ``end_date`` to match the rest of the app
        (see MembershipService._calculate_status), ignoring the stale
        persisted ``status`` column which is never updated on renewal.
        """
        rows = (
            self.db.query(Membership.member_id, Membership.end_date, Membership.is_active)
            .order_by(Membership.member_id, Membership.start_date.desc())
            .all()
        )

        result = {"active": 0, "expiring": 0, "expired": 0}
        seen = set()
        now = datetime.utcnow()
        for member_id, end_date, is_active in rows:
            if member_id in seen:
                continue
            seen.add(member_id)
            # Manually deactivated memberships are not counted as active/expiring/expired.
            if not is_active:
                continue
            days_remaining = (end_date - now).days
            if days_remaining < 0:
                result["expired"] += 1
            elif days_remaining <= 5:
                result["expiring"] += 1
            else:
                result["active"] += 1
        return result

    # ------------------------------------------------------------------ #
    # Revenue                                                              #
    # ------------------------------------------------------------------ #

    def get_monthly_revenue(self, year: int, month: int) -> float:
        """Total payment amount for a given month."""
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(seconds=1)

        result = (
            self.db.query(func.sum(Payment.amount))
            .filter(Payment.payment_date >= start, Payment.payment_date <= end)
            .scalar()
        )
        return result or 0.0

    def get_revenue_by_plan(self, year: int, month: int) -> list:
        """Revenue grouped by plan for a given month via JOIN.

        Returns list of (plan_id, plan_name, count, total_amount).
        """
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(seconds=1)

        rows = (
            self.db.query(
                Plan.id,
                Plan.name,
                func.count(Payment.id),
                func.sum(Payment.amount),
            )
            .join(Membership, Payment.membership_id == Membership.id)
            .join(Plan, Membership.plan_id == Plan.id)
            .filter(
                Payment.payment_date >= start,
                Payment.payment_date <= end,
                Payment.membership_id.isnot(None),
            )
            .group_by(Plan.id, Plan.name)
            .order_by(func.sum(Payment.amount).desc())
            .all()
        )
        return rows

    # ------------------------------------------------------------------ #
    # Recent renewals                                                      #
    # ------------------------------------------------------------------ #

    def get_recent_renewals(self, limit: int = 5) -> list:
        """Most recent memberships with member name, plan name and last payment.

        Returns list of (membership, member_name, plan_name, amount_paid).
        """
        rows = (
            self.db.query(
                Membership.id,
                Membership.member_id,
                Member.full_name,
                Plan.name,
                Membership.start_date,
                Membership.end_date,
                func.max(Payment.amount),
            )
            .join(Member, Membership.member_id == Member.id)
            .join(Plan, Membership.plan_id == Plan.id)
            .outerjoin(Payment, Payment.membership_id == Membership.id)
            .group_by(
                Membership.id,
                Membership.member_id,
                Member.full_name,
                Plan.name,
                Membership.start_date,
                Membership.end_date,
            )
            .order_by(Membership.start_date.desc())
            .limit(limit)
            .all()
        )
        return rows
