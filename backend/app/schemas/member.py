"""Pydantic schemas for member validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MemberBase(BaseModel):
    """Base schema for member fields."""

    full_name: str = Field(..., min_length=1, max_length=255, description="Cliente")
    phone: str = Field(..., min_length=1, max_length=20, description="Teléfono")
    document: Optional[str] = Field(
        None, max_length=20, description="Documento (opcional)"
    )
    notes: Optional[str] = Field(None, max_length=1000, description="Notas")


class MemberCreate(MemberBase):
    """Schema for creating a new member."""

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if any(char.isdigit() for char in v):
            raise ValueError("El nombre no debe contener números")
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("El teléfono debe contener solo números")
        return v

    @field_validator('document')
    @classmethod
    def validate_document(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() != '' and not v.isdigit():
            raise ValueError("El documento debe contener solo números")
        return v


class MemberUpdate(BaseModel):
    """Schema for updating a member."""

    full_name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Cliente"
    )
    phone: Optional[str] = Field(None, min_length=1, max_length=20, description="Teléfono")
    document: Optional[str] = Field(
        None, max_length=20, description="Documento (opcional)"
    )
    notes: Optional[str] = Field(None, max_length=1000, description="Notas")
    is_active: Optional[bool] = Field(None, description="Activo")

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if any(char.isdigit() for char in v):
                raise ValueError("El nombre no debe contener números")
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.isdigit():
                raise ValueError("El teléfono debe contener solo números")
        return v

    @field_validator('document')
    @classmethod
    def validate_document(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() != '' and not v.isdigit():
            raise ValueError("El documento debe contener solo números")
        return v


class MemberRead(MemberBase):
    """Schema for reading member data."""

    id: int = Field(..., description="ID del cliente")
    registration_date: datetime = Field(..., description="Fecha de registro")
    is_active: bool = Field(..., description="Activo")

    model_config = {"from_attributes": True}


class MemberListResponse(BaseModel):
    """Schema for list response."""

    total: int = Field(..., description="Total de clientes")
    items: list[MemberRead] = Field(..., description="Lista de clientes")
