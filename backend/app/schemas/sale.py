"""Sale schemas — Fase B: customer_id, PaymentType, SaleStatus literals."""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

SaleStatus = Literal['PAID', 'PARTIAL', 'PENDING', 'CANCELLED']
PaymentType = Literal['cash', 'credit']


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class SaleCreate(BaseModel):
    customer_id: Optional[int] = None
    payment_type: PaymentType = 'cash'
    items: List[SaleItemCreate] = Field(..., min_length=1)
    discount: float = Field(0.0, ge=0)
    notes: Optional[str] = None


class SaleItemRead(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class SaleRead(BaseModel):
    id: int
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    sale_date: datetime
    subtotal: float
    discount: float
    total: float
    payment_type: str
    notes: Optional[str] = None
    status: str
    amount_paid: float = 0.0
    balance: float = 0.0
    items: List[SaleItemRead] = []
    created_at: datetime

    class Config:
        from_attributes = True


class CarteraKPI(BaseModel):
    total_balance: float
    sale_count: int
    customer_count: int


class CarteraResponse(BaseModel):
    items: List[SaleRead]
    kpi: CarteraKPI


class SaleListResponse(BaseModel):
    total: int
    total_amount: float
    items: List[SaleRead]


# ── Store Reports — Fase C ────────────────────────────────────────────────────

class TopProductItem(BaseModel):
    product_id: int
    product_name: str
    units_sold: int
    revenue: float


class LowStockItem(BaseModel):
    product_id: int
    product_name: str
    stock: int
    min_stock: int
    category_name: Optional[str] = None


class SalesKPI(BaseModel):
    total_sales: int
    total_revenue: float
    cash_sales_count: int
    cash_sales_amount: float
    credit_sales_count: int
    credit_sales_amount: float
    credit_collections_amount: float
    average_ticket: float


class CarteraReport(BaseModel):
    outstanding_balance: float
    customers_with_debt: int
    pending_sales_count: int
    partial_sales_count: int
    oldest_debt_date: Optional[datetime] = None


class InventoryReport(BaseModel):
    low_stock_count: int
    low_stock_products: List[LowStockItem]


class StoreReportResponse(BaseModel):
    date_from: datetime
    date_to: datetime
    sales: SalesKPI
    top_products: List[TopProductItem]
    cartera: CarteraReport
    inventory: InventoryReport
