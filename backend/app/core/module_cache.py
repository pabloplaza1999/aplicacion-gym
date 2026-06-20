"""In-memory module activation cache. Keyed by gym_id → module_key → bool.

Loaded from DB at startup via load_from_db(); refreshed after Super Admin writes
via refresh_gym(). Default True for unknown gym/module preserves backward compat.
"""

_cache: dict[int, dict[str, bool]] = {}


def load(rows: list) -> None:
    """Rebuild the full cache from a list of GymModule ORM rows."""
    global _cache
    new_cache: dict[int, dict[str, bool]] = {}
    for row in rows:
        new_cache.setdefault(row.gym_id, {})[row.module_key] = row.active
    _cache = new_cache


def refresh_gym(gym_id: int, rows: list) -> None:
    """Rebuild cache for a single gym after a write operation."""
    _cache[gym_id] = {row.module_key: row.active for row in rows}


def has_gym(gym_id: int) -> bool:
    """Return True if the gym has any cache entries (cache is populated)."""
    return gym_id in _cache


def module_is_active(gym_id: int, module_key: str) -> bool:
    """Return True if the module is active for the gym. Defaults to True when not cached."""
    return _cache.get(gym_id, {}).get(module_key, True)


def load_from_db() -> None:
    """Load the full module cache from DB. Called at startup after init_db()."""
    from app.database.session import SessionLocal
    from app.models.gym import GymModule

    db = SessionLocal()
    try:
        rows = db.query(GymModule).all()
        load(rows)
        if rows:
            print(f"[OK] Caché de módulos cargado ({len(rows)} entradas)")
    except Exception as e:
        print(f"[WARNING] No se pudo cargar caché de módulos: {e}")
    finally:
        db.close()
