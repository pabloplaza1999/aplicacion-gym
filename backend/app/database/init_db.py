"""Database initialization with seed data."""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select, text, inspect
from app.database.session import engine, SessionLocal
from app.models.base import Base
from app.models.plan import Plan
from app.models.body_measurement import BodyMeasurement  # noqa: F401 — ensures table is created


def _add_column_if_missing(table: str, column: str, ddl: str) -> None:
    """Add a column to an existing SQLite table only if it is missing (idempotent)."""
    inspector = inspect(engine)
    columns = {c["name"] for c in inspector.get_columns(table)}
    if column not in columns:
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))
        print(f"[OK] Migración: columna {table}.{column} añadida")


def _run_migrations() -> None:
    """Lightweight idempotent migrations for pre-existing DBs (create_all won't alter)."""
    _add_column_if_missing("memberships", "is_active", "is_active BOOLEAN NOT NULL DEFAULT 1")
    # Fase A — soporte de valeras (voucher)
    _add_column_if_missing("plans", "entry_count", "entry_count INTEGER NOT NULL DEFAULT 0")
    _add_column_if_missing("memberships", "entries_total", "entries_total INTEGER")


def _seed_voucher_plans() -> None:
    """Seed valera (voucher) plans idempotently, also on already-populated DBs."""
    db = SessionLocal()
    try:
        voucher_plans = [
            {"id": 5, "name": "Valera 7 días", "price": 30000,
             "duration_days": 30, "plan_type": "voucher", "entry_count": 7},
            {"id": 6, "name": "Valera 15 días", "price": 40000,
             "duration_days": 30, "plan_type": "voucher", "entry_count": 15},
        ]
        added = False
        for vp in voucher_plans:
            exists = db.query(Plan).filter(Plan.name == vp["name"]).first()
            if not exists:
                db.add(Plan(**vp))
                added = True
        if added:
            db.commit()
            print("[OK] Seed: planes de valera (voucher) añadidos")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding voucher plans: {e}")
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database with tables and seed data."""

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Lightweight migrations for existing databases
    _run_migrations()

    # Seed plans (only if they don't exist)
    db = SessionLocal()
    try:
        # Check if plans already exist
        existing_plans = db.query(Plan).count()

        if existing_plans == 0:
            # Seed initial plans
            plans = [
                Plan(
                    id=1,
                    name="Plan Día",
                    price=7000,
                    duration_days=1,
                    plan_type="daily",
                ),
                Plan(
                    id=2,
                    name="Plan Básico",
                    price=60000,
                    duration_days=30,
                    plan_type="monthly",
                ),
                Plan(
                    id=3,
                    name="Funcional y Musculación",
                    price=120000,
                    duration_days=30,
                    plan_type="monthly",
                ),
                Plan(
                    id=4,
                    name="Entrenamiento Personalizado",
                    price=210000,
                    duration_days=30,
                    plan_type="premium",
                ),
            ]

            db.add_all(plans)
            db.commit()
            print("[OK] Database initialized and plans seeded successfully")
        else:
            print(f"[OK] Database already initialized ({existing_plans} plans found)")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error initializing database: {e}")
        raise
    finally:
        db.close()

    # Seed valera plans (idempotent, runs on fresh and existing DBs)
    _seed_voucher_plans()


if __name__ == "__main__":
    init_db()
