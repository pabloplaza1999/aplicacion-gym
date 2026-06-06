"""Attendance API routes — voucher check-in by document (cédula)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.attendance import AttendanceCheckIn, CheckInResult, VoucherStatus
from app.services.attendance_service import AttendanceService, CheckInError

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("/check-in", response_model=CheckInResult)
def check_in(
    data: AttendanceCheckIn,
    db: Session = Depends(get_db),
) -> CheckInResult:
    """
    Register an attendance for a voucher membership by document (cédula).

    Consumes one entry. Rules enforced:
    - The member must exist and have an active voucher.
    - The voucher must not be expired and must have entries remaining.
    - Only one attendance per member per calendar day.
    """
    service = AttendanceService(db)
    try:
        return service.check_in(data.document)
    except CheckInError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/voucher-status/{document}", response_model=VoucherStatus)
def voucher_status(
    document: str,
    db: Session = Depends(get_db),
) -> VoucherStatus:
    """Read-only status of a member's active voucher (does not consume entries)."""
    service = AttendanceService(db)
    try:
        return service.get_voucher_status(document)
    except CheckInError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
