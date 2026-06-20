"""Application configuration."""

from datetime import timedelta
from pydantic import model_validator
from pydantic_settings import BaseSettings

# Colombia operates at UTC-5 year-round (no DST).
# Used for converting UTC datetimes to local business dates (e.g. Plan Día end-of-day).
BOGOTA_OFFSET = timedelta(hours=-5)

_DEV_JWT_KEY = "dev-only-insecure-jwt-key-change-in-prod"


class Settings(BaseSettings):
    """Application settings."""

    # Project
    project_name: str = "Gym Platform"
    project_version: str = "1.2.0"
    # SEC-011: secure-by-default. Production runs with debug=False.
    # Development must opt in explicitly with DEBUG=true in its own .env.
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./gym.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Notifications — Fernet key for encrypting smtp_password in DB.
    # SEC-009: must be UNIQUE per installation (never shared between deployments).
    # In production (debug=False) it is mandatory — see _validate_production_secrets.
    secret_key: str = ""

    # JWT auth — signs operator session tokens. Independent of secret_key (different
    # rotation cycle and format). Generate with: python -c "import secrets; print(secrets.token_hex(32))"
    jwt_secret_key: str = _DEV_JWT_KEY
    jwt_expire_hours: int = 8

    # Admin initial password — used for first-startup seed and manual reset (scripts/reset_admin.py).
    # In production, set a strong value in .env before first launch.
    admin_initial_password: str = "admin123"

    # Super Admin password — used for super_admin user seed and manual reset (scripts/reset_super_admin.py).
    # Not required if super_admin functionality is not used. Mandatory in production when set.
    super_admin_password: str = ""

    # Rate limiting — login endpoint only. Override via .env if needed.
    login_rate_limit_window: int = 60   # seconds in the sliding window
    login_rate_limit_max_attempts: int = 20  # max attempts per IP per window

    # Backup
    db_path: str = "/app/data/gym.db"
    backup_dir: str = "/app/data/backups"
    max_auto_backups: int = 30
    max_manual_backups: int = 10

    # ── Gym identity — used for initial licensing seed ──────────────────────────
    # Set before first launch on a new installation.
    gym_name: str = "Gym"
    gym_plan: str = "professional"  # starter / professional / premium

    # ── Feature flags — Premium modules ────────────────────────────────────────
    # Opt-out model for modules already in production: default=True preserves
    # existing behavior for installations that don't set the flag in .env.
    # These flags are used ONLY during initial DB seed (_migrate_to_licensing_system).
    # After seed, the gym_modules table is the source of truth.
    module_notifications: bool = True   # P-01 Comunicación Automatizada
    module_body_tracking: bool = True   # P-07 Seguimiento Corporal
    module_store: bool = True           # Tienda (activo en todas las instalaciones actuales)

    class Config:
        env_file = ".env"
        case_sensitive = False

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        """Fail fast at startup if a production deploy lacks required secrets.

        Runs for every process that imports `settings` (API and scheduler).
        SEC-009: SECRET_KEY mandatory in production.
        F2: JWT_SECRET_KEY and ADMIN_INITIAL_PASSWORD also mandatory in production.
        """
        if not self.debug:
            errors = []
            if not self.secret_key:
                errors.append(
                    "SECRET_KEY es obligatoria. "
                    "Genera una con: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
                )
            if not self.jwt_secret_key or self.jwt_secret_key == _DEV_JWT_KEY:
                errors.append(
                    "JWT_SECRET_KEY es obligatoria y debe ser única por instalación. "
                    "Genera una con: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
            if not self.admin_initial_password:
                errors.append(
                    "ADMIN_INITIAL_PASSWORD es obligatoria para el seed del primer usuario admin."
                )
            if self.super_admin_password and self.super_admin_password == self.admin_initial_password:
                errors.append(
                    "SUPER_ADMIN_PASSWORD no puede ser igual a ADMIN_INITIAL_PASSWORD."
                )
            if errors:
                raise ValueError(
                    "Configuración de producción incompleta (DEBUG=false). "
                    "Revisa el archivo .env:\n" + "\n".join(f"  - {e}" for e in errors)
                )
        return self


settings = Settings()
