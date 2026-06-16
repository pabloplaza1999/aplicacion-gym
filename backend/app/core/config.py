"""Application configuration."""

from datetime import timedelta
from pydantic import model_validator
from pydantic_settings import BaseSettings
from pathlib import Path

# Colombia operates at UTC-5 year-round (no DST).
# Used for converting UTC datetimes to local business dates (e.g. Plan Día end-of-day).
BOGOTA_OFFSET = timedelta(hours=-5)


class Settings(BaseSettings):
    """Application settings."""

    # Project
    project_name: str = "Gym Management System"
    project_version: str = "0.1.0"
    # SEC-011: secure-by-default. Production runs with debug=False.
    # Development must opt in explicitly with DEBUG=true in its own .env.
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./gym.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Notifications — Fernet key for encrypting smtp_password in DB.
    # Generate once with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    # SEC-009: must be UNIQUE per installation (never shared between deployments).
    # In production (debug=False) it is mandatory — see _validate_production_secrets.
    # In development (debug=True) it may stay empty; SMTP encryption degrades gracefully
    # (crypto_service raises only when SMTP is actually used).
    secret_key: str = ""

    # Backup
    db_path: str = "/app/data/gym.db"
    backup_dir: str = "/app/data/backups"
    max_auto_backups: int = 30
    max_manual_backups: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        """SEC-009: fail fast at startup if a production deploy lacks SECRET_KEY.

        Runs for every process that imports `settings` (API and scheduler),
        so neither can boot in production without a key.
        """
        if not self.debug and not self.secret_key:
            raise ValueError(
                "SECRET_KEY es obligatoria en producción (DEBUG=false). "
                "Defínela en .env con una clave ÚNICA por instalación (no la reutilices entre despliegues). "
                "Genera una con: "
                "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        return self


settings = Settings()
