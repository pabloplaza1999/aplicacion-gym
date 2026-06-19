"""FastAPI shared dependencies — auth token validation."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.admin_user import AdminUser
from app.repositories.admin_user_repository import AdminUserRepository
from app.services.auth_service import AuthError, verify_token

# auto_error=False so missing header → None (we raise 401 manually, not 403)
_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> AdminUser:
    """Validate Bearer token and return AdminUser. Allows is_temporary users."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
    try:
        payload = verify_token(credentials.credentials)
    except AuthError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
    username = payload.get("sub")
    user = AdminUserRepository(db).get_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
    return user


def require_active_user(user: AdminUser = Depends(get_current_user)) -> AdminUser:
    """Require a non-temporary authenticated user. Blocks access until password is changed."""
    if user.is_temporary:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes cambiar tu contraseña antes de continuar",
        )
    return user
