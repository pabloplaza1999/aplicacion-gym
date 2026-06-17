# BASE_DATOS.md
SQLite. Archivo: `gym.db`. Auto-creacion via `Base.metadata.create_all()`.

## Tablas

**members:** id PK | full_name | phone | document?(UNIQUE) | email? | registration_date auto | notes? | is_active=true

**plans:** id PK | name | price | duration_days | plan_type(monthly/quarterly/semiannual/annual/**daily**) | entry_count=0

**memberships:** id PK | member_id FK | plan_id FK | start_date | end_date(auto) | is_active=true | entries_total?
-> freeze: frozen_at? | frozen_days_remaining? | freeze_count=0
-> end_date para plan_type=daily: calculado como 23:59:59 hora Bogotá (UTC-5) del día de inicio, almacenado como UTC.
   Fórmula: `(start_utc + BOGOTA_OFFSET).replace(23,59,59) - BOGOTA_OFFSET`. Ver `BOGOTA_OFFSET` en `app/core/config.py`.

**payments:** id PK | member_id FK | membership_id FK? | amount | payment_method(cash/transfer/qr/nequi) | payment_date auto

**body_measurements:** id PK | member_id FK UNIQUE | updated_at auto
-> age(int) | height | shoulder | chest | waist | hip | bicep | forearm | calf | thigh (float,cm) | body_weight(float,kg)
-> todos nullable

**attendances:** id PK | member_id FK | membership_id FK | check_in_date(date) | check_in_at auto
-> UNIQUE(member_id, check_in_date) — una asistencia por cliente por dia

**product_categories:** id PK | name UNIQUE | description? | is_active=true | created_at auto

**products:** id PK | category_id FK | name UNIQUE | description? | price | cost? | stock=0 | min_stock=0 | is_active=true | created_at auto

**inventory_movements:** id PK | product_id FK | type(entry/sale/adjustment) | quantity(+/-) | stock_before | stock_after | note? | sale_id FK? | created_at auto

**customers:** id PK | name(150) | document?(30) idx | phone?(30) | email?(100) | notes? | member_id FK UNIQUE? | created_at auto
-> member_id: relación 1:1 opcional con Member. NULL admitido (clientes externos sin cuenta de gym).
-> dedup por document: enforced en CustomerService (no restricción DB; SQLite admite NULL múltiple en UNIQUE).
-> [Cliente Único Phase 1] tabla conservada transitoriamente. CustomerService inactivo. Limpieza diferida a Phase 2 (TD-48).

**sales:** id PK | member_id FK? | customer_id?(legado, inerte) | sale_date auto | subtotal | discount=0 | total | payment_type(cash/credit)=cash | notes? | status(PAID/PARTIAL/PENDING/CANCELLED)=PAID | created_at auto
-> status semántica: PAID=pagada completo | PENDING=crédito sin abonos | PARTIAL=crédito con abonos parciales | CANCELLED=anulada
-> balance no almacenado; calculado en runtime: total - SUM(credit_payments.amount)
-> member_id: [Cliente Único Phase 1] columna canónica — FK → members.id, mapeada en ORM, usada por toda la lógica activa. TD-19 RESUELTO.
-> customer_id: columna legado (Fase B). No escrita por el backend nuevo. Conservada para compatibilidad transitoria (TD-48).

**sale_items:** id PK | sale_id FK | product_id FK | quantity | unit_price(snapshot al momento de venta) | subtotal

**credit_payments:** id PK | sale_id FK | amount | method(String) | notes? | paid_at auto | created_at auto
-> Inmutables: sin endpoints PUT/DELETE.
-> Al registrar abono: si total - SUM(abonos) ≤ 0.01 → sale.status = PAID, sino PARTIAL.

## Relaciones
members 1->N memberships | members 1->N payments | members 1->1 body_measurements | members 1->N attendances
members 1->1? customers (via customers.member_id UNIQUE) [transitorio — Phase 2 eliminará customers]
members 1->N sales (via sales.member_id) [Cliente Único Phase 1 — relación canónica]
plans 1->N memberships | memberships 1->N payments | memberships 1->N attendances
product_categories 1->N products | products 1->N inventory_movements | products 1->N sale_items
customers 1->N sales (via sales.customer_id) [legado, inerte — Phase 2 eliminará esta relación]

## Seed (init_db.py)
Plan Dia $7.000/1d | Plan Basico $60.000/30d | Funcional y Musculacion $120.000/30d | Entrenamiento Personalizado $210.000/30d
Valera 7 dias $30.000/30d (entry_count=7) | Valera 15 dias $40.000/30d (entry_count=15)

## Migraciones idempotentes (_add_column_if_missing)
memberships: is_active | entries_total | frozen_at | frozen_days_remaining | freeze_count
plans: entry_count
sales: customer_id | payment_type | member_id [Cliente Único Phase 1]
_migrate_sale_status(): UPDATE sales SET status='PAID' WHERE status='completed' (y 'cancelled'→'CANCELLED')
_migrate_sales_to_member_id(): [Cliente Único Phase 1] backfill sales.member_id desde customers.member_id para ventas con customer_id de cliente vinculado. Ventas de clientes solo-tienda (customer.member_id NULL) quedan con member_id=NULL.
_migrate_historical_customer_ids(): ELIMINADO en Cliente Único Phase 1 — creaba Customer rows desde Members en cada startup, revirtiendo la migración.
Tablas nuevas (customers, credit_payments) vía create_all por import en init_db.py — sin ALTER TABLE
