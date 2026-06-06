"""Member model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.models.base import Base


class Member(Base):
    """Member model for gym clients."""

    __tablename__ = "members"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Fields
    full_name = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    document = Column(String(20), nullable=True, unique=True)
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Member(id={self.id}, full_name='{self.full_name}', phone='{self.phone}')>"
