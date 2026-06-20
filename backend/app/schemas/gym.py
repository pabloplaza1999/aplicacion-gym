"""Pydantic schemas for gym, license, and module management."""

from datetime import date, datetime
from pydantic import BaseModel


class GymRead(BaseModel):
    id: int
    name: str
    slug: str
    contact_name: str | None
    contact_email: str | None
    active: bool

    model_config = {"from_attributes": True}


class GymUpdate(BaseModel):
    name: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None


class LicenseRead(BaseModel):
    id: int
    plan_name: str
    valid_from: date | None
    valid_until: date | None
    status: str
    notes: str | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class LicensePlanUpdate(BaseModel):
    plan_name: str


class LicenseValidityUpdate(BaseModel):
    valid_from: date | None = None
    valid_until: date | None = None


class ModuleStatusRead(BaseModel):
    module_key: str
    name: str
    active: bool
    source: str
    activated_at: datetime | None
    deactivated_at: datetime | None


class ModuleToggle(BaseModel):
    active: bool
    notes: str | None = None


class GymLicensePanel(BaseModel):
    gym: GymRead
    license: LicenseRead | None
    modules: list[ModuleStatusRead]
