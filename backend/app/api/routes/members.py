"""Members API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.member import MemberCreate, MemberUpdate, MemberRead, MemberListResponse
from app.services.member_service import MemberService, DuplicateDocumentError

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", response_model=MemberRead, status_code=201)
def create_member(
    data: MemberCreate,
    db: Session = Depends(get_db),
) -> MemberRead:
    """
    Create a new member.

    **Fields:**
    - **full_name**: Full name (required)
    - **phone**: Phone number (required)
    - **document**: Document/ID (optional)
    - **email**: Email address (optional). Validated via EmailStr; "" and " " stored as null.
    - **notes**: Notes (optional)
    """
    service = MemberService(db)
    try:
        return service.create_member(data)
    except DuplicateDocumentError:
        raise HTTPException(status_code=409, detail="Ya existe un cliente con ese número de documento.")


@router.get("", response_model=MemberListResponse)
def list_members(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros"),
    search: Optional[str] = Query(None, description="Buscar por nombre o teléfono"),
    db: Session = Depends(get_db),
):
    """
    List all members.

    **Query Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records (default: 100)
    - **search**: Search by name or phone (optional)
    """
    service = MemberService(db)
    if search:
        return service.search_members(search, skip=skip, limit=limit)
    return service.list_members(skip=skip, limit=limit)


@router.get("/{member_id}", response_model=MemberRead)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
) -> MemberRead:
    """Get a member by ID."""
    service = MemberService(db)
    member = service.get_member(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    return member


@router.put("/{member_id}", response_model=MemberRead)
def update_member(
    member_id: int,
    data: MemberUpdate,
    db: Session = Depends(get_db),
) -> MemberRead:
    """
    Update a member.

    **Fields (all optional):**
    - **full_name**: Full name
    - **phone**: Phone number
    - **document**: Document/ID
    - **email**: Email address. Contract: valid string → update; null or "" → sets NULL (delete); omitted → no change.
    - **notes**: Notes
    - **is_active**: Active status
    """
    service = MemberService(db)
    member = service.update_member(member_id, data)
    if not member:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    return member


@router.delete("/{member_id}", response_model=MemberRead)
def delete_member(
    member_id: int,
    hard: bool = Query(False, description="If true, permanently delete member and all related data from database"),
    db: Session = Depends(get_db),
) -> MemberRead:
    """Deactivate or permanently delete a member."""
    service = MemberService(db)
    if hard:
        member = service.get_member(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Miembro no encontrado")
        try:
            success = service.hard_delete_member(member_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        if not success:
            raise HTTPException(status_code=500, detail="Error al eliminar el miembro")
        return member
    else:
        member = service.deactivate_member(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Miembro no encontrado")
        return member
