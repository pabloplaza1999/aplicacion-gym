"""Pydantic schemas for membership validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MembershipBase(BaseModel):
    """Base schema for membership fields."""

    member_id: int = Field(..., description="ID del cliente")
    plan_id: int = Field(..., description="ID del plan")
    start_date: Optional[datetime] = Field(None, description="Fecha de inicio")


class MembershipCreate(MembershipBase):
    """Schema for creating a new membership."""

    pass


class MembershipRenew(BaseModel):
    """Schema for renewing a membership."""

    plan_id: int = Field(..., description="ID del plan")


class MembershipSetActive(BaseModel):
    """Schema for manually activating/deactivating a membership."""

    is_active: bool = Field(..., description="Estado manual de la membresía")


class MembershipRead(BaseModel):
    """Schema for reading membership data."""

    id: int = Field(..., description="ID de la membresía")
    member_id: int = Field(..., description="ID del cliente")
    plan_id: int = Field(..., description="ID del plan")
    start_date: datetime = Field(..., description="Fecha de inicio")
    end_date: datetime = Field(..., description="Fecha de vencimiento")
    status: str = Field(..., description="Estado (active, expiring, expired, inactive)")
    freeze_days: int = Field(..., description="Días congelados")
    is_active: bool = Field(..., description="Estado manual (activada/desactivada)")

    model_config = {"from_attributes": True}


class MembershipWithPlanRead(MembershipRead):
    """Membership with plan details."""

    plan_name: str = Field(..., description="Nombre del plan")
    plan_price: float = Field(..., description="Precio del plan")
    plan_duration_days: int = Field(..., description="Duración en días")
    days_remaining: int = Field(..., description="Días restantes")


class MembershipHistoryResponse(BaseModel):
    """Schema for membership history response."""

    total: int = Field(..., description="Total de membresías")
    items: list[MembershipRead] = Field(..., description="Lista de membresías")
