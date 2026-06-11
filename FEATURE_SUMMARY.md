# FEATURE_SUMMARY.md

## Estado
✅ Sprint 1-7 completos (backend + frontend)
🔧 fix1 GET /api/plans + selector plan vacío
🔧 fix2 DELETE pago individual
🔧 fix3 member_name en tabla Pagos (JOIN)
🔧 fix4 Tab Info: datos cliente + medidas corporales
🔧 fix5 [object Object]: onUpdated() sin payload
🔧 fix6 422 measurements: BodyMeasurementUpsert separado de Read
🔧 fix7 422 persistente: field_validator empty_str→None
🔧 fix8 botón Eliminar cliente: deleteMember(id, true) → hard delete real (antes solo desactivaba)
🔧 fix9 Dashboard Membresías Activas: cuenta solo membresía vigente por cliente (estado derivado de end_date), ignora históricos/renovaciones y columna status obsoleta
🔧 fix10 Botón activar/desactivar membresía manual (independiente del cliente): columna memberships.is_active + estado 'inactive' + PATCH /memberships/{id}/active. Cliente inactivo NO altera la membresía. Dashboard excluye membresías desactivadas. Migración SQLite ALTER en init_db.
🔧 valeras-faseA Estructura de datos para valeras: plan_type='voucher', plans.entry_count, memberships.entries_total. Migración idempotente (_add_column_if_missing) + seed idempotente Valera 7 ($30.000/7/30d) y Valera 15 ($40.000/15/30d). Sin tocar _calculate_status, dashboard, current-membership ni pagos.
🔧 valeras-faseB Backend asistencias/consumo: tabla attendances (UNIQUE member_id+check_in_date), módulo attendance (model/schema/repo/service/route). Check-in por cédula: POST /api/attendance/check-in, GET /api/attendance/voucher-status/{document}. Consumo = COUNT(attendances) (fuente única); restantes = entries_total - count. Valera finaliza al agotar ingresos o vencer. create_membership puebla entries_total solo si plan voucher. Sin tocar _calculate_status, dashboard ni pagos.
🔧 valera-unica Regla: una sola valera activa vigente por cliente. MembershipService._has_active_valid_voucher() (is_active + no vencida + restantes>0 vía COUNT(attendances)); bloqueo en create_membership y renew_membership SOLO si el nuevo plan es voucher → ActiveVoucherExistsError → 409 Conflict en routes. Valera agotada/vencida NO bloquea. Mensuales sin cambios. Sin tocar dashboard, current-membership, pagos ni asistencia.
🔧 valera-renew-entries Riesgo 1 corregido: renew_membership ahora puebla entries_total (snapshot de entry_count del nuevo plan) cuando es voucher; mensual mantiene entries_total=None. Renovación a voucher queda operativa para check-in. Cambios limitados al flujo de renovación.
🔧 ui-redesign Rediseño visual UI/UX Pro Max: tokens energy/success en tailwind.config.js, Barlow Condensed añadido, badge-active→verde semántico, badge-expiring→naranja, scrollbar refinada, .card con hover transition-all, barras de progreso h-1→h-2, sidebar activo con gradiente from-brand-500/20, indicador lateral h-4→h-5, hover en filas de renovaciones Dashboard.
🔧 valera-a-mensual Cambio de valera a plan mensual con advertencia: GET /members/{id}/active-voucher-warning retorna info de valera activa (plan, restantes, vence). create_membership y renew_membership aceptan force=True para desactivar valera atómicamente al cambiar a plan no-voucher. Frontend (Members.tsx) muestra banner naranja con datos de la valera y botón "Confirmar cambio" antes de proceder; cancelar descarta la acción. Sin cambios de esquema de BD.
🔧 valeras-faseC Frontend asistencia/valeras: tipos CheckInResult y VoucherStatus (types/index.ts); api checkInAttendance (POST /attendance/check-in) y getVoucherStatus (GET /attendance/voucher-status/{document}). Nueva página pages/Attendance.tsx (input cédula, botón registrar ingreso + consultar valera, banner éxito/error con detail verbatim, visualización totales/consumidos/restantes/vencimiento/estado derivado vigente·agotada·vencida solo voucher). Navegación: ruta /attendance + acceso en App.tsx (sidebar real) y Navbar.tsx. Sin tocar backend salvo consumo de endpoints existentes; dashboard, pagos y current-membership sin cambios.

## Endpoints activos

### Members
GET/POST /api/members | GET/PUT/DELETE /api/members/{id}

### Membresías
POST /api/members/{id}/memberships | GET /api/members/{id}/memberships
GET /api/members/{id}/current-membership | POST /api/members/memberships/{id}/renew
PATCH /api/members/memberships/{id}/active (activar/desactivar manual)
GET /api/members/{id}/active-voucher-warning

### Pagos
POST/GET /api/members/{id}/payments
GET /api/payments (paginado + member_name) | DELETE /api/payments/{id}
GET /api/payments/statistics | GET /api/payments/statistics/current-month
GET /api/payments/method/{method} | GET /api/payments/monthly/{year}/{month}

### Asistencia (valeras)
POST /api/attendance/check-in (por cédula) | GET /api/attendance/voucher-status/{document}

### Otros
GET /api/plans | GET /api/dashboard
GET /api/members/{id}/measurements | PUT /api/members/{id}/measurements

## Archivos clave
| Archivo | Última modificación |
|---|---|
| schemas/body_measurement.py | fix7 — field_validator empty_str→None |
| repositories/payment_repository.py | fix3 — get_all_with_member() JOIN |
| api/routes/plans.py | fix1 — creado |
| api/routes/body_measurements.py | fix4 — creado |
| components/MemberInfo.tsx | fix7 — datos + medidas, validación; notificaciones-fase1 — campo email |
| pages/Members.tsx | fix8 — deleteMember(id, true) hard delete; notificaciones-fase1 — campo email en MemberForm |
| repositories/dashboard_repository.py | fix9 — get_memberships_by_status() por cliente vía end_date |
| pages/Payments.tsx | fix3 — member_name |
| types/index.ts | fix6 — BodyMeasurementUpsert separado; notificaciones-fase1 — email en Member/MemberCreate |
| models/member.py | notificaciones-fase1 — columna email |
| models/membership.py | notificaciones-fase1 — columna last_notified_at |
| schemas/member.py | notificaciones-fase1 — EmailStr + _MemberValidators mixin + normalize_email |
| schemas/membership.py | notificaciones-fase1 — last_notified_at en MembershipRead (campo interno) |
| database/init_db.py | notificaciones-fase1 — migraciones idempotentes email y last_notified_at |
| api/routes/members.py | notificaciones-fase1 — docstrings POST y PUT actualizados con contrato email |
| utils/validators.ts | notificaciones-fase1 — creado: onlyLetters, onlyDigits, isValidEmail centralizados |

🔧 freeze-pause Congelar/pausar membresías: columnas frozen_at, frozen_days_remaining, freeze_count (migraciones idempotentes). POST /api/members/memberships/{id}/freeze|unfreeze. Límite MAX_FREEZE_CYCLES=3 por membresía (FreezeLimitReachedError→400). Cálculo correcto: new_end_date = end_date + (now - frozen_at) sin pérdida de días por división entera. Dashboard KPI: bucket frozen separado (is_active=False AND frozen_at IS NOT NULL). Frontend: botones Congelar/Reactivar condicionales según estado en Members.tsx.
🔧 tienda-fase-a Módulo Tienda Fase A: categorías, productos, inventario, ventas de contado. 4 modelos nuevos (product_categories, products, inventory_movements, sales/sale_items). Venta atómica: valida stock de todos los items → crea venta → descuenta stock + registra movimientos → commit único (InsufficientStockError→409). Anulación repone stock. 3 servicios, 3 repositorios, 3 schemas, router /api/store/* (26 endpoints). Frontend: página /tienda con tabs Productos/Ventas/Categorías, carrito de venta, modal inventario/movimientos.

## Endpoints activos

### Store (Tienda — Fase A)
GET/POST /api/store/categories | PATCH /api/store/categories/{id}/active | DELETE /api/store/categories/{id}
GET/POST /api/store/products | GET/PUT /api/store/products/{id} | PATCH /api/store/products/{id}/active | DELETE /api/store/products/{id}
POST /api/store/products/{id}/inventory/entry | POST /api/store/products/{id}/inventory/adjustment
GET /api/store/products/{id}/inventory/movements | GET /api/store/inventory/low-stock
POST/GET /api/store/sales | GET /api/store/sales/{id} | POST /api/store/sales/{id}/cancel

🔧 tienda-fixes Correcciones módulo Tienda: (1) eliminación de productos con cascade (sale_items → ventas vacías → movimientos → producto); (2) eliminación individual + bulk-delete con checkboxes; (3) edición de categorías inline; (4) campo "Stock actual" editable en formulario de edición (genera ajuste automático si cambia); (5) inputs numéricos muestran vacío en lugar de 0; (6) campo cantidad en Ajuste acepta negativos correctamente (string→int en submit); (7) HTTP 204 sin body ya no lanza error de JSON; (8) productos recién creados disponibles en carrito de ventas (onUpdated propagado al padre); (9) explicación de "stock mínimo" visible en formulario. POST /api/store/products/bulk-delete añadido.

## Endpoints activos

### Store (Tienda — correcciones)
POST /api/store/products/bulk-delete — elimina múltiples productos con cascade

### Store (Tienda — Fase B)
GET/POST /api/store/customers | GET/PUT /api/store/customers/{id} | POST /api/store/customers/from-member/{id}
POST/GET /api/store/sales/{id}/payments | GET /api/store/cartera

🔧 tienda-fase-b Ventas a crédito (cartera) y clientes vinculados: entidad Customer independiente de Member (vinculable opcionalmente con FK unique). Estados de venta PAID/PARTIAL/PENDING/CANCELLED como Column(String) + Pydantic Literal. PaymentType cash/credit. CreditPayment (abonos) inmutables. Migración idempotente: sales.customer_id, sales.payment_type, status completed→PAID / cancelled→CANCELLED, member_id histórico→customer_id vía raw SQL. Deduplicación por document en CustomerService (no restricción DB, SQLite permite NULL múltiple). KPIs de cartera solo en módulo Tienda (Fase C para Dashboard). 5 nuevos archivos backend + 2 nuevos schemas; Store.tsx extendido con tabs Cartera y Clientes, CustomerPicker con búsqueda debounced + QuickCustomerModal, AbonoModal, StatusBadge.

🔧 alertas-membresias Panel de alertas de membresías en Dashboard: chips ejecutivos (vencidas/hoy/3 días/7 días) + lista filtrable por tab. Clasificación centralizada en backend; frontend solo renderiza. Filtra valeras (plan_type != 'voucher'). Unicidad por cliente: membresía con end_date más lejano (orden end_date DESC, no start_date DESC, para evitar falsos positivos cuando un miembro tiene varias membresías en la misma fecha de inicio). Máx. 50 por grupo, ASC por end_date. Extiende DashboardKPI con alerts?: AlertsSummary (4 listas + 4 conteos, campo opcional — retrocompatible). TD-04 ampliado con impacto en alertas.

🔧 fixes-post-tienda-b Correcciones post-lanzamiento: (1) AbonoModal step="any" (validación nativa browser); (2) eliminación de cliente con cascade de ventas CANCELLED; (3) purga de ventas CANCELLED huérfanas (customer_id NULL o FK rota) en startup + botón manual; (4) UNIQUE constraint `attendances` migrada de `(member_id, check_in_date)` a `(membership_id, check_in_date)` — elimina Internal Server Error al registrar asistencia en valera nueva cuando el mismo miembro tenía asistencia previa en valera antigua el mismo día.

### Endpoints nuevos (fixes-post-tienda-b)
DELETE /api/store/customers/{id} | POST /api/store/sales/purge-orphaned

🔧 td-01-exhausted-voucher-status Estado `exhausted` para valeras agotadas: `_enrich_membership` sobreescribe status cuando `COUNT(attendances) >= entries_total` y la valera está dentro de fecha. Dashboard: subquery correlacionada en `get_memberships_by_status` + bucket `exhausted` en `MembershipStatusSummary` + StatCard "Valeras agotadas". Badge frontend con token `energy`. Sin cambios en `_calculate_status`, check-in, pagos ni alertas.
🔧 td-02-deactivate-duplicate-vouchers Corrección histórica en startup: `_deactivate_duplicate_active_vouchers()` en `init_db.py` detecta clientes con más de una valera `is_active=True` y desactiva las sobrantes (conserva la más reciente por `start_date DESC, id DESC`). Idempotente. TD-10 resuelto por transitividad (TD-05 + TD-02). Sin cambios en runtime, servicios ni frontend.
🔧 fix-get-active-membership-tiebreak `get_active_membership` en `membership_repository.py` cambia `ORDER BY start_date DESC` a `ORDER BY start_date DESC, id DESC`. Corrige bug donde al renovar una valera el mismo día, la membresía inactiva (old, menor id) se devolvía como "actual" por orden arbitrario de SQLite, mostrando "Inactivo" en UI y bloqueando una nueva renovación con `ActiveVoucherExistsError` falso positivo. Cambio mínimo: 1 línea.
🔧 td-05-deactivate-on-renew `renew_membership` desactiva atómicamente la membresía anterior (`is_active=False`) antes del commit de la nueva. Nuevo método `deactivate_no_commit` en repositorio (flush sin commit). El commit único de `create()` cubre ambas operaciones. Sin cambios en `create_membership`, dashboard, pagos ni frontend.

🔧 tienda-fase-c Reportes operativos Tienda: endpoint único GET /api/store/reports?date_from&date_to. Tres bloques: (A) Ventas — KPIs período (total, ingresos, ticket promedio, abonos cobrados, contado/crédito) + top 5 productos por SQL (GROUP BY/SUM/LIMIT); (B) Cartera — estado actual (saldo, clientes con deuda, pendientes, parciales, deuda más antigua); (C) Inventario — bajo stock actual (hasta 10 productos). Filtro de período solo afecta ventas y top_products; cartera e inventario siempre actuales. Ventas CANCELLED excluidas de todos los KPIs. 3 métodos nuevos en sale_repository, 1 en product_repository, get_store_report en SaleService. Frontend: componente ReportsTab aislado con selector de período (Hoy/Esta semana/Este mes/Personalizado) y StatCards. Tab Reportes añadida a Store.tsx.

### Endpoints nuevos (tienda-fase-c)
GET /api/store/reports — KPIs ventas + cartera + inventario bajo stock

🔧 dashboard-fase-b KPIs de Tienda integrados en Dashboard ejecutivo: `membership_revenue`, `store_revenue` (contado + abonos cobrados del mes), `total_revenue`, `store_sales_count`, `cartera_balance` como campos opcionales en `DashboardKPI`. `AlertsSummary` extendida con `top_debtors` (top 5 por saldo DESC, con `days_overdue` y `oldest_sale_date`) y `low_stock_items` (top 5 productos bajo stock). Panel "Alertas operativas" con 6 tabs: Vencidas/Hoy/3días/7días/Cartera/Bajo stock. Secciones "Ingresos del mes" y "Tienda" en Dashboard.tsx condicionales si el backend envía los nuevos campos. `monthly_revenue` conservado sin cambios. Cálculos financieros reutilizan `get_sales_kpis`, `get_credit_collections`, `get_cartera_kpis` de `SaleRepository`. Nuevo método `get_top_debtors(limit)` en `SaleRepository`. Sin nuevos endpoints ni tablas.

🔧 resumen-control-membresias Resumen y control de membresías en Dashboard.

**Tabla "Membresías por plan"** — nueva sección entre las StatCards y el panel de alertas. Muestra una fila por cada plan activo con columnas: Plan | Activos | Agotados | Vencidos | Congelados | Total. Ordenada por Total DESC. Dinámica: planes nuevos aparecen automáticamente sin cambios de código. La columna Agotados solo muestra valores para `plan_type='voucher'`; planes mensuales muestran `—`.

**Regla de clasificación — Membresías por plan (unidad: membresía individual, sin dedup global):**
- **Activos:** `is_active=True`, `end_date >= hoy`, no agotadas.
- **Agotados:** `plan_type='voucher'`, `is_active=True`, `end_date >= hoy`, `COUNT(attendances) >= entries_total`.
- **Vencidos:** `is_active=True`, `end_date < hoy`. Aplica a todos los tipos de plan.
- **Congelados:** `is_active=False`, `frozen_at IS NOT NULL`.
- Sin deduplicación global: un cliente con mensual + Plan Día contribuye a ambas filas de plan.

**Regla de clasificación — StatCards (unidad: cliente, Best State Wins):**
`active(5) > expiring(4) > exhausted(3) > frozen(2) > expired(1)`. Un cliente con membresía mensual activa + Plan Día vencido cuenta como `active`.

**Regla de clasificación — Alertas operativas (unidad: cliente, Best State Wins con supresión):**
- Si el cliente tiene ANY membresía con `diff > 5 días` (`state='active'`) → suprimido de TODOS los buckets.
- Si `best_state='expired'` → aparece en Vencidas con la membresía más recientemente vencida.
- Si `best_state='expiring'` → aparece en Hoy/3días/7días con la membresía que vence más pronto.
- `best_state='exhausted'` o `'frozen'` → suprimido (cubiertos por StatCards propias).
- Todos los tipos de plan incluidos (monthly, daily, voucher vencida por fecha).

**Panel "Alertas operativas" extendido:**
- `MembershipAlert` gana `document` (cédula, opcional) y `days_overdue: int = 0` (calculado para bucket `expired` como `abs(today - end_date)`).
- Tab **Vencidas**: ordenada DESC por `end_date`. Sub-texto muestra plan, cédula y días vencidos.
- Tab **Vencidas**: filtros rápidos de antigüedad (pills): `Todos` / `1-7 días` / `8-30 días` / `+30 días`. Filtro sobre `days_overdue`. Solo visibles en tab Vencidas.
- Todos los tabs de membresías (Vencidas / Hoy / 3 días / 7 días): input de búsqueda por nombre o documento, filtrado local. No aplica a tabs Cartera y Bajo stock.
- Búsqueda y filtro de antigüedad se aplican en **AND**. Se resetean al cambiar de tab.

**Sin nuevos endpoints ni tablas.** `GET /api/dashboard` extiende su response con `members_by_plan: List[MembersByPlan]` (campo opcional, retrocompatible, default `[]`). Nuevos métodos `get_members_by_plan()` y `get_membership_alerts()` (reescrito) en `DashboardRepository`.

🔧 fix-dashboard-expiring Dashboard mostraba solo 1 cliente en "Por vencer" y alertas operativas. Causa: membresías no-voucher con `is_active=True` históricamente duplicadas (antes del fix TD-05) activaban la regla de supresión Best State Wins, clasificando al cliente como "active" en lugar de "expiring". Fix completo en tres partes: (1) `_deactivate_duplicate_active_non_voucher_memberships()` en `init_db.py` para limpiar datos históricos; (2) `create_membership` ahora desactiva atómicamente la membresía no-voucher activa anterior antes de crear la nueva (mismo patrón que `renew_membership`); (3) `set_membership_active(True)` bloquea con HTTP 400 si ya existe otra membresía no-voucher activa para el mismo cliente. Nuevo método `get_active_non_voucher_membership(member_id, exclude_id)` en `MembershipRepository`.

🔧 notificaciones-fase1 **Data Layer — Notificaciones de vencimiento (Fase 1 de 3).**
Prepara el sistema para notificar automáticamente a clientes con membresías próximas a vencer.
Esta fase establece únicamente la capa de datos; el envío de correos se implementa en Fases 2 y 3.

**Cambios de sistema:**
- `Member` ahora es un contacto completo: nombre, teléfono, documento, **email**, notas.
- `Membership` registra el estado de notificación internamente (`last_notified_at`) sin exponerlo al operador.

**Contrato de API — `Member.email`:**
- `email: "correo@ejemplo.com"` → strip → validar (EmailStr RFC) → guardar
- `email: null` o `email: ""` → sets NULL en BD (borrado explícito)
- `email` omitido → BD intacta (no change)
- Backend es fuente de verdad; frontend normaliza como cortesía.

**Contrato de campo `Membership.last_notified_at`:**
- Ownership exclusivo del job de notificaciones (Fase 2). Nunca escrito por servicios de membresía, rutas ni frontend.
- Expuesto en `MembershipRead` como campo de solo lectura en Fase 1.
- `NULL` = nunca notificado (estado inicial de todos los registros).

**Implementación técnica:** migración idempotente `_add_column_if_missing` para ambas columnas. `pydantic[email]` + `EmailStr`. `_MemberValidators` mixin con `check_fields=False` elimina duplicación de validators. `frontend/src/utils/validators.ts` centraliza `onlyLetters`, `onlyDigits`, `isValidEmail`.

**Deuda técnica pendiente:** TD-25 (Baja) — borrado de email desde UI no alcanzable por normalización del frontend.

🔧 portabilidad-docker Capa de portabilidad Docker: sistema ejecutable en cualquier máquina con `docker compose up`. Backend FastAPI en contenedor `python:3.11-slim`; frontend build estático servido por Nginx (`nginx:alpine`, multi-stage). SQLite persistida en volumen Docker (`db-data:/app/data`). `VITE_API_URL` inyectada en build time (embebida en el JS estático); fallback a `'/api'` para desarrollo local sin Docker. `.env.example` documenta todas las variables. Placeholder `scheduler` comentado en compose para Fase 2. Sin cambios en lógica de negocio, servicios ni componentes UI.

### Archivos nuevos (portabilidad-docker)
| Archivo | Descripción |
|---|---|
| `docker-compose.yml` | Orquestación: backend + frontend + volumen db-data |
| `backend/Dockerfile` | Imagen python:3.11-slim + uvicorn |
| `backend/.dockerignore` | Excluye __pycache__, *.db, .env |
| `frontend/Dockerfile` | Multi-stage: node:20-alpine (build) → nginx:alpine (serve) |
| `frontend/nginx.conf` | SPA fallback + cache headers |
| `frontend/.dockerignore` | Excluye node_modules, dist |
| `frontend/src/vite-env.d.ts` | Tipos de ImportMeta.env para TypeScript |

### Archivos modificados (portabilidad-docker)
| Archivo | Cambio |
|---|---|
| `.env.example` | Todas las variables: DATABASE_URL, CORS_ORIGINS, VITE_API_URL |
| `.gitignore` | Añadido .env, frontend/dist/, frontend/node_modules/ |
| `frontend/src/services/api.ts` | `BASE = import.meta.env.VITE_API_URL \|\| '/api'` |

### Validación (portabilidad-docker)
43/43 pruebas PASS. `docker compose config`, `build`, `up -d`, healthcheck, smoke tests de endpoints, React Router sin 404 de Nginx, persistencia SQLite tras `down/up` — todos verificados. Desarrollo local sin Docker sin regresiones (fallback `'/api'` confirmado en bundle).

### Deuda técnica (portabilidad-docker)
- TD-26 (Media): backup automático de volumen SQLite no implementado. Procedimiento manual documentado en `README.md`. Pendiente automatización con cron en host antes de despliegue en producción real.

🔧 fix-vite-api-url Bug: frontend no cargaba datos en Docker — `VITE_API_URL=http://localhost:8000` reemplazaba `/api` en lugar de precederlo, resultando en `GET /members` (404) en vez de `GET /api/members` (200). Fix: `BASE = (VITE_API_URL || '') + '/api'` — el origen del servidor y el prefijo `/api` son responsabilidades separadas. Desarrollo local sin Docker sin regresión (`'' + '/api'` = `'/api'`). `.env.example` actualizado con advertencia: `VITE_API_URL` no debe incluir `/api`.

| Archivo | Cambio |
|---|---|
| `frontend/src/services/api.ts` | `BASE = (VITE_API_URL \|\| '') + '/api'` |
| `.env.example` | Advertencia: sin `/api` al final de VITE_API_URL |

## Próximo paso
Notificaciones Fase 2: APScheduler + job diario de evaluación de vencimientos (sin integración externa)
Tienda Fase D: exportación de reportes o mejoras operativas
