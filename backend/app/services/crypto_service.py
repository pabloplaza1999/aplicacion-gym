"""Fernet symmetric encryption helpers — used by notification settings to protect smtp_password."""

from cryptography.fernet import Fernet
from app.core.config import settings as app_settings


def _fernet() -> Fernet:
    key = app_settings.secret_key
    if not key:
        raise ValueError(
            "SECRET_KEY no está configurada en .env. "
            "Genera una con: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode())


def encrypt(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt(token: str) -> str:
    return _fernet().decrypt(token.encode()).decode()
