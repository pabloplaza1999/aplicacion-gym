"""Dashboard service — builds KPI response."""

from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardKPI,
    MembershipStatusSummary,
    RevenueByPlan,
    RecentRenewal,
)


class DashboardService:
    """Builds the dashboard KPI payload."""

    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)

    def get_kpis(self) -> DashboardKPI:
        """Return all KPIs for the current month."""
        now = datetime.utcnow()
        year, month = now.year, now.month

        # 1. Active members
        total_active = self.repository.get_active_members_count()

        # 2. Memberships by status
        status_counts = self.repository.get_memberships_by_status()
        memberships = MembershipStatusSummary(
            active=status_counts["active"],
            expiring=status_counts["expiring"],
            expired=status_counts["expired"],
        )

        # 3. Monthly revenue
        monthly_revenue = self.repository.get_monthly_revenue(year, month)

        # 4. Revenue by plan
        plan_rows = self.repository.get_revenue_by_plan(year, month)
        revenue_by_plan = [
            RevenueByPlan(
                plan_id=row[0],
                plan_name=row[1],
                count=row[2],
                total_amount=row[3] or 0.0,
            )
            for row in plan_rows
        ]

        # 5. Recent renewals (last 5)
        renewal_rows = self.repository.get_recent_renewals(limit=5)
        recent_renewals = [
            RecentRenewal(
                member_id=row[1],
                member_name=row[2],
                plan_name=row[3],
                start_date=str(row[4].date()),
                end_date=str(row[5].date()),
                amount_paid=row[6],
            )
            for row in renewal_rows
        ]

        return DashboardKPI(
            total_active_members=total_active,
            memberships=memberships,
            monthly_revenue=monthly_revenue,
            revenue_by_plan=revenue_by_plan,
            recent_renewals=recent_renewals,
        )
