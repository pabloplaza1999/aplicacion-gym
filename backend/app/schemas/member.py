"""Pydantic schemas for member validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, field_validator


class _MemberValidators(BaseModel):
    """Shared field validators for MemberCreate and MemberUpdate.
    Fields live in subclasses; check_fields=False is required for inherited validators.
    """

    @field_validator('full_name', check_fields=False)
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and any(char.isdigit() for char in v):
            raise ValueError("El nombre no debe contener números")
        return v

    @field_validator('phone', check_fields=False)
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.isdigit():
            raise ValueError("El teléfono debe contener solo números")
        return v

    @field_validator('document', check_fields=False)
    @classmethod
    def validate_document(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() != '' and not v.isdigit():
            raise ValueError("El documento debe contener solo números")
        return v

    @field_validator('email', mode='before', check_fields=False)
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        """Email contract (backend is source of truth):
        - valid string  → strip() → EmailStr validates → stored
        - ""  / " "     → strip() == "" → None → sets NULL in DB (explicit delete)
        - null/omitted  → None / not in update_dict → no change (via exclude_unset)
        Frontend normalization is a courtesy; this validator is the enforcement layer.
        """
        if not isinstance(v, str):
            return v
        stripped = v.strip()
        return stripped if stripped else None


class MemberBase(BaseModel):
    """Base schema for member fields."""

    full_name: str = Field(..., min_length=1, max_length=255, description="Cliente")
    phone: str = Field(..., min_length=1, max_length=20, description="Teléfono")
    document: Optional[str] = Field(None, max_length=20, description="Documento (opcional)")
    email: Optional[EmailStr] = Field(None, description="Correo electrónico (opcional)")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas")


class MemberCreate(MemberBase, _MemberValidators):
    """Schema for creating a new member."""


class MemberUpdate(_MemberValidators):
    """Schema for updating a member."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Cliente")
    phone: Optional[str] = Field(None, min_length=1, max_length=20, description="Teléfono")
    document: Optional[str] = Field(None, max_length=20, description="Documento (opcional)")
    email: Optional[EmailStr] = Field(None, description="Correo electrónico (opcional)")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas")
    is_active: Optional[bool] = Field(None, description="Activo")


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
