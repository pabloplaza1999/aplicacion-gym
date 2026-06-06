"""Pydantic schemas for attendance / voucher check-in."""

from datetime import datetime, date

from pydantic import BaseModel, Field


class AttendanceCheckIn(BaseModel):
    """Request body for registering an attendance by document (cédula)."""

    document: str = Field(..., min_length=1, description="Cédula del cliente")


class AttendanceRead(BaseModel):
    """Single attendance record."""

    id: int
    member_id: int
    membership_id: int
    check_in_at: datetime
    check_in_date: date

    model_config = {"from_attributes": True}


class CheckInResult(BaseModel):
    """Result returned after a successful check-in."""

    member_id: int
    member_name: str
    membership_id: int
    plan_name: str
    entries_total: int
    entries_used: int
    entries_remaining: int
    end_date: datetime
    finished: bool = Field(..., description="True si la valera quedó finalizada")
    check_in_at: datetime


class VoucherStatus(BaseModel):
    """Read-only status of a member's active voucher."""

    member_id: int
    member_name: str
    membership_id: int
    plan_name: str
    entries_total: int
    entries_used: int
    entries_remaining: int
    end_date: datetime
    attended_today: bool
    finished: bool
