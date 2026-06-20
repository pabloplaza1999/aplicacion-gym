"""FastAPI shared dependencies — auth token validation and access control."""

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


def require_super_admin(user: AdminUser = Depends(require_active_user)) -> AdminUser:
    """Require super_admin role. Regular admin users are rejected with 403."""
    if getattr(user, "role", "admin") != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido al Super Administrador",
        )
    return user


def require_module(module_key: str):
    """Return a dependency that enforces module licensing for the current gym.

    super_admin bypasses module checks. Unknown gym/module defaults to active=True
    to avoid breaking existing installations during migration (A3 + A5).
    """
    def _check(user: AdminUser = Depends(require_active_user)) -> AdminUser:
        if getattr(user, "role", "admin") == "super_admin":
            return user
        from app.core.module_cache import module_is_active
        gym_id = getattr(user, "gym_id", None) or 1
        if not module_is_active(gym_id, module_key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Módulo no disponible en tu plan actual",
            )
        return user
    return _check
