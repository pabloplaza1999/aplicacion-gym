"""Credit payment (abono) schemas — Tienda Fase B."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CreditPaymentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    method: str = Field(..., min_length=1)
    notes: Optional[str] = None


class CreditPaymentRead(BaseModel):
    id: int
    sale_id: int
    amount: float
    method: str
    notes: Optional[str] = None
    paid_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
