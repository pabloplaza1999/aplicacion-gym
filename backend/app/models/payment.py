"""Payment model."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from app.models.base import Base


class Payment(Base):
    """Payment model for membership payments."""

    __tablename__ = "payments"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    membership_id = Column(
        Integer, ForeignKey("memberships.id"), nullable=True, index=True
    )

    # Fields
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False, index=True)
    payment_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return (
            f"<Payment(id={self.id}, member_id={self.member_id}, "
            f"amount={self.amount}, method='{self.payment_method}')>"
        )
