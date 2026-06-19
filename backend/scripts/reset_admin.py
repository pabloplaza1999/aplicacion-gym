"""Reset admin password to the configured ADMIN_INITIAL_PASSWORD.

Sets is_temporary=True so the operator must change it on next login.
Updates the existing user — never deletes or recreates.

Usage (inside the backend container):
    python scripts/reset_admin.py

Or on the host with the backend virtualenv active:
    cd backend && python scripts/reset_admin.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.database.session import SessionLocal
from app.models.admin_user import AdminUser
from app.services.auth_service import hash_password


def main() -> None:
    password = settings.admin_initial_password
    if not password:
        print("[ERROR] ADMIN_INITIAL_PASSWORD no está configurada en .env")
        sys.exit(1)

    db = SessionLocal()
    try:
        user = db.query(AdminUser).first()
        if not user:
            print("[ERROR] No existe un usuario admin. Arranca el backend primero para que el seed lo cree.")
            sys.exit(1)

        user.hashed_password = hash_password(password)
        user.is_temporary = True
        db.commit()
        print(f"[OK] Contraseña del admin '{user.username}' reseteada a temporal.")
        print("[OK] El operador deberá cambiarla en el primer login.")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
