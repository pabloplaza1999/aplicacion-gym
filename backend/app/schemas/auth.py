"""Auth schemas — login, token and password change."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_temporary: bool


class ChangePasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8)
    confirm_password: str


class AdminUserRead(BaseModel):
    username: str
    is_temporary: bool

    model_config = {"from_attributes": True}
