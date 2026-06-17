# ARQUITECTURA.md
Monolítica modular. Service Layer + Repository Pattern.

## Estructura
```
backend/app/
  api/routes/      ← FastAPI endpoints
  models/          ← SQLAlchemy ORM
  schemas/         ← Pydantic (separar Upsert vs Read)
  services/        ← lógica de negocio
  repositories/    ← acceso a datos
  database/        ← session.py, init_db.py

frontend/src/
  pages/           ← Dashboard, Members, Payments, Attendance, Store
  components/      ← StatCard, Badge, Modal, MemberInfo, Spinner, Empty
  services/api.ts  ← fetch tipado centralizado
  types/index.ts   ← interfaces TS
```

## Routers registrados en main.py
```
/api/members/*              members.py
/api/members/*/memberships  memberships.py
/api/payments/*             payments.py
/api/dashboard              dashboard.py
/api/plans                  plans.py
/api/members/*/measurements body_measurements.py
/api/attendance/*           attendance.py
/api/store/*                store.py
```

## Modulo Tienda — patron de transaccion atomica
SaleService.create_sale sigue el patron:
1. Validar stock de TODOS los items (sin escrituras)
2. flush() sale para obtener ID
3. Por cada item: create_sale_item + product.stock -= qty + create_movement(type=sale)
4. db.commit() unico al final
InsufficientStockError(ValueError) → HTTP 409 (distinto de ValueError → HTTP 400)

## Tienda Fase B — Cartera y Clientes
Customer: entidad independiente, vinculable opcionalmente a Member (member_id UNIQUE nullable).
SaleStatus: PAID | PARTIAL | PENDING | CANCELLED — almacenado como String, validado por Pydantic Literal.
PaymentType: cash | credit — idem.
CreditPayment: inmutable. Al registrar: valida PENDING/PARTIAL, valida amount ≤ balance (tolerancia 0.01), actualiza status venta, commit único.
balance calculado en runtime (_enrich_sale): total - SUM(credit_payments). No desnormalizado.
Dedup Customer por document en CustomerService.create_customer / update_customer (no restricción DB).
KPIs cartera (total_balance, sale_count, customer_count) en SaleRepository.get_cartera_kpis() — queries SQL agregadas, no iteración Python.
Rutas estáticas antes que dinámicas: POST /customers/from-member/{id} declarada antes de GET /customers/{id}.

## Cliente Único Phase 1 — Member como entidad canónica de ventas
Member es ahora la entidad canónica de clientes para toda la lógica de ventas (phase 1, backend-only).
sales.member_id (FK → members.id) reemplaza a sales.customer_id como columna activa del ORM.
_enrich_sale(): lee sale.member_id → devuelve customer_id=member_id (semantic reuse para retrocompatibilidad de frontend).
SaleCreate.customer_id contiene semánticamente un member_id — cero cambios de contrato API ni de frontend (diferido a Phase 2).
/store/customers/* son alias sobre MemberService + _member_as_customer() helper; CustomerService inactivo en este módulo.
MemberRepository ampliado: has_active_sales(), get_debt_total(), search_for_store(), has_memberships().
MemberService ampliado: get_members_for_store(), delete_customer_from_store(), hard_delete_member() con guard de ventas activas.
Purge dual-modelo: _purge_orphaned_cancelled_sales() valida contra members (new) y customers (legacy) según qué FK está set.
Tabla customers + CustomerService conservados transitoriamente (TD-48). CreditPayment sigue en customer.py (TD-49).
Migración idempotente en startup: _add_column_if_missing("sales","member_id") + _migrate_sales_to_member_id().
_migrate_historical_customer_ids() eliminado del startup — creaba Customer rows desde Members, revirtiendo la migración.

## Tienda Fase C — Reportes operativos
Endpoint único GET /store/reports (evita múltiples llamadas desde el frontend).
Tres bloques en un solo response: sales (SalesKPI + top_products), cartera (CarteraReport), inventory (InventoryReport).
Separación temporal: filtro de período solo afecta ventas y top_products; cartera e inventario son siempre actuales.
get_top_products: SQL puro (GROUP BY Product.id, SUM(SaleItem.quantity), ORDER BY units_sold DESC, LIMIT 5).
Import local de Sale/SaleItem dentro de get_top_products en ProductRepository para evitar import circular.
get_cartera_kpis_for_report extiende get_cartera_kpis() con pending_count, partial_count, oldest_debt_date.
low_stock filter: stock <= min_stock AND min_stock > 0 (evita falsos positivos en productos sin mínimo definido).
ReportsTab: componente aislado sin props — carga su propio estado; no comparte estado con otros tabs de Store.

## Integridad credit_payments (TD-21)
delete_sale_cascade elimina credit_payments antes de la venta (cascade explícito en Python).
delete_empty_sales resuelve IDs a eliminar en Python y limpia credit_payments antes del DELETE en bloque.
_purge_orphaned_credit_payments (startup, idempotente): elimina (a) credit_payments sin sale_id válido, (b) credit_payments en ventas payment_type='cash' — invariante de negocio: cash sales nunca generan abonos.

## Invariante de membresías activas
Un cliente puede tener como máximo una membresía no-voucher `is_active=True` en cualquier momento.
Puntos de escritura que la hacen cumplir:
- `renew_membership`: `deactivate_no_commit(old_id)` + `create()` en commit único (TD-05).
- `create_membership`: mismo patrón — desactiva la no-voucher activa anterior antes de crear la nueva (fix-dashboard-expiring).
- `set_membership_active(True)`: bloquea con `ValueError` (→ HTTP 400) si ya existe otra no-voucher activa para el mismo cliente.
- Startup `_deactivate_duplicate_active_non_voucher_memberships` (idempotente): limpia duplicados históricos al arrancar.
La regla de una sola valera activa (`valera-unica`) opera de forma independiente vía `ActiveVoucherExistsError`.

## Reglas críticas
- Rutas estáticas ANTES que dinámicas: `/payments/statistics` antes de `/payments/{id}`
- Frontend: Vite proxy `/api` → `localhost:8000`
- Estado local con useState/useCallback, sin estado global
- `ConfigDict(extra='ignore')` en todos los schemas Upsert
- `field_validator(mode='before')` convierte `""` → `None` en campos Optional numéricos
