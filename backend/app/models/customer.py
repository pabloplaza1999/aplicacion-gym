"""Customer and credit payment models — Tienda Fase B."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from app.models.base import Base


class Customer(Base):
    """Store customer — may or may not be a gym member."""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    document = Column(String(30), nullable=True, index=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name='{self.name}')>"


class CreditPayment(Base):
    """Immutable payment record for a credit sale (abono). Never edited or deleted."""

    __tablename__ = "credit_payments"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    method = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    paid_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<CreditPayment(id={self.id}, sale_id={self.sale_id}, amount={self.amount})>"
