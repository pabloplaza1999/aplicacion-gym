"""Customer schemas — Tienda Fase B."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    document: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    document: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class CustomerRead(BaseModel):
    id: int
    name: str
    document: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    member_id: Optional[int] = None
    member_name: Optional[str] = None
    debt_total: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True
