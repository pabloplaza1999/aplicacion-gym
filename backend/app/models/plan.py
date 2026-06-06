"""Plan model."""

from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class Plan(Base):
    """Plan model for gym membership plans."""

    __tablename__ = "plans"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Fields
    name = Column(String(255), nullable=False, index=True)
    price = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)
    plan_type = Column(String(50), nullable=False, index=True)
    # Number of entries granted (used by "voucher" plans / valeras). 0 = date-based plan.
    entry_count = Column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Plan(id={self.id}, name='{self.name}', price={self.price})>"
