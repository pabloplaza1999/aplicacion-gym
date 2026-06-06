"""Payment schemas."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


class PaymentBase(BaseModel):
    """Base payment schema."""

    member_id: int = Field(..., gt=0, description="Member ID")
    membership_id: Optional[int] = Field(None, gt=0, description="Membership ID (optional)")
    amount: float = Field(..., gt=0, description="Payment amount")
    payment_method: str = Field(..., min_length=1, max_length=50, description="Payment method: cash, transfer, qr, nequi")


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""

    pass


class PaymentRead(PaymentBase):
    """Schema for reading payment data."""

    id: int
    payment_date: datetime
    member_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaymentsByMemberResponse(BaseModel):
    """Response for payments by member."""

    total: int
    amount_total: float
    items: List[PaymentRead]


class PaymentsByMethodResponse(BaseModel):
    """Response for payments by method."""

    method: str
    count: int
    total_amount: float
    percentage: float


class PaymentStatistics(BaseModel):
    """Payment statistics for a period."""

    total_payments: int
    total_amount: float
    by_method: List[PaymentsByMethodResponse]
    payment_date_range: Optional[str] = None


class PaymentListResponse(BaseModel):
    """Response for payment list."""

    total: int
    total_amount: float
    items: List[PaymentRead]
