"""Dashboard API route."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.dashboard import DashboardKPI
from app.services.dashboard_service import DashboardService

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardKPI)
def get_dashboard(db: Session = Depends(get_db)):
    """Get dashboard KPIs.

    Returns:
    - **total_active_members**: Members with active account
    - **memberships**: Count by status (active / expiring / expired)
    - **monthly_revenue**: Total income current month
    - **revenue_by_plan**: Income breakdown by plan (current month)
    - **recent_renewals**: Last 5 membership registrations
    """
    service = DashboardService(db)
    return service.get_kpis()
