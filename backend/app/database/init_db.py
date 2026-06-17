"""Database initialization with seed data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text, inspect
from app.database.session import engine, SessionLocal
from app.models.base import Base
from app.models.plan import Plan
from app.models.body_measurement import BodyMeasurement  # noqa: F401
from app.models.product import ProductCategory, Product  # noqa: F401
from app.models.inventory import InventoryMovement  # noqa: F401
from app.models.sale import Sale, SaleItem  # noqa: F401
from app.models.customer import Customer, CreditPayment  # noqa: F401
from app.models.notification import NotificationLog, NotificationSettings  # noqa: F401


def _add_column_if_missing(table: str, column: str, ddl: str) -> None:
    """Add a column to an existing SQLite table only if it is missing (idempotent)."""
    inspector = inspect(engine)
    columns = {c["name"] for c in inspector.get_columns(table)}
    if column not in columns:
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))
        print(f"[OK] Migración: columna {table}.{column} añadida")


def _migrate_sale_status() -> None:
    """Idempotent: convert legacy status values completed→PAID, cancelled→CANCELLED."""
    with engine.begin() as conn:
        n1 = conn.execute(text("SELECT COUNT(*) FROM sales WHERE status = 'completed'")).scalar()
        if n1:
            conn.execute(text("UPDATE sales SET status = 'PAID' WHERE status = 'completed'"))
            print(f"[OK] Migración: {n1} ventas 'completed' → 'PAID'")
        n2 = conn.execute(text("SELECT COUNT(*) FROM sales WHERE status = 'cancelled'")).scalar()
        if n2:
            conn.execute(text("UPDATE sales SET status = 'CANCELLED' WHERE status = 'cancelled'"))
            print(f"[OK] Migración: {n2} ventas 'cancelled' → 'CANCELLED'")


def _attendance_unique_covers_membership() -> bool:
    """Return True if the attendances UNIQUE constraint already uses membership_id."""
    with engine.connect() as conn:
        for row in conn.execute(text("PRAGMA index_list(attendances)")).fetchall():
            if row[2] != 1:  # not unique
                continue
            cols = [r[2] for r in conn.execute(text(f"PRAGMA index_info({row[1]})")).fetchall()]
            if "membership_id" in cols and "member_id" not in cols:
                return True
    return False


def _migrate_attendance_unique_constraint() -> None:
    """Idempotent: recreate attendances table replacing UNIQUE(member_id, check_in_date)
    with UNIQUE(membership_id, check_in_date).

    The original constraint blocked check-in when the same member had an attendance on the
    same calendar day under a *different* (old/inactive) membership. Scoping to membership_id
    allows each valera to independently track its own daily check-in.
    """
    if _attendance_unique_covers_membership():
        return  # already migrated

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS attendances_new (
                id INTEGER NOT NULL PRIMARY KEY,
                member_id INTEGER NOT NULL,
                membership_id INTEGER NOT NULL,
                check_in_at DATETIME NOT NULL,
                check_in_date DATE NOT NULL,
                UNIQUE (membership_id, check_in_date)
            )
        """))
        conn.execute(text("""
            INSERT OR IGNORE INTO attendances_new
                (id, member_id, membership_id, check_in_at, check_in_date)
            SELECT id, member_id, membership_id, check_in_at, check_in_date
            FROM attendances
        """))
        conn.execute(text("DROP TABLE attendances"))
        conn.execute(text("ALTER TABLE attendances_new RENAME TO attendances"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_attendances_id ON attendances (id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_attendances_member_id ON attendances (member_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_attendances_membership_id ON attendances (membership_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_attendances_check_in_date ON attendances (check_in_date)"))
    print("[OK] Migración: attendances UNIQUE constraint migrada a (membership_id, check_in_date)")


def _migrate_sales_to_member_id() -> None:
    """Idempotent: backfill sales.member_id from customers.member_id for linked customers.

    For pre-Cliente-Único sales (customer_id set, member_id NULL):
    - Linked customer (customer.member_id IS NOT NULL) → copy member_id to the sale.
    - Store-only customer (customer.member_id IS NULL) → sale.member_id remains NULL.
    Rows already migrated (member_id IS NOT NULL) are skipped.
    """
    with engine.begin() as conn:
        count = conn.execute(text(
            "SELECT COUNT(*) FROM sales WHERE customer_id IS NOT NULL AND member_id IS NULL"
        )).scalar()
        if not count:
            return
        conn.execute(text("""
            UPDATE sales
            SET member_id = (
                SELECT c.member_id FROM customers c WHERE c.id = sales.customer_id
            )
            WHERE customer_id IS NOT NULL AND member_id IS NULL
        """))
        migrated = conn.execute(text(
            "SELECT COUNT(*) FROM sales WHERE customer_id IS NOT NULL AND member_id IS NOT NULL"
        )).scalar()
        print(f"[OK] Cliente Único: {migrated}/{count} ventas migradas a member_id")


def _purge_orphaned_cancelled_sales() -> None:
    """Delete CANCELLED sales whose owner no longer exists, plus dependent records.

    Handles both models:
    - New (member_id set): orphan if member was deleted.
    - Legacy (customer_id set, no member_id): orphan if customer was deleted.
    - Anonymous (both NULL): always purge.
    """
    with engine.begin() as conn:
        orphan_condition = (
            "status = 'CANCELLED' AND ("
            "  (member_id IS NOT NULL AND member_id NOT IN (SELECT id FROM members))"
            "  OR (member_id IS NULL AND customer_id IS NOT NULL"
            "      AND customer_id NOT IN (SELECT id FROM customers))"
            "  OR (member_id IS NULL AND customer_id IS NULL)"
            ")"
        )
        count = conn.execute(text(
            f"SELECT COUNT(*) FROM sales WHERE {orphan_condition}"
        )).scalar()
        if not count:
            return
        # TD-21: credit_payments must be deleted before sales to avoid orphaned records
        conn.execute(text(
            f"DELETE FROM credit_payments WHERE sale_id IN "
            f"(SELECT id FROM sales WHERE {orphan_condition})"
        ))
        conn.execute(text(
            f"DELETE FROM inventory_movements WHERE sale_id IN "
            f"(SELECT id FROM sales WHERE {orphan_condition})"
        ))
        conn.execute(text(
            f"DELETE FROM sale_items WHERE sale_id IN "
            f"(SELECT id FROM sales WHERE {orphan_condition})"
        ))
        conn.execute(text(f"DELETE FROM sales WHERE {orphan_condition}"))
        print(f"[OK] Purga: {count} ventas anuladas sin cliente válido eliminadas")


def _purge_orphaned_credit_payments() -> None:
    """TD-21: Delete invalid credit_payments (idempotent). Two cases:

    1. Sale no longer exists (classic orphan after sale deletion without cascade).
    2. Sale exists but is payment_type='cash' — cash sales never generate abonos by
       design; such records indicate ID reuse after sale deletion (SQLite reuses rowids).

    Running at startup ensures DB consistency regardless of how past sessions left it.
    The fix in delete_sale_cascade / delete_empty_sales prevents new orphans going forward.
    """
    with engine.begin() as conn:
        count_missing = conn.execute(text(
            "SELECT COUNT(*) FROM credit_payments "
            "WHERE sale_id NOT IN (SELECT id FROM sales)"
        )).scalar()
        count_cash = conn.execute(text(
            "SELECT COUNT(*) FROM credit_payments "
            "WHERE sale_id IN (SELECT id FROM sales WHERE payment_type = 'cash')"
        )).scalar()
        total = count_missing + count_cash
        if not total:
            return
        if count_missing:
            conn.execute(text(
                "DELETE FROM credit_payments "
                "WHERE sale_id NOT IN (SELECT id FROM sales)"
            ))
        if count_cash:
            conn.execute(text(
                "DELETE FROM credit_payments "
                "WHERE sale_id IN (SELECT id FROM sales WHERE payment_type = 'cash')"
            ))
        print(
            f"[OK] TD-21: {total} credit_payments inválidos eliminados "
            f"({count_missing} huérfanos, {count_cash} en ventas de contado)"
        )


def _deactivate_duplicate_active_vouchers() -> None:
    """Idempotent: deactivate surplus active vouchers per member, keeping the most recent.

    Selects the voucher with the highest start_date (tie-break: highest id) per member
    and sets is_active=False on all other active vouchers for that member.
    Runs only when duplicates exist.
    """
    with engine.begin() as conn:
        count = conn.execute(text("""
            SELECT COUNT(*) FROM memberships m
            JOIN plans p ON m.plan_id = p.id
            WHERE m.is_active = 1 AND p.plan_type = 'voucher'
            GROUP BY m.member_id
            HAVING COUNT(*) > 1
        """)).fetchall()
        if not count:
            return
        total = sum(r[0] - 1 for r in count)
        conn.execute(text("""
            UPDATE memberships SET is_active = 0
            WHERE is_active = 1
              AND id IN (
                SELECT m.id FROM memberships m
                JOIN plans p ON m.plan_id = p.id
                WHERE m.is_active = 1 AND p.plan_type = 'voucher'
                  AND m.id != (
                    SELECT m2.id FROM memberships m2
                    JOIN plans p2 ON m2.plan_id = p2.id
                    WHERE m2.member_id = m.member_id
                      AND m2.is_active = 1
                      AND p2.plan_type = 'voucher'
                    ORDER BY m2.start_date DESC, m2.id DESC
                    LIMIT 1
                  )
              )
        """))
        print(f"[OK] Corrección TD-02: {total} valeras duplicadas desactivadas")


def _deactivate_duplicate_active_non_voucher_memberships() -> None:
    """Idempotent: deactivate surplus active non-voucher memberships per member.

    Mirrors TD-02 for monthly/daily/premium plans. Before TD-05 was fixed,
    create_membership did not deactivate the previous membership, leaving stale
    is_active=True records. Those stale records trigger the Best State Wins
    suppression in get_membership_alerts(), hiding clients that should appear in
    expiring/expired alert buckets.

    Keeps the membership with the highest start_date (tie-break: highest id) per
    member and deactivates all others. Runs only when duplicates exist.
    """
    with engine.begin() as conn:
        count = conn.execute(text("""
            SELECT COUNT(*) FROM memberships m
            JOIN plans p ON m.plan_id = p.id
            WHERE m.is_active = 1 AND p.plan_type != 'voucher'
            GROUP BY m.member_id
            HAVING COUNT(*) > 1
        """)).fetchall()
        if not count:
            return
        total = sum(r[0] - 1 for r in count)
        conn.execute(text("""
            UPDATE memberships SET is_active = 0
            WHERE is_active = 1
              AND id IN (
                SELECT m.id FROM memberships m
                JOIN plans p ON m.plan_id = p.id
                WHERE m.is_active = 1 AND p.plan_type != 'voucher'
                  AND m.id != (
                    SELECT m2.id FROM memberships m2
                    JOIN plans p2 ON m2.plan_id = p2.id
                    WHERE m2.member_id = m.member_id
                      AND m2.is_active = 1
                      AND p2.plan_type != 'voucher'
                    ORDER BY m2.start_date DESC, m2.id DESC
                    LIMIT 1
                  )
              )
        """))
        print(f"[OK] Corrección: {total} membresías no-voucher duplicadas desactivadas")


def _run_migrations() -> None:
    """Lightweight idempotent migrations for pre-existing DBs (create_all won't alter)."""
    _add_column_if_missing("memberships", "is_active", "is_active BOOLEAN NOT NULL DEFAULT 1")
    _add_column_if_missing("plans", "entry_count", "entry_count INTEGER NOT NULL DEFAULT 0")
    _add_column_if_missing("memberships", "entries_total", "entries_total INTEGER")
    _add_column_if_missing("memberships", "frozen_at", "frozen_at DATETIME")
    _add_column_if_missing("memberships", "frozen_days_remaining", "frozen_days_remaining INTEGER")
    _add_column_if_missing("memberships", "freeze_count", "freeze_count INTEGER NOT NULL DEFAULT 0")
    # Notificaciones Fase 1 — datos de contacto y control interno
    _add_column_if_missing("members", "email", "email VARCHAR(255)")
    _add_column_if_missing("memberships", "last_notified_at", "last_notified_at DATETIME")
    # Fase B — sales
    _add_column_if_missing("sales", "customer_id", "customer_id INTEGER")
    _add_column_if_missing("sales", "payment_type", "payment_type VARCHAR(10) NOT NULL DEFAULT 'cash'")
    _migrate_sale_status()
    # Cliente Único — member_id must be added before purge so orphan logic can reference it
    _add_column_if_missing("sales", "member_id", "member_id INTEGER")
    _migrate_sales_to_member_id()
    _purge_orphaned_cancelled_sales()
    # Fase C — attendances constraint fix
    _migrate_attendance_unique_constraint()
    # TD-02 — deactivate surplus active vouchers from historical data
    _deactivate_duplicate_active_vouchers()
    # fix-dashboard-expiring — deactivate surplus active non-voucher memberships
    _deactivate_duplicate_active_non_voucher_memberships()
    # TD-21 — purge orphaned credit_payments left by prior code that lacked cascade delete
    _purge_orphaned_credit_payments()


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
            if not db.query(Plan).filter(Plan.name == vp["name"]).first():
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
    Base.metadata.create_all(bind=engine)
    _run_migrations()
    # NOTE: _migrate_historical_customer_ids() removed — Cliente Único uses member_id directly.
    # That function created Customer rows from Member data, which would reverse the migration.

    db = SessionLocal()
    try:
        existing_plans = db.query(Plan).count()
        if existing_plans == 0:
            plans = [
                Plan(id=1, name="Plan Día", price=7000, duration_days=1, plan_type="daily"),
                Plan(id=2, name="Plan Básico", price=60000, duration_days=30, plan_type="monthly"),
                Plan(id=3, name="Funcional y Musculación", price=120000, duration_days=30, plan_type="monthly"),
                Plan(id=4, name="Entrenamiento Personalizado", price=210000, duration_days=30, plan_type="premium"),
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

    _seed_voucher_plans()


if __name__ == "__main__":
    init_db()
