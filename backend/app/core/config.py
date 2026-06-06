"""Application configuration."""

from pydantic_settings import BaseSettings
from pathlib import Path


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

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
