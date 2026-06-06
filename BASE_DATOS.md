# BASE_DATOS.md
SQLite. Archivo: `gym.db`. Auto-creación vía `Base.metadata.create_all()`.

## Tablas

**members:** id PK | full_name | phone | document? | registration_date auto | notes? | is_active=true

**plans:** id PK | name | price | duration_days | plan_type(monthly/quarterly/semiannual/annual)

**memberships:** id PK | member_id FK | plan_id FK | start_date | end_date(auto) | status(active/expiring/expired) | freeze_days=0

**payments:** id PK | member_id FK | membership_id FK? | amount | payment_method(cash/transfer/qr/nequi) | payment_date auto

**body_measurements:** id PK | member_id FK UNIQUE | updated_at auto
→ age(int,años) | height | shoulder | chest | waist | hip | bicep | forearm | calf | thigh (float,cm) | body_weight(float,kg)
→ todos nullable

## Relaciones
members 1→N memberships | members 1→N payments | members 1→1 body_measurements
plans 1→N memberships | memberships 1→N payments

## Seed (init_db.py)
Plan Diario $5.000/1d | Plan Mensual $60.000/30d | Plan Trimestral $150.000/90d | Plan Semestral $250.000/180d
