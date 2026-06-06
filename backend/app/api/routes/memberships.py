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
)
from app.services.membership_service import (
    ActiveVoucherExistsError,
    MembershipService,
)

router = APIRouter(prefix="/members", tags=["memberships"])


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
    membership = service.set_membership_active(membership_id, data.is_active)
    if not membership:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    return membership


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
