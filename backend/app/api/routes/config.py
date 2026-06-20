"""Platform configuration endpoint — exposes active module state."""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/config", tags=["config"])

_GYM_ID = 1  # Single-tenant installation — always gym_id=1


@router.get("/features")
def get_features() -> dict:
    """Returns the active state of all platform modules.

    Source of truth: module_cache (DB-backed). Falls back to .env feature flags
    when the gym has not been seeded yet (A3 backward compatibility).

    Public endpoint — no authentication required.
    TD-65: revisit authentication requirement when evolving to cloud multi-tenant (F8+).
    """
    from app.core.module_cache import has_gym, module_is_active

    def _flag(module_key: str, settings_attr: str) -> bool:
        if has_gym(_GYM_ID):
            return module_is_active(_GYM_ID, module_key)
        return getattr(settings, settings_attr, True)

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
            "notifications": _flag("MODULE_NOTIFICATIONS", "module_notifications"),
            "body_tracking": _flag("MODULE_BODY_TRACKING", "module_body_tracking"),
            "store": _flag("MODULE_STORE", "module_store"),
        },
    }
