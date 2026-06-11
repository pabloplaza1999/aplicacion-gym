"""Inventory movement model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.models.base import Base


class InventoryMovement(Base):
    """Tracks every stock change: entries, sales, manual adjustments."""

    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    # 'entry' | 'sale' | 'adjustment'
    type = Column(String(20), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)       # positive = in, negative = out
    stock_before = Column(Integer, nullable=False)
    stock_after = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return (
            f"<InventoryMovement(id={self.id}, product_id={self.product_id}, "
            f"type='{self.type}', qty={self.quantity})>"
        )
