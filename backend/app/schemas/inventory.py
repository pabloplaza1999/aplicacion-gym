"""Inventory movement schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class InventoryEntryCreate(BaseModel):
    quantity: int = Field(..., gt=0)
    note: Optional[str] = None


class InventoryAdjustmentCreate(BaseModel):
    quantity: int = Field(..., ne=0)   # positive or negative, never zero
    note: str = Field(..., min_length=1)


class InventoryMovementRead(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    type: str
    quantity: int
    stock_before: int
    stock_after: int
    note: Optional[str] = None
    sale_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
