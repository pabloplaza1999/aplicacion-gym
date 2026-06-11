# BASE_DATOS.md
SQLite. Archivo: `gym.db`. Auto-creacion via `Base.metadata.create_all()`.

## Tablas

**members:** id PK | full_name | phone | document? | registration_date auto | notes? | is_active=true

**plans:** id PK | name | price | duration_days | plan_type(monthly/quarterly/semiannual/annual) | entry_count=0

**memberships:** id PK | member_id FK | plan_id FK | start_date | end_date(auto) | is_active=true | entries_total?
-> freeze: frozen_at? | frozen_days_remaining? | freeze_count=0

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

**sales:** id PK | member_id?(legado, inerte) | customer_id FK? | sale_date auto | subtotal | discount=0 | total | payment_type(cash/credit)=cash | notes? | status(PAID/PARTIAL/PENDING/CANCELLED)=PAID | created_at auto
-> status semántica: PAID=pagada completo | PENDING=crédito sin abonos | PARTIAL=crédito con abonos parciales | CANCELLED=anulada
-> balance no almacenado; calculado en runtime: total - SUM(credit_payments.amount)
-> member_id: columna legada (Fase A), no mapeada en ORM, ignorada por SQLAlchemy (TD-19)

**sale_items:** id PK | sale_id FK | product_id FK | quantity | unit_price(snapshot al momento de venta) | subtotal

**credit_payments:** id PK | sale_id FK | amount | method(String) | notes? | paid_at auto | created_at auto
-> Inmutables: sin endpoints PUT/DELETE.
-> Al registrar abono: si total - SUM(abonos) ≤ 0.01 → sale.status = PAID, sino PARTIAL.

## Relaciones
members 1->N memberships | members 1->N payments | members 1->1 body_measurements | members 1->N attendances
members 1->1? customers (via customers.member_id UNIQUE)
plans 1->N memberships | memberships 1->N payments | memberships 1->N attendances
product_categories 1->N products | products 1->N inventory_movements | products 1->N sale_items
customers 1->N sales | sales 1->N sale_items | sales 1->N inventory_movements | sales 1->N credit_payments

## Seed (init_db.py)
Plan Dia $7.000/1d | Plan Basico $60.000/30d | Funcional y Musculacion $120.000/30d | Entrenamiento Personalizado $210.000/30d
Valera 7 dias $30.000/30d (entry_count=7) | Valera 15 dias $40.000/30d (entry_count=15)

## Migraciones idempotentes (_add_column_if_missing)
memberships: is_active | entries_total | frozen_at | frozen_days_remaining | freeze_count
plans: entry_count
sales: customer_id | payment_type
_migrate_sale_status(): UPDATE sales SET status='PAID' WHERE status='completed' (y 'cancelled'→'CANCELLED')
_migrate_historical_customer_ids(): lee member_id legado via raw SQL, crea Customer desde Member, actualiza customer_id via raw SQL
Tablas nuevas (customers, credit_payments) vía create_all por import en init_db.py — sin ALTER TABLE
