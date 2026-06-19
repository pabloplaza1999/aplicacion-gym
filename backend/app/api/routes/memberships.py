"""Memberships API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.membership import (
    MembershipCreate,
    MembershipRead,
    MembershipRenew,
    MembershipSetActive,
    MembershipWithPlanRead,
    MembershipHistoryResponse,
    VoucherWarning,
)
from app.schemas.membership_correction import MembershipStartDateCorrectionCreate
from app.services.membership_service import (
    ActiveVoucherExistsError,
    FreezeLimitReachedError,  # raised when freeze_count >= MAX_FREEZE_CYCLES
    MembershipCorrectionError,
    MembershipNotFoundError,
    MembershipService,
)

router = APIRouter(prefix="/members", tags=["memberships"])


@router.get("/{member_id}/active-voucher-warning", response_model=VoucherWarning)
def get_active_voucher_warning(
    member_id: int,
    db: Session = Depends(get_db),
) -> VoucherWarning:
    """
    Retorna información de la valera activa vigente del cliente, si existe.

    Usado por el frontend antes de crear/renovar a plan mensual para mostrar
    advertencia al operador y solicitar confirmación explícita.
    """
    service = MembershipService(db)
    return service.get_active_voucher_warning(member_id)


@router.post("/{member_id}/memberships", response_model=MembershipRead, status_code=201)
def create_membership(
    member_id: int,
    data: MembershipCreate,
    db: Session = Depends(get_db),
) -> MembershipRead:
    """
    Create a new membership for a member.

    **Fields:**
    - **member_id**: Member ID (path parameter)
    - **plan_id**: Plan ID (required)
    - **start_date**: Start date (optional, defaults to today)

    **Automatic calculations:**
    - End date calculated based on plan duration
    - Status calculated based on days remaining
    """
    if data.member_id != member_id:
        data.member_id = member_id

    service = MembershipService(db)
    try:
        return service.create_membership(data)
    except ActiveVoucherExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/{member_id}/memberships", response_model=MembershipHistoryResponse)
def get_member_memberships(
    member_id: int,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros"),
    db: Session = Depends(get_db),
) -> MembershipHistoryResponse:
    """
    Get all memberships for a member.

    **Path Parameters:**
    - **member_id**: Member ID

    **Query Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records (default: 100)

    **Returns:**
    List of memberships ordered by start_date (most recent first)
    """
    service = MembershipService(db)
    result = service.get_member_memberships(member_id, skip=skip, limit=limit)
    return MembershipHistoryResponse(**result)


@router.get("/{member_id}/current-membership", response_model=MembershipWithPlanRead)
def get_current_membership(
    member_id: int,
    db: Session = Depends(get_db),
) -> MembershipWithPlanRead:
    """
    Get the current (most recent) membership for a member.

    **Path Parameters:**
    - **member_id**: Member ID

    **Returns:**
    Current membership with plan details and days remaining
    """
    service = MembershipService(db)
    membership = service.get_current_membership(member_id)
    if not membership:
        raise HTTPException(status_code=404, detail="No se encontraron membresías")
    return membership


@router.post("/memberships/{membership_id}/renew", response_model=MembershipRead, status_code=201)
def renew_membership(
    membership_id: int,
    data: MembershipRenew,
    db: Session = Depends(get_db),
) -> MembershipRead:
    """
    Renew a membership with a new plan.

    Creates a new membership starting from today with the specified plan.

    **Path Parameters:**
    - **membership_id**: Current membership ID (for reference)

    **Fields:**
    - **plan_id**: New plan ID (required)

    **Returns:**
    New membership starting from today
    """
    service = MembershipService(db)
    try:
        return service.renew_membership(membership_id, data)
    except ActiveVoucherExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/memberships/{membership_id}/freeze", response_model=MembershipWithPlanRead)
def freeze_membership(
    membership_id: int,
    db: Session = Depends(get_db),
) -> MembershipWithPlanRead:
    """
    Freeze a membership: preserves remaining days, deactivates.

    On unfreeze, end_date = today + frozen_days_remaining.
    Blocked if already frozen, inactive, or expired.
    """
    service = MembershipService(db)
    try:
        return service.freeze_membership(membership_id)
    except MembershipNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memberships/{membership_id}/unfreeze", response_model=MembershipWithPlanRead)
def unfreeze_membership(
    membership_id: int,
    db: Session = Depends(get_db),
) -> MembershipWithPlanRead:
    """
    Unfreeze a membership: restores end_date = today + frozen_days_remaining.

    Accumulates freeze_days with elapsed days. Clears freeze fields.
    Blocked if not currently frozen.
    """
    service = MembershipService(db)
    try:
        return service.unfreeze_membership(membership_id)
    except MembershipNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/memberships/{membership_id}/active", response_model=MembershipWithPlanRead)
def set_membership_active(
    membership_id: int,
    data: MembershipSetActive,
    db: Session = Depends(get_db),
) -> MembershipWithPlanRead:
    """
    Manually activate or deactivate a membership.

    The membership state changes ONLY through this endpoint; it does not
    depend on the member's own active/inactive state.

    **Path Parameters:**
    - **membership_id**: Membership ID

    **Fields:**
    - **is_active**: Desired manual state (true = activa, false = desactivada)
    """
    service = MembershipService(db)
    try:
        membership = service.set_membership_active(membership_id, data.is_active)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not membership:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    return membership


@router.patch("/memberships/{membership_id}/start-date", response_model=MembershipWithPlanRead)
def correct_membership_start_date(
    membership_id: int,
    data: MembershipStartDateCorrectionCreate,
    db: Session = Depends(get_db),
) -> MembershipWithPlanRead:
    """
    Correct the start_date of an existing membership.

    Recalculates end_date preserving the original plan duration.
    For frozen memberships, also recalculates frozen_days_remaining.
    Writes an immutable audit record atomically with the update.

    **Blocked when:**
    - Membership is expired or manually deactivated (not frozen).
    - Membership has recorded attendances.
    - New start_date is in the future.
    - Correction would make end_date fall in the past.
    - Correction would overlap with another active membership of the same member.
    - For frozen memberships: new end_date would be before frozen_at.
    """
    service = MembershipService(db)
    try:
        return service.correct_start_date(membership_id, data.new_start_date, data.reason)
    except MembershipNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MembershipCorrectionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/memberships/{membership_id}", response_model=MembershipWithPlanRead)
def get_membership(
    membership_id: int,
    db: Session = Depends(get_db),
) -> MembershipWithPlanRead:
    """
    Get a membership by ID with plan details.

    **Path Parameters:**
    - **membership_id**: Membership ID

    **Returns:**
    Membership with plan details and days remaining
    """
    service = MembershipService(db)
    membership = service.get_membership(membership_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    return membership
