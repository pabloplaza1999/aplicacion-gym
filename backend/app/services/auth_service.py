"""Auth service — JWT emission, password verification and change."""

from datetime import datetime, timedelta

import jwt

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.admin_user import AdminUser
from app.repositories.admin_user_repository import AdminUserRepository
from app.schemas.auth import TokenResponse

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthError(Exception):
    pass


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = AdminUserRepository(db)

    def login(self, username: str, password: str) -> TokenResponse:
        user = self.repo.get_by_username(username)
        if not user or not _pwd_context.verify(password, user.hashed_password):
            raise AuthError("Usuario o contraseña incorrectos")
        return TokenResponse(access_token=_create_token(user), is_temporary=user.is_temporary)

    def change_password(self, user: AdminUser, new_password: str, confirm_password: str) -> TokenResponse:
        if new_password != confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        hashed = _pwd_context.hash(new_password)
        updated = self.repo.update_password(user, hashed, is_temporary=False)
        return TokenResponse(access_token=_create_token(updated), is_temporary=False)


def _create_token(user: AdminUser) -> str:
    expire = datetime.utcnow() + timedelta(hours=settings.jwt_expire_hours)
    payload = {"sub": user.username, "exp": expire, "is_temporary": user.is_temporary}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise AuthError("Token inválido o expirado")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)
