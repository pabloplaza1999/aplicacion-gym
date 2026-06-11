"""Product and category schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Category ──────────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Product ───────────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    cost: Optional[float] = Field(None, ge=0)
    stock: int = Field(0, ge=0)
    min_stock: int = Field(0, ge=0)


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)


class ProductRead(BaseModel):
    id: int
    category_id: int
    category_name: Optional[str] = None
    name: str
    description: Optional[str] = None
    price: float
    cost: Optional[float] = None
    stock: int
    min_stock: int
    is_active: bool
    is_low_stock: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
