"""Body measurements model."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from app.models.base import Base


class BodyMeasurement(Base):
    """Body measurements for a gym member (all in cm, weight in kg)."""

    __tablename__ = "body_measurements"

    id               = Column(Integer, primary_key=True, index=True)
    member_id        = Column(Integer, ForeignKey("members.id"), nullable=False, unique=True, index=True)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Personal
    age              = Column(Integer,  nullable=True)

    # Measurements (cm)
    height           = Column(Float, nullable=True)
    shoulder         = Column(Float, nullable=True)
    chest            = Column(Float, nullable=True)
    waist            = Column(Float, nullable=True)
    hip              = Column(Float, nullable=True)
    bicep            = Column(Float, nullable=True)
    forearm          = Column(Float, nullable=True)
    calf             = Column(Float, nullable=True)
    thigh            = Column(Float, nullable=True)

    # Weight (kg)
    body_weight      = Column(Float, nullable=True)
