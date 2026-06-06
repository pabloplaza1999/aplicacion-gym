"""Body measurement schemas."""

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, Any
from datetime import datetime


class BodyMeasurementBase(BaseModel):

    age:         Optional[int]   = Field(None, ge=0,  le=150)
    height:      Optional[float] = Field(None, ge=0,  le=1000, description="cm")
    shoulder:    Optional[float] = Field(None, ge=0,  le=1000, description="cm")
    chest:       Optional[float] = Field(None, ge=0,  le=1000, description="cm")
    waist:       Optional[float] = Field(None, ge=0,  le=1000, description="cm")
    hip:         Optional[float] = Field(None, ge=0,  le=1000, description="cm")
    bicep:       Optional[float] = Field(None, ge=0,  le=1000, description="cm")
    forearm:     Optional[float] = Field(None, ge=0,  le=1000, description="cm")
    calf:        Optional[float] = Field(None, ge=0,  le=1000, description="cm")
    thigh:       Optional[float] = Field(None, ge=0,  le=1000, description="cm")
    body_weight: Optional[float] = Field(None, ge=0,  le=5000, description="kg")

    @field_validator('age', mode='before')
    @classmethod
    def coerce_age(cls, v: Any) -> Any:
        """Coerce age to int, handling floats and empty strings."""
        if v is None or (isinstance(v, str) and v.strip() == ''):
            return None
        try:
            return int(float(str(v)))
        except (ValueError, TypeError):
            return v

    @field_validator(
        'height', 'shoulder', 'chest', 'waist', 'hip',
        'bicep', 'forearm', 'calf', 'thigh', 'body_weight',
        mode='before',
    )
    @classmethod
    def empty_str_to_none(cls, v: Any) -> Any:
        """Convert empty string or whitespace to None before type coercion."""
        if v is None or (isinstance(v, str) and v.strip() == ''):
            return None
        return v


class BodyMeasurementUpsert(BodyMeasurementBase):
    model_config = ConfigDict(extra='ignore')


class BodyMeasurementRead(BodyMeasurementBase):
    id:         int
    member_id:  int
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
