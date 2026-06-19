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

    force: bool = Field(False, description="Desactivar valera activa si existe (cambio a plan mensual)")


class MembershipRenew(BaseModel):
    """Schema for renewing a membership."""

    plan_id: int = Field(..., description="ID del plan")
    force: bool = Field(False, description="Desactivar valera activa si existe (cambio a plan mensual)")


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
    status: str = Field(..., description="Estado (active, expiring, expired, inactive, frozen)")
    freeze_days: int = Field(..., description="Días congelados acumulados")
    is_active: bool = Field(..., description="Estado manual (activada/desactivada)")
    frozen_at: Optional[datetime] = Field(None, description="Fecha en que se congeló (None si no está congelada)")
    frozen_days_remaining: Optional[int] = Field(None, description="Días pendientes guardados al congelar")
    last_notified_at: Optional[datetime] = Field(
        None,
        description="[INTERNO] Última vez que el job de notificaciones envió aviso de vencimiento. "
                    "Solo escrito por el notification job (Fase 2). Nunca modificar desde servicios de membresía o frontend.",
    )
    last_correction_at: Optional[datetime] = Field(
        None, description="Fecha y hora de la última corrección de fecha de inicio."
    )
    last_correction_reason: Optional[str] = Field(
        None, description="Motivo de la última corrección de fecha de inicio."
    )

    model_config = {"from_attributes": True}


class MembershipWithPlanRead(MembershipRead):
    """Membership with plan details."""

    plan_name: str = Field(..., description="Nombre del plan")
    plan_price: float = Field(..., description="Precio del plan")
    plan_duration_days: int = Field(..., description="Duración en días")
    days_remaining: int = Field(..., description="Días restantes")


class VoucherWarning(BaseModel):
    """Advertencia de valera activa al cambiar a plan mensual."""

    has_active_voucher: bool
    membership_id: Optional[int] = None
    plan_name: Optional[str] = None
    entries_remaining: Optional[int] = None
    end_date: Optional[str] = None


class MembershipHistoryResponse(BaseModel):
    """Schema for membership history response."""

    total: int = Field(..., description="Total de membresías")
    items: list[MembershipRead] = Field(..., description="Lista de membresías")
