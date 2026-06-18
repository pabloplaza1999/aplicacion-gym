# FEATURE_SUMMARY.md

## Estado
✅ Sprint 1-7 completos (backend + frontend)
🔧 migracion-inicial 50 clientes migrados desde Excel (CLIENTES.xlsm) vía API REST. Cada cliente incluye: member, membresía con plan correcto (start=vencimiento−30d, end=fecha Excel), pago en efectivo al precio del plan. Teléfonos faltantes con placeholder 0000000 para ajuste posterior desde la app. semipersonalizado → Funcional y Musculación.
🔧 fix-fecha-vencimiento-tz Corrección de desfase de un día (y crash del Dashboard) al mostrar fechas. Causa: el frontend trataba fechas de negocio (start/end_date, naive UTC) como timestamps y al convertir a Bogotá restaba un día; además /dashboard devuelve end_date como solo-fecha ("2026-07-20") y appendear -05:00 producía fecha inválida → RangeError → pantalla negra. Solución (utils/validators.ts): nueva helper normalizeDateStr (maneja date-only y datetime naive, agrega T00:00:00 si falta hora y offset -05:00; respeta strings con TZ) usada por fmtBogotaDate; guarda isNaN para no tumbar la SPA ante fecha malformada. normalizeUtcStr intacto para timestamps reales (check_in_at). Attendance.tsx: fmtDate→normalizeDateStr, fmtDateTime→normalizeUtcStr. Sin cambios de backend, esquema ni datos. Build Docker requiere builder prune previo (ver TD-47).
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

🔧 fix-duplicate-document `IntegrityError` (UNIQUE `members.document`) no manejada retornaba HTTP 500 sin headers CORS → browser mostraba "Failed to fetch". Fix: pre-check en `MemberService.create_member` usando `get_by_document()` antes del INSERT → lanza `DuplicateDocumentError` → ruta retorna HTTP 409 con mensaje "Ya existe un cliente con ese número de documento." Sin dependencia de texto del motor SQLite.

🔧 fix-email-create Bug: `email` no se persistía al crear cliente desde la UI. Causa: `MemberService.create_member` y `MemberRepository.create` omitían el campo `email`. Fix mínimo en 2 archivos; `update_member` sin cambios (ya usaba `model_dump(exclude_unset=True)`). El flujo de Notificaciones Fase 2 ahora puede leer emails de clientes creados desde la UI.

🔧 migracion-correctiva-plan-dia Corrección histórica de 6 membresías Plan Día creadas con la lógica UTC antigua. Backup manual previo (`gym_2026-06-12_14-13.db`). IDs afectados: 2, 3, 4, 5, 6, 7. La membresía ID=6 (rhino gym) estaba activa incorrectamente — pasó a `expired` tras la corrección. Los 5 restantes eran inactivos (corrección cosmética de fecha de vencimiento). Migración atómica con assert de exactamente 6 filas; 10 registros restantes sin tocar. Verificado vía API: ID=6 muestra `status=expired`, Dashboard refleja bucket `expired` correctamente.

🔧 fix-plan-dia-timezone Plan Día vencía a las 23:59:59 UTC (18:59:59 Bogotá) en lugar de al final del día local. Membresías creadas después de las 19:00 Bogotá mostraban fecha de inicio incorrecta (día UTC siguiente) y aparecían como expiradas antes de medianoche local. **Fix funcional:** `_calculate_end_date` convierte `start_date` UTC a hora Bogotá (UTC-5), calcula 23:59:59 local y convierte de vuelta a UTC. Centralizado en `BOGOTA_OFFSET = timedelta(hours=-5)` en `config.py`. **Fix de visualización:** `fmtBogotaDate(utcStr)` en `validators.ts` + `normalizeUtcStr` como helper compartido; reemplaza todos los `slice(0,10)` sobre fechas de membresía en `Members.tsx`; `Dashboard.tsx` usa `fmtBogotaDate` en alertas y renovaciones recientes; `Attendance.tsx` usa `timeZone: 'America/Bogota'` explícito en `fmtDate`/`fmtDateTime`. **Fix alertas:** `get_membership_alerts` en `dashboard_repository.py` compara contra fecha Bogotá local (`datetime.utcnow() + BOGOTA_OFFSET`). TD-04 reclasificado de Baja a Media (parcialmente resuelto — Plan Día y alertas corregidos; restricción `check_in_date` por día local pendiente).

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

🔧 backup-td26 Backups automáticos de la base de datos: servicio `scheduler` en Docker Compose ejecuta backup diario a las 02:00 AM (America/Bogota) usando `sqlite3.backup()` (hot backup nativo). Backup manual disponible desde el Dashboard. Retención diferenciada: `backups/automatic/` máx. 30 archivos, `backups/manual/` máx. 10 archivos — pools independientes. Panel de estado en Dashboard (indicador verde/naranja/rojo + botón "Ver respaldos"). Modal administrativo con lista por tipo y botón de backup manual. `GET /api/backup/status`, `GET /api/backup/list`, `POST /api/backup/manual`. TD-26 resuelto.

### Endpoints nuevos (backup-td26)
GET /api/backup/status — resumen para Dashboard (último automático + indicador antigüedad)
GET /api/backup/list — lista completa agrupada por tipo para modal
POST /api/backup/manual — crea backup manual inmediato

### Archivos nuevos (backup-td26)
| Archivo | Descripción |
|---|---|
| `backend/app/schemas/backup.py` | BackupFile, BackupListResponse, BackupStatus |
| `backend/app/services/backup_service.py` | Lógica de backup, retención y listado |
| `backend/app/api/routes/backup.py` | Router con 3 endpoints |
| `backend/scheduler/__init__.py` | Módulo scheduler |
| `backend/scheduler/main.py` | APScheduler cron 02:00 AM + backup al arrancar |
| `frontend/src/components/BackupModal.tsx` | Modal con lista por tipo y backup manual |

### Archivos modificados (backup-td26)
| Archivo | Cambio |
|---|---|
| `backend/app/core/config.py` | db_path, backup_dir, max_auto_backups, max_manual_backups |
| `backend/app/main.py` | Registrar backup.router |
| `backend/requirements.txt` | apscheduler==3.10.4 |
| `docker-compose.yml` | Servicio scheduler activo con volumen db-data |
| `frontend/src/types/index.ts` | BackupFile, BackupListResponse, BackupStatus |
| `frontend/src/services/api.ts` | getBackupStatus(), listBackups(), createManualBackup() |
| `frontend/src/pages/Dashboard.tsx` | Panel Respaldos + BackupModal |
| `docs/MANUAL_TECNICO.md` | Sección backup reescrita con nuevo flujo automático |

🔧 notificaciones-fase2 Job diario de notificaciones de vencimiento de membresías: evaluación automática a las 08:00 AM (America/Bogota) via APScheduler. Deduplicación por par `(membership_id, threshold_days)` — una sola query anti-N+1. Cifrado Fernet para `smtp_password` (SECRET_KEY en .env). Excluye: frozen, vouchers. Umbrales configurables (default: 7d, 3d, 1d, 0d). Historial paginado en `notification_logs`. Panel operativo en Dashboard (enviados/fallidos/sin-email hoy + botón "Ejecutar ahora"). Página `/configuracion` con formulario SMTP + umbrales + toggle habilitado. `NotificationHistoryModal` con paginación. Arquitectura desacoplada evaluador/canal — preparada para Fase 3 (WhatsApp/SMS).

### Endpoints nuevos (notificaciones-fase2)
GET /api/notifications/settings — configuración SMTP + umbrales
PUT /api/notifications/settings — guarda configuración
POST /api/notifications/test-smtp — envía correo de prueba
GET /api/notifications/status — estado operativo (enviados/fallidos/sin-email hoy)
GET /api/notifications/history — historial paginado (?page=1&page_size=20)
POST /api/notifications/run — ejecuta ciclo manualmente

### Archivos nuevos (notificaciones-fase2)
| Archivo | Descripción |
|---|---|
| `backend/app/models/notification.py` | NotificationLog + NotificationSettings |
| `backend/app/schemas/notification.py` | Pydantic schemas |
| `backend/app/repositories/notification_repository.py` | CRUD + deduplicación + historial paginado |
| `backend/app/services/crypto_service.py` | encrypt/decrypt Fernet |
| `backend/app/services/email_service.py` | Adaptador SMTP (smtplib) |
| `backend/app/services/notification_service.py` | Evaluador + orquestador |
| `backend/app/api/routes/notifications.py` | Router con 6 endpoints |
| `frontend/src/pages/Settings.tsx` | Página /configuracion |
| `frontend/src/components/NotificationHistoryModal.tsx` | Modal historial paginado |

### Archivos modificados (notificaciones-fase2)
| Archivo | Cambio |
|---|---|
| `backend/requirements.txt` | cryptography==41.0.7 |
| `backend/app/core/config.py` | secret_key para Fernet |
| `backend/app/models/__init__.py` | Registrar modelos nuevos |
| `backend/app/database/init_db.py` | Importar modelos para create_all |
| `backend/app/main.py` | Registrar notifications.router |
| `backend/scheduler/main.py` | Job 08:00 AM + run_notification_job() |
| `frontend/src/types/index.ts` | NotificationSettings, NotificationLogRead, NotificationHistoryResponse, NotificationStatusPanel, NotificationRunResult |
| `frontend/src/services/api.ts` | 6 funciones de notificación |
| `frontend/src/pages/Dashboard.tsx` | Panel operativo Notificaciones |
| `frontend/src/App.tsx` | Ruta /configuracion + entrada sidebar |

🔧 f0-baseline-seguridad F0 — Línea base de seguridad: auditoría integral sin cambios de código. 20 hallazgos SEC-001→SEC-020 (OWASP API Top 10). Artefactos: `docs/BASELINE_SEGURIDAD.md` (hallazgos) y `docs/ROADMAP_COMERCIALIZACION.md` (fases F0-F9). Deuda técnica derivada: TD-34 a TD-44. Siguiente paso: Human Gate — revisar y aprobar hallazgos antes de F1.

🔧 f1-bloque-a-hardening **F1 — Endurecimiento del empaquetado (Bloque A).** Cinco hallazgos P0 del baseline, sin tocar lógica de negocio ni contratos de endpoints.
- **SEC-011** — `debug` default `False` en `config.py` (seguro por defecto; desarrollo activa `DEBUG=true` explícitamente).
- **SEC-009** — Validación de arranque centralizada en `Settings` (`model_validator`): en producción (`debug=False`) `SECRET_KEY` es obligatoria → aborta el arranque con mensaje accionable; en desarrollo se permite vacía con degradación (cifrado SMTP falla solo al usarse). Corre para API y scheduler (ambos importan `settings`). Cierra TD-30.
- **SEC-013** — Handler 422 en `main.py` sanitiza el log y la respuesta: conserva `loc`+`type`+`msg`, elimina `input`/`ctx` (PII: nombres, cédulas, emails). Nivel `warning`. Cierra TD-39.
- **SEC-007 + R1** — `backend/Dockerfile` crea usuario no-root `gymuser` (UID/GID 10001) + instala `gosu`. Nuevo `backend/docker-entrypoint.sh`: arranca como root, hace `chown -R` idempotente de `/app/data` y baja privilegios con `gosu`. Cubre backend y scheduler (misma imagen) y resuelve el caso upgrade sobre volumen existente con archivos root. Cierra TD-34.
- **SEC-005 + R3** — `docker-compose.yml` parametriza el bind: `${BIND_ADDR:-127.0.0.1}` en puertos `8000` y `80`. Default loopback (exposición mínima, PC única); multi-dispositivo LAN se configura por instalación (`BIND_ADDR` + `VITE_API_URL`). Sin hardcodear loopback. Residual sin auth → revisar en F2.
- **`.gitattributes`** nuevo: fuerza LF en `*.sh` (evita CRLF que rompería el shebang del entrypoint en Linux).

### Archivos (f1-bloque-a-hardening)
| Archivo | Cambio |
|---|---|
| `backend/app/core/config.py` | `debug` default `False` + `model_validator` SECRET_KEY obligatoria en prod |
| `backend/app/main.py` | Handler 422 sanitizado (sin `input`), nivel `warning` |
| `backend/Dockerfile` | Usuario no-root `gymuser` + `gosu` + ENTRYPOINT |
| `backend/docker-entrypoint.sh` | **Nuevo** — reconciliación idempotente de permisos + drop a no-root |
| `docker-compose.yml` | Bind parametrizado `${BIND_ADDR:-127.0.0.1}` (backend y frontend) |
| `.env.example` | `SECRET_KEY` obligatoria/única + `BIND_ADDR` documentados |
| `.gitattributes` | **Nuevo** — LF forzado en `*.sh` |

### Validación parcial (Paso 4)
- `config.py`/`main.py` parsean sin error. SEC-009/011 verificados en 3 escenarios: prod sin clave aborta (`ValidationError`); prod con clave arranca; dev sin clave arranca. `docker compose config` válido; bind resuelve a `127.0.0.1` por defecto. Entrypoint en LF.

### Estado final (Pasos 5–7)
**Estado técnico:** Implementado · Probado · Auditado · Aprobado. Sin defectos abiertos.
- Paso 5 (PASS con riesgos operativos): e2e en Docker. Usuario real del proceso = `gymuser`/10001 (`docker top` sobre uvicorn y scheduler). Instalación nueva (volumen fresco) y upgrade sobre volumen root-owned (permisos reconciliados `0:0`→`10001:10001`). Escritura `gym.db` (POST 201), backup manual y automático OK bajo no-root. Log 422 sin `input`/PII.
- Paso 5.5 (PASS — sin impacto histórico): sin cambios de esquema, migraciones, registros, contratos API ni backups existentes. El `chown` afecta solo ownership de filesystem, no el contenido de los datos.
- Paso 6 (auditoría APROBADA): implementación coincide con el diseño; sin regresiones; riesgos exclusivamente operativos/de despliegue.

**Estado de despliegue:** ⏳ Pendiente de rebuild + recreate en los entornos de producción actuales (los contenedores en marcha siguen en las imágenes previas — root, bind `0.0.0.0`). Es actividad operativa de release, no deuda técnica.

🔧 f1-bloque-b **F1 — Endurecimiento de seguridad en runtime (Bloque B).** Cuatro hallazgos de riesgo medio del baseline F0, sin tocar lógica de negocio ni contratos de endpoints. DEF-01 (`connect-src` bloqueando API) identificado durante Paso 5 y resuelto dentro del mismo ciclo.
- **SEC-010** — OpenAPI docs deshabilitados en producción: `FastAPI(docs_url=None, redoc_url=None, openapi_url=None)` cuando `settings.debug=False`. En desarrollo permanecen activos. Cierra TD-36.
- **SEC-012** — CORS explícito y mínimo: `allow_credentials=False`, métodos y headers listados explícitamente (`Content-Type` únicamente, verificado contra `api.ts`), orígenes tomados de `settings.cors_origins`. Cierra TD-38.
- **SEC-015** — Headers de seguridad HTTP en Nginx: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Content-Security-Policy` a nivel `server {}` con herencia correcta (cache vía `expires`, no `add_header`). CSP incluye `fonts.googleapis.com`/`gstatic.com` (Google Fonts) y `connect-src 'self' http://localhost:8000` (arquitectura single-PC). HSTS diferido a F5. Cierra TD-41.
- **SEC-017** — `str(e)` en `backup.py` y `notifications.py`: `except ValueError` → mensaje controlado al cliente; `except Exception` → HTTP 500 genérico + `logger.error(...)`. Detalle técnico preservado en logs del servidor. Cierra TD-43.

### Archivos (f1-bloque-b)
| Archivo | Cambio |
|---|---|
| `backend/app/main.py` | `FastAPI` condiciona docs a `debug`; `CORSMiddleware` explícito y mínimo |
| `frontend/nginx.conf` | 4 headers de seguridad + CSP; cache via `expires`; DEF-01 fix `connect-src` |
| `backend/app/api/routes/backup.py` | `logger` + `except ValueError`/`Exception` con mensajes controlados |
| `backend/app/api/routes/notifications.py` | `logger` + split `except ValueError`/`Exception` con mensajes controlados |

### Estado final (Pasos 5–7)
**Estado técnico:** Implementado · Probado · Auditado · Aprobado. DEF-01 resuelto. Sin defectos abiertos.
- Paso 5 (PASS): validación en Docker — headers confirmados vía `curl`; Dashboard carga con datos reales (`GET /api/dashboard 200`); DEF-01 detectado y corregido.
- Paso 5.5 (PASS — sin impacto histórico): cambios exclusivamente en capas de configuración e infraestructura. Sin tablas, migraciones ni lógica de datos afectada.
- Paso 6 (auditoría APROBADA con observaciones): configuración CSP/CORS consistente con despliegue real single-PC. Consideración de despliegue documentada para futura adopción LAN/Internet.

🔧 cliente-unico **Cliente Único — Fase 1 (backend).** Unifica las entidades `Customer` (tienda) y `Member` (gimnasio) en un único cliente canónico. `Sales.member_id` reemplaza `Sales.customer_id` como columna canónica. `/store/customers/*` redirige a `MemberService` (alias sin cambios de frontend). `SaleCreate.customer_id` se reutiliza semánticamente como `member_id` — cero cambios de frontend ni de contrato API. `_enrich_sale()` mapea `sale.member_id → SaleRead.customer_id` para retrocompatibilidad. `_migrate_historical_customer_ids()` eliminado del startup (creaba Customers desde Members, revirtiendo la migración). `_purge_orphaned_cancelled_sales()` actualizado para validar contra `members` y `customers` (modelo dual transitorio). `MemberService.hard_delete_member()` ahora bloquea si el cliente tiene ventas activas (PAID/PENDING/PARTIAL). Nuevo `DELETE /store/customers/{id}` bloquea además si el cliente tiene membresías del gimnasio. Tabla `customers` y servicio `CustomerService` se mantienen temporalmente (TD-48). Migración idempotente `_add_column_if_missing("sales", "member_id", ...)` + `_migrate_sales_to_member_id()` en startup. Frontend diferido a Fase 2.

### Archivos modificados (cliente-unico)
| Archivo | Cambio |
|---|---|
| `backend/app/models/sale.py` | Columna `member_id` FK→members añadida |
| `backend/app/database/init_db.py` | `_migrate_sales_to_member_id()` + `_purge_orphaned_cancelled_sales()` actualizado + `_migrate_historical_customer_ids()` eliminado del startup |
| `backend/app/repositories/sale_repository.py` | `member_id` canónico en todo el módulo; `get_member_name()`, `get_top_debtors()` con Member |
| `backend/app/services/sale_service.py` | `_enrich_sale` mapea `member_id→customer_id`; `CustomerRepository` eliminado |
| `backend/app/repositories/member_repository.py` | Nuevos: `has_active_sales()`, `get_debt_total()`, `search_for_store()`, `has_memberships()` |
| `backend/app/services/member_service.py` | `hard_delete_member()` con guard; `get_members_for_store()`, `delete_customer_from_store()` |
| `backend/app/api/routes/store.py` | `/customers/*` → alias MemberService con `_member_as_customer()` helper |
| `backend/app/api/routes/members.py` | `DELETE /{id}?hard=true` atrapa `ValueError` → HTTP 400 |

## Próximo paso

### Actividades operativas pendientes (no son deuda de código)
- **Deploy producción — Cliente Único Phase 1** (TD-51, Alta): ejecutar checklist Paso 5.5 sobre la instalación real del gimnasio antes de hacer `docker compose build backend`. Verificar V1–V4 sobre datos reales de `customers`, `sales` y `members`.

### Backlog funcional
- **F1 Bloque B:** ✅ Completado (2026-06-18). SEC-010/012/015/017 resueltos.
- **TD-35 (SEC-008):** Dependencias con CVEs — iniciativa separada, pendiente de aprobación.
- **F2 auth staff:** Siguiente fase principal.
- **Notificaciones Fase 3:** canales adicionales (WhatsApp/SMS) o plantillas personalizables.
- **Tienda Fase D:** exportación de reportes o mejoras operativas.
- **Cliente Único Phase 2:** actualizar frontend para usar `member_id` directamente; eliminar tabla `customers`, `CustomerService` y columna `sales.customer_id` (prerrequisito: mover `CreditPayment` a su propio módulo — TD-49).
