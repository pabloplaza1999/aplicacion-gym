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
  pages/           ← Dashboard, Members, Payments
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
```

## Reglas críticas
- Rutas estáticas ANTES que dinámicas: `/payments/statistics` antes de `/payments/{id}`
- Frontend: Vite proxy `/api` → `localhost:8000`
- Estado local con useState/useCallback, sin estado global
- `ConfigDict(extra='ignore')` en todos los schemas Upsert
- `field_validator(mode='before')` convierte `""` → `None` en campos Optional numéricos
