"""Dashboard schemas."""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class MembershipStatusSummary(BaseModel):
    """Summary of memberships by status."""

    active: int
    expiring: int   # 1-5 days remaining
    expired: int
    frozen: int = 0
    exhausted: int = 0  # vouchers with no entries remaining but still within date


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


class MembershipAlert(BaseModel):
    """A single membership alert item."""

    membership_id: int
    member_id: int
    member_name: str
    phone: Optional[str] = None
    document: Optional[str] = None
    plan_name: str
    end_date: date
    days_overdue: int = 0


class DebtorAlert(BaseModel):
    """Customer with outstanding debt, ordered by balance DESC."""

    customer_id: int
    customer_name: str
    outstanding_balance: float
    oldest_sale_date: Optional[date] = None
    days_overdue: int = 0


class LowStockAlertItem(BaseModel):
    """Product with stock at or below minimum."""

    product_id: int
    product_name: str
    stock: int
    min_stock: int


class AlertsSummary(BaseModel):
    """Consolidated alerts: memberships, cartera, and inventory."""

    # Membership alerts (4 urgency groups)
    expired_count: int
    today_count: int
    three_days_count: int
    seven_days_count: int

    expired_items: List[MembershipAlert]
    today_items: List[MembershipAlert]
    three_days_items: List[MembershipAlert]
    seven_days_items: List[MembershipAlert]

    # Store alerts (optional — default empty for backward compatibility)
    debtors_count: int = 0
    low_stock_count: int = 0
    top_debtors: List[DebtorAlert] = []
    low_stock_items: List[LowStockAlertItem] = []


class MembersByPlan(BaseModel):
    """Member count breakdown by plan and membership status."""

    plan_id: int
    plan_name: str
    plan_type: str          # 'monthly' | 'voucher'
    active_count: int
    exhausted_count: int    # vouchers only — within date but no entries remaining
    expired_count: int
    frozen_count: int
    total: int


class DashboardKPI(BaseModel):
    """Full dashboard KPI response."""

    # Members
    total_active_members: int

    # Memberships
    memberships: MembershipStatusSummary

    # Revenue — monthly_revenue preserved for backward compatibility
    monthly_revenue: float
    revenue_by_plan: List[RevenueByPlan]

    # Revenue breakdown (optional — new in Dashboard Fase B)
    membership_revenue: Optional[float] = None
    store_revenue: Optional[float] = None
    total_revenue: Optional[float] = None

    # Store KPIs (optional)
    store_sales_count: Optional[int] = None
    cartera_balance: Optional[float] = None

    # Renewals
    recent_renewals: List[RecentRenewal]

    # Alerts (consolidated: memberships + store)
    alerts: Optional[AlertsSummary] = None

    # Members by plan distribution
    members_by_plan: List[MembersByPlan] = []
