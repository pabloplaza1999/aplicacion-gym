"""Sale and sale item models — Fase B: customer_id replaces member_id, payment_type added."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from app.models.base import Base


class Sale(Base):
    """Sales transaction. payment_type: cash|credit. status: PAID|PARTIAL|PENDING|CANCELLED."""

    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    sale_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    subtotal = Column(Float, nullable=False)
    discount = Column(Float, default=0.0, nullable=False)
    total = Column(Float, nullable=False)
    payment_type = Column(String(10), default="cash", nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="PAID", nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Sale(id={self.id}, total={self.total}, status='{self.status}')>"


class SaleItem(Base):
    """Individual product line within a sale."""

    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<SaleItem(id={self.id}, sale_id={self.sale_id}, "
            f"product_id={self.product_id}, qty={self.quantity})>"
        )
