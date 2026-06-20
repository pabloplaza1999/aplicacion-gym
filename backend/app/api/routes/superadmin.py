"""Super Admin routes — gym info, licensing, and module management.

All endpoints require role='super_admin'. Regular admin users receive HTTP 403.
Single-tenant: always operates on gym_id=1. Will be parameterized in F8+ (multi-tenant).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_super_admin
from app.database.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.gym import (
    GymLicensePanel,
    GymRead,
    GymUpdate,
    LicensePlanUpdate,
    LicenseRead,
    LicenseValidityUpdate,
    ModuleStatusRead,
    ModuleToggle,
)
from app.services.license_service import LicenseService

router = APIRouter(prefix="/superadmin", tags=["superadmin"])

_GYM_ID = 1


@router.get("/panel", response_model=GymLicensePanel)
def get_panel(
    user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> GymLicensePanel:
    """Return gym info, active license, and all module states."""
    try:
        return LicenseService(db).get_panel(_GYM_ID)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/gym", response_model=GymRead)
def update_gym(
    data: GymUpdate,
    user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> GymRead:
    """Update gym contact information."""
    try:
        return LicenseService(db).update_gym(_GYM_ID, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/license/plan", response_model=LicenseRead)
def change_plan(
    data: LicensePlanUpdate,
    user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> LicenseRead:
    """Change the commercial plan for the gym. Updates module source flags automatically."""
    valid_plans = ["starter", "professional", "premium"]
    if data.plan_name not in valid_plans:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Plan inválido. Opciones: {valid_plans}",
        )
    try:
        return LicenseService(db).change_plan(_GYM_ID, data, user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/license/validity", response_model=LicenseRead)
def update_validity(
    data: LicenseValidityUpdate,
    user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> LicenseRead:
    """Update license validity dates. Set valid_until=null to remove expiry."""
    try:
        return LicenseService(db).update_validity(_GYM_ID, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/modules/{module_key}", response_model=ModuleStatusRead)
def toggle_module(
    module_key: str,
    data: ModuleToggle,
    user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> ModuleStatusRead:
    """Activate or deactivate a module for the gym. Updates in-memory cache immediately."""
    try:
        return LicenseService(db).toggle_module(_GYM_ID, module_key, data, user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
