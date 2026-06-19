"""Schema for membership start_date correction request."""

from datetime import date
from pydantic import BaseModel, field_validator


class MembershipStartDateCorrectionCreate(BaseModel):
    """Request body for correcting a membership's start_date (PATCH /memberships/{id}/start-date)."""

    new_start_date: date
    reason: str

    @field_validator("reason")
    @classmethod
    def reason_min_length(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("El motivo debe tener al menos 10 caracteres.")
        return v.strip()
