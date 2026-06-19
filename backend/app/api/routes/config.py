"""Platform configuration endpoint — exposes active module state."""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/features")
def get_features() -> dict:
    """Returns the active state of all platform modules.

    Public endpoint — no authentication required.
    TD-65: revisit authentication requirement when evolving to cloud multi-tenant (F8+).
    """
    return {
        "core": {
            "members": True,
            "memberships": True,
            "attendance": True,
            "payments": True,
            "dashboard": True,
            "auth": True,
            "backup": True,
        },
        "premium": {
            "notifications": settings.module_notifications,
            "body_tracking": settings.module_body_tracking,
            "store": settings.module_store,
        },
    }
