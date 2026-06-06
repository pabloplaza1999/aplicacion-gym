"""Dashboard schemas."""

from pydantic import BaseModel
from typing import List, Optional


class MembershipStatusSummary(BaseModel):
    """Summary of memberships by status."""

    active: int
    expiring: int   # 1-5 days remaining
    expired: int


class RevenueByPlan(BaseModel):
    """Revenue breakdown by plan."""

    plan_id: int
    plan_name: str
    count: int
    total_amount: float


class RecentRenewal(BaseModel):
    """Recent membership renewal info."""

    member_id: int
    member_name: str
    plan_name: str
    start_date: str
    end_date: str
    amount_paid: Optional[float] = None


class DashboardKPI(BaseModel):
    """Full dashboard KPI response."""

    # Members
    total_active_members: int

    # Memberships
    memberships: MembershipStatusSummary

    # Revenue
    monthly_revenue: float
    revenue_by_plan: List[RevenueByPlan]

    # Renewals
    recent_renewals: List[RecentRenewal]
