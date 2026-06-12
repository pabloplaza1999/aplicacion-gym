"""Application configuration."""

from datetime import timedelta
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
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./gym.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Notifications — Fernet key for encrypting smtp_password in DB.
    # Generate once with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    # If empty, SMTP password encryption is disabled and test-smtp will fail gracefully.
    secret_key: str = ""

    # Backup
    db_path: str = "/app/data/gym.db"
    backup_dir: str = "/app/data/backups"
    max_auto_backups: int = 30
    max_manual_backups: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
