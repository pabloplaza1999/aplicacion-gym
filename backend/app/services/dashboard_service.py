"""Dashboard service — builds KPI response."""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.dashboard import (
    DashboardKPI,
    MembershipStatusSummary,
    MembersByPlan,
    RevenueByPlan,
    RecentRenewal,
    MembershipAlert,
    AlertsSummary,
    DebtorAlert,
    LowStockAlertItem,
)


class DashboardService:
    """Builds the dashboard KPI payload."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = DashboardRepository(db)

    def get_kpis(self) -> DashboardKPI:
        """Return all KPIs for the current month."""
        now = datetime.utcnow()
        year, month = now.year, now.month

        # Month boundaries (reused by both membership and store queries)
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(seconds=1)

        # 1. Active members
        total_active = self.repository.get_active_members_count()

        # 2. Memberships by status
        status_counts = self.repository.get_memberships_by_status()
        memberships = MembershipStatusSummary(
            active=status_counts["active"],
            expiring=status_counts["expiring"],
            expired=status_counts["expired"],
            frozen=status_counts["frozen"],
            exhausted=status_counts["exhausted"],
        )

        # 3. Monthly revenue (memberships) — preserved as-is for backward compatibility
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

        # 6. Store KPIs — reutiliza métodos consolidados de SaleRepository/ProductRepository
        sale_repo = SaleRepository(self.db)
        product_repo = ProductRepository(self.db)

        sales_kpis = sale_repo.get_sales_kpis(start, end)
        credit_collections = sale_repo.get_credit_collections(start, end)
        # store_revenue = dinero efectivamente cobrado: ventas cash + abonos del período
        store_revenue = round(sales_kpis['cash_sales_amount'] + credit_collections, 2)
        store_sales_count = sales_kpis['total_sales']

        cartera_kpis = sale_repo.get_cartera_kpis()
        cartera_balance = cartera_kpis['total_balance']

        # Top deudores ordenados por saldo DESC con antigüedad
        today = now.date()
        top_debtors = [
            DebtorAlert(
                customer_id=row[0],
                customer_name=row[1],
                outstanding_balance=round(float(row[2]), 2),
                oldest_sale_date=row[3].date() if row[3] else None,
                days_overdue=(today - row[3].date()).days if row[3] else 0,
            )
            for row in sale_repo.get_top_debtors(limit=5)
        ]

        # Bajo stock — reutiliza query existente de ProductRepository
        low_stock_items = [
            LowStockAlertItem(
                product_id=p.id,
                product_name=p.name,
                stock=p.stock,
                min_stock=p.min_stock,
            )
            for p in product_repo.get_products(low_stock=True, active_only=True, limit=5)
        ]

        # 7. Members by plan distribution
        plan_rows = self.repository.get_members_by_plan()
        members_by_plan = [MembersByPlan(**p) for p in plan_rows]

        # 8. Alerts — membresías + cartera + bajo stock consolidados
        alert_groups = self.repository.get_membership_alerts()
        alerts = AlertsSummary(
            expired_count=len(alert_groups["expired"]),
            today_count=len(alert_groups["today"]),
            three_days_count=len(alert_groups["three_days"]),
            seven_days_count=len(alert_groups["seven_days"]),
            expired_items=[MembershipAlert(**i) for i in alert_groups["expired"]],
            today_items=[MembershipAlert(**i) for i in alert_groups["today"]],
            three_days_items=[MembershipAlert(**i) for i in alert_groups["three_days"]],
            seven_days_items=[MembershipAlert(**i) for i in alert_groups["seven_days"]],
            debtors_count=cartera_kpis['customer_count'],
            low_stock_count=len(low_stock_items),
            top_debtors=top_debtors,
            low_stock_items=low_stock_items,
        )

        return DashboardKPI(
            total_active_members=total_active,
            memberships=memberships,
            monthly_revenue=monthly_revenue,
            revenue_by_plan=revenue_by_plan,
            recent_renewals=recent_renewals,
            alerts=alerts,
            membership_revenue=monthly_revenue,
            store_revenue=store_revenue,
            total_revenue=round(monthly_revenue + store_revenue, 2),
            store_sales_count=store_sales_count,
            cartera_balance=cartera_balance,
            members_by_plan=members_by_plan,
        )
