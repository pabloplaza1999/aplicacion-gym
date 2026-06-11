"""Product and category models."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, Boolean, DateTime, ForeignKey
from app.models.base import Base


class ProductCategory(Base):
    """Product category for grouping store items."""

    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ProductCategory(id={self.id}, name='{self.name}')>"


class Product(Base):
    """Store product with inventory tracking."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=False, index=True)
    name = Column(String(150), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)       # sale price
    cost = Column(Float, nullable=True)          # purchase cost (for margin calc)
    stock = Column(Integer, default=0, nullable=False)
    min_stock = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', stock={self.stock})>"
