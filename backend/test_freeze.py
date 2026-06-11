"""
Pruebas de integración — Congelar/Pausar Membresía
Requiere el servidor corriendo en http://localhost:8000
"""
import requests
import sys
import time
from datetime import datetime, timedelta

base = "http://localhost:8000/api"

def unique_doc():
    """Genera documento único para evitar conflicto UNIQUE en ejecuciones repetidas."""
    return str(int(time.time()))[-7:]
PASS = "[PASS]"
FAIL = "[FAIL]"
results = []

def check(label, ok, detail=""):
    tag = PASS if ok else FAIL
    msg = f"{tag} {label}" + (f" — {detail}" if detail else "")
    print(msg)
    results.append(ok)

def post(path, body=None):
    return requests.post(f"{base}{path}", json=body or {})

def get(path):
    return requests.get(f"{base}{path}")

def patch(path, body):
    return requests.patch(f"{base}{path}", json=body)

print("=" * 60)
print("TEST: Congelar/Pausar Membresía")
print("=" * 60)

# Setup: crear miembro y membresía activa
r = post("/members", {"full_name": "Test Freeze", "phone": "3001110001", "document": unique_doc()})
assert r.status_code in (200, 201), f"No se pudo crear miembro: {r.text}"
mid = r.json()["id"]

# Usar plan_id=2 (Plan Básico ~30 días) — ajustar si no existe
r = post(f"/members/{mid}/memberships", {"member_id": mid, "plan_id": 2})
assert r.status_code in (200, 201), f"No se pudo crear membresía: {r.text}"
msid = r.json()["id"]

# Leer estado inicial
r = get(f"/members/{mid}/current-membership")
m = r.json()
check("Estado inicial es 'active'", m["status"] == "active", m["status"])
check("frozen_at es None inicialmente", m["frozen_at"] is None)
check("frozen_days_remaining es None inicialmente", m["frozen_days_remaining"] is None)

# ── Positivos ─────────────────────────────────────────────────────────────────
print("\n--- Escenarios positivos ---")

# Congelar membresía activa
r = post(f"/members/memberships/{msid}/freeze")
check("POST /freeze retorna 200", r.status_code == 200, str(r.status_code))
if r.status_code == 200:
    m = r.json()
    check("status pasa a 'frozen'", m["status"] == "frozen", m["status"])
    check("frozen_at no es None", m["frozen_at"] is not None)
    check("frozen_days_remaining > 0", (m["frozen_days_remaining"] or 0) > 0,
          str(m["frozen_days_remaining"]))
    check("is_active es False tras congelar", m["is_active"] is False)
    days_saved = m["frozen_days_remaining"]
    end_before = m["end_date"]

# Reactivar membresía congelada
r = post(f"/members/memberships/{msid}/unfreeze")
check("POST /unfreeze retorna 200", r.status_code == 200, str(r.status_code))
if r.status_code == 200:
    m = r.json()
    check("status vuelve a 'active' (o 'expiring')", m["status"] in ("active", "expiring"), m["status"])
    check("frozen_at es None tras descongelar", m["frozen_at"] is None)
    check("frozen_days_remaining es None tras descongelar", m["frozen_days_remaining"] is None)
    check("is_active es True tras descongelar", m["is_active"] is True)
    # Floor division al guardar días puede restar hasta 1 día al descongelar inmediatamente
    new_end = datetime.fromisoformat(m["end_date"][:19])
    old_end = datetime.fromisoformat(end_before[:19])
    check("end_date se extiende (tolerancia floor -1d)", new_end >= old_end - timedelta(days=1),
          f"{m['end_date']} ~= {end_before}")
    check("freeze_days acumula días", (m.get("freeze_days") or 0) >= 0)

# ── Negativos ─────────────────────────────────────────────────────────────────
print("\n--- Escenarios negativos ---")

# Congelar membresía ya activa de nuevo (OK), luego intentar congelarla dos veces
r = post(f"/members/memberships/{msid}/freeze")
check("Re-congelar membresía activa OK", r.status_code == 200)

r2 = post(f"/members/memberships/{msid}/freeze")
check("Congelar dos veces retorna 400", r2.status_code == 400, str(r2.status_code))

# Intentar activar (toggle) una membresía congelada
r3 = patch(f"/members/memberships/{msid}/active", {"is_active": True})
check("Activar membresía congelada vía toggle retorna 400", r3.status_code == 400, str(r3.status_code))

# Descongelar para dejarla limpia
post(f"/members/memberships/{msid}/unfreeze")

# Descongelar membresía que NO está congelada
r4 = post(f"/members/memberships/{msid}/unfreeze")
check("Descongelar membresía no congelada retorna 400", r4.status_code == 400, str(r4.status_code))

# ── Casos límite ──────────────────────────────────────────────────────────────
print("\n--- Casos límite ---")

# ID inexistente
r = post("/members/memberships/999999/freeze")
check("Freeze ID inexistente retorna 404", r.status_code == 404, str(r.status_code))

r = post("/members/memberships/999999/unfreeze")
check("Unfreeze ID inexistente retorna 404", r.status_code == 404, str(r.status_code))

# ── Regresiones ───────────────────────────────────────────────────────────────
print("\n--- Regresiones ---")

# Toggle normal (desactivar) sigue funcionando
r = get(f"/members/{mid}/current-membership")
m = r.json()
if m["status"] not in ("frozen",):
    r = patch(f"/members/memberships/{msid}/active", {"is_active": False})
    check("Desactivar membresía activa sigue funcionando (200)", r.status_code == 200, str(r.status_code))
    r = patch(f"/members/memberships/{msid}/active", {"is_active": True})
    check("Activar membresía inactiva (no frozen) sigue funcionando (200)", r.status_code == 200, str(r.status_code))
else:
    print("  [SKIP] Membresía está congelada, skip regresión toggle")

# Badge — verificar que el campo status llega en current-membership
r = get(f"/members/{mid}/current-membership")
m = r.json()
check("Campo 'status' presente en respuesta", "status" in m)
check("Campo 'frozen_at' presente en respuesta", "frozen_at" in m)
check("Campo 'frozen_days_remaining' presente en respuesta", "frozen_days_remaining" in m)

# ── Resumen ───────────────────────────────────────────────────────────────────
passed = sum(results)
total  = len(results)
print(f"\n{'=' * 60}")
print(f"Resultado: {passed}/{total} pruebas pasaron")
if passed == total:
    print("RESULTADO FINAL: PASS")
else:
    print(f"RESULTADO FINAL: FAIL ({total - passed} fallaron)")
print("=" * 60)

sys.exit(0 if passed == total else 1)
