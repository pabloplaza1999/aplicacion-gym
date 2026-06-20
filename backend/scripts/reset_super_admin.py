#!/usr/bin/env python
"""Reset super_admin password to SUPER_ADMIN_PASSWORD from .env (sets is_temporary=True).

Run from the backend/ directory:
    python scripts/reset_super_admin.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
os.chdir(Path(__file__).parent.parent)

from app.core.config import settings
from app.database.session import SessionLocal
from app.models.admin_user import AdminUser
from app.services.auth_service import hash_password


def reset_super_admin() -> None:
    if not settings.super_admin_password:
        print("[ERROR] SUPER_ADMIN_PASSWORD no está configurada en .env")
        sys.exit(1)

    db = SessionLocal()
    try:
        user = db.query(AdminUser).filter(AdminUser.username == "super_admin").first()
        if not user:
            print("[ERROR] Usuario super_admin no existe. Ejecuta init_db primero.")
            sys.exit(1)
        user.hashed_password = hash_password(settings.super_admin_password)
        user.is_temporary = True
        db.commit()
        print("[OK] Contraseña de super_admin reseteada (is_temporary=True — debe cambiarse en el primer login)")
    finally:
        db.close()


if __name__ == "__main__":
    reset_super_admin()
