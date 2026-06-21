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
🔧 fix-cambiar-contrasena-voluntario Cambio voluntario de contraseña sin primer login: botón candado (🔒) en footer del sidebar (App.tsx) para admin y super_admin; navega a `/change-password`. Subtítulo de ChangePassword.tsx cambiado a texto genérico (era específico de primer acceso). Sin cambios de backend — `POST /api/auth/change-password` ya aceptaba tokens no temporales. Commit: 0df8307.
🔧 fix-cancelar-change-password Botón "Cancelar" en ChangePassword.tsx visible solo cuando `!isTemporary` (acceso voluntario). En primer acceso forzado el botón no aparece; en acceso voluntario desde sidebar vuelve a la pantalla anterior con `navigate(-1)`. `isTemporary` leído de `useAuth()` — sin cambios de backend ni de AuthContext.

## Endpoints activos

### Members
GET/POST /api/members | GET/PUT/DELETE /api/members/{id}

### Membresías
POST /api/members/{id}/memberships | GET /api/members/{id}/memberships
GET /api/members/{id}/current-membership | POST /api/members/memberships/{id}/renew
PATCH /api/members/memberships/{id}/active (activar/desactivar manual)
PATCH /api/members/memberships/{id}/start-date (corregir fecha inicio + auditoría)
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

🔧 fix-td46-calculate-status `_calculate_status` en `MembershipService` ahora usa `datetime.utcnow() + BOGOTA_OFFSET` (hora Bogotá local) en lugar de `datetime.utcnow()`. Corrige que membresías vigentes aparecieran como `expired` desde las 19:00 Bogotá del día anterior al vencimiento real (UTC medianoche = 19:00 Bogotá). `BOGOTA_OFFSET` ya estaba importado desde `app.core.config`. Cambio de 1 línea; sin impacto histórico, sin migraciones. Afecta todos los flujos que invocan `_calculate_status`: `_enrich_membership`, `get_active_membership`, `get_all_memberships`, `create_membership`, `renew_membership`, `set_membership_active`. TD-46 resuelto.

| Archivo | Cambio |
|---|---|
| `backend/app/services/membership_service.py` | línea 66: `today = datetime.utcnow() + BOGOTA_OFFSET` |

---

🔧 fix-tz-normalization Normalización completa del uso de hora Bogotá en el dominio de membresías y dashboard. Consolida TD-52, TD-53 y TD-54 en una única corrección de 5 líneas. Causa raíz: `datetime.utcnow()` usado para lógica de negocio que debe evaluarse con hora local (`datetime.utcnow() + BOGOTA_OFFSET`). Sin cambios arquitectónicos, sin migraciones, sin impacto histórico. `BOGOTA_OFFSET` ya importado en ambos archivos. Freeze/unfreeze mantienen UTC-vs-UTC intencionalmente (correcto). TD-52, TD-53 y TD-54 resueltos.

| Archivo | Cambio |
|---|---|
| `backend/app/repositories/dashboard_repository.py` | Línea 72 (`get_memberships_by_status`): `now = datetime.utcnow() + BOGOTA_OFFSET` |
| `backend/app/repositories/dashboard_repository.py` | Línea 144 (`get_members_by_plan`): `now = datetime.utcnow() + BOGOTA_OFFSET` |
| `backend/app/services/membership_service.py` | Línea 124 (`_enrich_membership`): `today = datetime.utcnow() + BOGOTA_OFFSET` |
| `backend/app/services/membership_service.py` | Línea 151 (`_has_active_valid_voucher`): `now = datetime.utcnow() + BOGOTA_OFFSET` |
| `backend/app/services/membership_service.py` | Línea 170 (`get_active_voucher_warning`): `now = datetime.utcnow() + BOGOTA_OFFSET` |

🔧 fix-normalize-date-str `normalizeDateStr()` en `validators.ts` interpretaba todos los naive datetimes como hora Bogotá (append `-05:00`), cuando los datetimes con componente de hora (`T`) son UTC naives devueltos por la API. Consecuencia: Plan Día `end_date = "2026-06-19T04:59:59"` (UTC) se mostraba como `19/06/2026` en lugar de `18/06/2026`. Fix: split en dos ramas — strings con `T` → append `Z` (UTC real); date-only → append `T00:00:00-05:00` (fecha Bogotá, sin cambio). Backend y BD correctos en todo momento. Cambio de 2 líneas; sin impacto histórico. Corrige también el display de membresías mensuales creadas después de las 19:00 Bogotá (mostraban día UTC+1 en lugar del día Bogotá correcto).

| Archivo | Cambio |
|---|---|
| `frontend/src/utils/validators.ts` | `normalizeDateStr`: rama `T` → append `Z`; date-only → append `T00:00:00-05:00` |

🔧 correct-start-date **Corrección de fecha de inicio de membresía.** Permite corregir la `start_date` de una membresía que fue registrada con fecha incorrecta o tardíamente, recalculando `end_date` de forma automática. Registra auditoría inmutable en tabla dedicada. Ciclo completo Paso 1→7. Estado técnico: **Implementado · Probado · Auditado · Aprobado** (Paso 5 PASS · Paso 5.5 PASS sin impacto histórico · Paso 6 auditoría Aprobada con observaciones).

**Reglas de negocio clave:**
- Solo membresías activas (`active`/`expiring`) o congeladas (`frozen`) son corregibles.
- Membresías vencidas, manualmente desactivadas o con asistencias registradas no son corregibles.
- `new_start_date` no puede ser futura.
- La corrección no puede producir `end_date` en el pasado ni solaparse con otra membresía activa del mismo cliente.
- Para membresías congeladas: `new_end_date` debe ser posterior a `frozen_at`; `frozen_days_remaining` se recalcula.
- Motivo obligatorio (mínimo 10 caracteres); múltiples correcciones permitidas (auditoría completa).

**Backend:** nueva tabla `membership_correction_logs` (auditoría inmutable). `MembershipCorrectionRepository.create()` + `get_latest_for_membership()`. `MembershipRepository.get_active_overlapping()` + `correct_start_date_no_commit()`. `MembershipService.correct_start_date()`. Atomicidad: flush auditoría → flush membresía → un único commit. `MembershipRead` expone `last_correction_at` y `last_correction_reason` (None para listados — sin N+1).

**Frontend:** `StartDateCorrectionModal` (fecha actual de referencia, date input con max = hoy en Bogotá, textarea motivo ≥10 chars). Botón "Corregir fecha de inicio" visible en tab Membresía cuando `status ∈ {active, expiring, frozen}`. `correctMembershipStartDate()` en `api.ts`.

### Endpoints nuevos (correct-start-date)
PATCH /api/members/memberships/{id}/start-date — corrige start_date; recalcula end_date y frozen_days_remaining; registra auditoría atómica

### Archivos nuevos (correct-start-date)
| Archivo | Descripción |
|---|---|
| `backend/app/models/membership_correction.py` | Modelo `MembershipCorrectionLog` |
| `backend/app/schemas/membership_correction.py` | `MembershipStartDateCorrectionCreate` (new_start_date, reason) |
| `backend/app/repositories/membership_correction_repository.py` | create + get_latest_for_membership |
| `frontend/src/components/StartDateCorrectionModal.tsx` | Modal de corrección con validación |

### Archivos modificados (correct-start-date)
| Archivo | Cambio |
|---|---|
| `backend/app/schemas/membership.py` | `MembershipRead` + `last_correction_at`, `last_correction_reason` |
| `backend/app/repositories/membership_repository.py` | `get_active_overlapping`, `correct_start_date_no_commit` |
| `backend/app/services/membership_service.py` | `MembershipCorrectionError`, `correct_start_date()`, `_enrich_membership` con auditoría |
| `backend/app/api/routes/memberships.py` | PATCH `/memberships/{id}/start-date` (antes del GET dinámico) |
| `backend/app/database/init_db.py` | Import `MembershipCorrectionLog` para `create_all` |
| `backend/app/models/__init__.py` | Export `MembershipCorrectionLog` |
| `frontend/src/types/index.ts` | `Membership` + `last_correction_at/reason`; `MembershipStartDateCorrectionCreate` |
| `frontend/src/services/api.ts` | `correctMembershipStartDate()` |
| `frontend/src/pages/Members.tsx` | Import modal, estado `showCorrectionModal`, botón condicional, render modal |

**Deuda técnica generada:** TD-55 (`corrected_by` diferido a F2), TD-56 (GET historial de correcciones diferido), TD-57 (índice compuesto `(membership_id, corrected_at)` en `membership_correction_logs` diferido).

🔧 f2-auth-staff **F2 — Autenticación JWT para el operador del gimnasio.** Un único usuario admin, JWT stateless, sin roles múltiples. Diseñado para uso local por un solo operador.

**Decisiones de arquitectura:**
- `JWT_SECRET_KEY` independiente de `SECRET_KEY` (Fernet/SMTP) — ciclos de rotación distintos.
- Token almacenado en `localStorage` (justificación: CORS `allow_credentials=False` de F1 Bloque B hace inviable httpOnly cookie sin revertir hardening).
- Dos dependencias FastAPI: `get_current_user` (permite `is_temporary`) y `require_active_user` (bloquea `is_temporary` → 403). Cero cambios en los 11 routers existentes.
- Protección global en `main.py` via `_protected = {"dependencies": [Depends(require_active_user)]}` aplicado a cada `include_router`.
- Contraseña inicial via `ADMIN_INITIAL_PASSWORD` env var (no hardcodeada en logs).
- Reset admin: `UPDATE` sobre usuario existente (A1 — no DELETE+seed), via `scripts/reset_admin.py`.
- `change-password` devuelve `TokenResponse` fresco (`is_temporary=False`) — sin re-login.
- `bcrypt==4.0.1` anclado explícitamente en `requirements.txt` (passlib 1.7.4 incompatible con bcrypt 5.x).

**Flujos cubiertos:**
1. Login → recibe token JWT con `is_temporary`. Si temporal: redirige a `/change-password` bloqueando todo acceso al resto de la app. Si no temporal: accede normalmente.
2. Cambio de contraseña en primer login → recibe token fresco con `is_temporary=False` → sin re-login.
3. Sesión expirada (401 en cualquier ruta) → redirige a `/login?expired=1` con banner informativo.
4. Logout → limpia `localStorage` → redirige a `/login`.

**Excepciones de protección de rutas:**
- Públicas: `POST /api/auth/login`, `GET /api/health`, `GET /`.
- Token válido (permite `is_temporary`): `POST /api/auth/change-password`.
- Token válido + no temporal: todos los demás endpoints.

**Validación producción extendida:** `model_validator` en `config.py` valida `JWT_SECRET_KEY` (no vacía, no igual al default dev) y `ADMIN_INITIAL_PASSWORD` (no vacía) cuando `DEBUG=False`.

**Entorno oficial de despliegue:** Docker Compose. Las validaciones finales de F2 se ejecutaron sobre el stack Docker (`docker compose up --build`). El modo `INICIAR.bat` / uvicorn+npm solo es válido para desarrollo y depuración local.

---

### Procedimiento de primer acceso (f2-auth-staff)

1. Asegurarse de que `.env` contenga `ADMIN_INITIAL_PASSWORD` (contraseña inicial del operador).
2. Levantar el stack: `docker compose up --build -d`.
3. Abrir `http://localhost` en el navegador.
4. Iniciar sesión con usuario `admin` y la contraseña definida en `ADMIN_INITIAL_PASSWORD`.
5. El sistema redirige automáticamente a `/change-password` — el acceso al resto de la app está bloqueado hasta completar el cambio.
6. Ingresar y confirmar la nueva contraseña definitiva (mínimo 8 caracteres).
7. El sistema genera un nuevo token con `is_temporary=False` y redirige al Dashboard.

**Nota:** `ADMIN_INITIAL_PASSWORD` solo se usa en el seed del primer arranque y en `reset_admin.py`. Cambiarla en `.env` después del primer login **no afecta** la contraseña activa en la DB. Para resetear la contraseña, usar `scripts/reset_admin.py`.

---

### Reset de contraseña de emergencia (reset_admin.py)

Si el operador pierde acceso o necesita restablecer la contraseña:

```bash
# Dentro del contenedor backend:
docker exec -it aplicacion-gym-backend-1 python scripts/reset_admin.py

# O en entorno local con virtualenv activo:
cd backend && python scripts/reset_admin.py
```

El script:
- Actualiza `hashed_password` al valor hash de `ADMIN_INITIAL_PASSWORD` en `.env`.
- Establece `is_temporary=True` — el operador debe cambiar la contraseña en el siguiente login.
- Nunca elimina ni recrea el usuario (usa `UPDATE`, no `DELETE+INSERT`).

---

### Checklist de actualización para instalaciones existentes (TD-60)

Al actualizar una instalación que no tenía F2 a una versión con F2:

1. **Antes de reiniciar el backend**, agregar al `.env` raíz:
   ```
   JWT_SECRET_KEY=<generar con: python -c "import secrets; print(secrets.token_hex(32))">
   ADMIN_INITIAL_PASSWORD=<contraseña inicial segura>
   ```
2. Reconstruir imágenes: `docker compose up --build -d`.
3. Al primer acceso, el sistema presentará la pantalla de login (nuevo comportamiento).
4. Iniciar sesión con `admin` / `ADMIN_INITIAL_PASSWORD` y cambiar la contraseña.

**Si no se completan los pasos 1 antes del reinicio:** el backend no arrancará con `DEBUG=false` — mensaje de error explícito indica las variables faltantes. Agregar las variables y reiniciar.

---

### Explicación de ADMIN_INITIAL_PASSWORD (TD-59)

`ADMIN_INITIAL_PASSWORD` tiene dos usos exclusivos:

| Cuándo se usa | Descripción |
|---|---|
| Seed inicial (`init_db`) | Primer arranque sin usuario admin → crea `admin_users` con esta contraseña y `is_temporary=True` |
| Reset manual (`reset_admin.py`) | Restablece la contraseña del admin existente a esta contraseña con `is_temporary=True` |

**No se usa en runtime**: la contraseña activa del operador vive en `admin_users.hashed_password` (DB). Cambiar `ADMIN_INITIAL_PASSWORD` en `.env` después del primer login no tiene ningún efecto hasta la próxima ejecución de `reset_admin.py`.

---

**Deuda técnica generada:** TD-58 (pin `bcrypt==4.0.1`), TD-59 (`ADMIN_INITIAL_PASSWORD` no cambia contraseña activa), TD-60 (arranque bloqueado en actualización sin `.env` actualizado), TD-55 (`corrected_by` ahora accionable con F2 implementado).

### Endpoints nuevos (f2-auth-staff)
POST /api/auth/login — recibe `{username, password}`, retorna `TokenResponse` (access_token, token_type, is_temporary)
POST /api/auth/change-password — requiere Bearer token (allows is_temporary); retorna `TokenResponse` fresco

### Archivos nuevos (f2-auth-staff)
| Archivo | Descripción |
|---|---|
| `backend/app/models/admin_user.py` | Modelo `AdminUser` (id, username, hashed_password, is_temporary, created_at) |
| `backend/app/schemas/auth.py` | LoginRequest, TokenResponse, ChangePasswordRequest, AdminUserRead |
| `backend/app/repositories/admin_user_repository.py` | get_first, get_by_username, create, update_password |
| `backend/app/services/auth_service.py` | AuthService, AuthError, hash_password, verify_token, _create_token |
| `backend/app/api/deps.py` | get_current_user (allows is_temporary), require_active_user (blocks is_temporary) |
| `backend/app/api/routes/auth.py` | Router /auth con login y change-password |
| `backend/scripts/reset_admin.py` | Reset contraseña admin a temporal (UPDATE, nunca DELETE) |
| `frontend/src/contexts/AuthContext.tsx` | AuthProvider, useAuth, TOKEN_KEY, parseToken, loadInitialState |
| `frontend/src/components/ProtectedRoute.tsx` | Guard de React Router v6 (requiere token; redirige a /change-password si is_temporary) |
| `frontend/src/pages/Login.tsx` | Pantalla de login con toggle show/hide, banner sesión expirada |
| `frontend/src/pages/ChangePassword.tsx` | Pantalla cambio de contraseña (primer login y voluntario); recibe token fresco sin re-login; botón "Cancelar" visible solo cuando `!isTemporary` |

### Archivos modificados (f2-auth-staff)
| Archivo | Cambio |
|---|---|
| `backend/requirements.txt` | `python-jose[cryptography]==3.3.0`, `passlib[bcrypt]==1.7.4`, `bcrypt==4.0.1` |
| `backend/app/core/config.py` | `jwt_secret_key`, `jwt_expire_hours`, `admin_initial_password`; model_validator extendido |
| `backend/app/models/__init__.py` | Export `AdminUser` |
| `backend/app/database/init_db.py` | Import `AdminUser`; `_seed_admin_user()` idempotente al final de `init_db()` |
| `backend/app/main.py` | auth router (público); `_protected` aplicado a 10 routers; `Authorization` en CORS allow_headers |
| `frontend/src/types/index.ts` | LoginRequest, TokenResponse, ChangePasswordRequest |
| `frontend/src/services/api.ts` | `req()` añade header Bearer; 401 → redirect a /login?expired=1; loginUser(), changePassword() |
| `frontend/src/App.tsx` | AuthProvider wrapper; rutas /login y /change-password fuera de AppLayout; logout + username + botón candado cambio voluntario de contraseña en sidebar |

---

🔧 f3-edicion-local **F3 — Kit de Entrega Rhinopower (Edición Local).** Primera versión instalable y comercializable del sistema. Sin cambios en lógica de negocio; únicamente empaquetado, scripts operativos y documentación del cliente.

**Cambios de código:**
- `frontend/src/App.tsx`: etiqueta de versión `v0.1.0 · Fase 2` → `v1.0 · Local`.
- `docker-compose.yml`: añade `name: rhinopower` (contenedores predecibles) y directivas `image: rhinopower/backend:1.0` / `image: rhinopower/frontend:1.0` — fuente única para dev (`--build`) y distribución (imagen pre-construida).
- `.env.example`: documenta variables F2 faltantes (`JWT_SECRET_KEY`, `ADMIN_INITIAL_PASSWORD`).

**Scripts operativos (nuevos en raíz):**
- `start.bat` — inicia Docker Compose y abre el navegador en `http://localhost`.
- `stop.bat` — detiene los contenedores de forma ordenada.
- `upgrade.bat` — migración automática y aditiva de `aplicacion-gym_db-data` → `rhinopower_db-data` para instalaciones pre-F3; idempotente para instalaciones nuevas.
- `backup-manual.bat` — crea respaldo manual vía `docker compose exec backend python scripts/create_backup.py`.
- `reset-password.bat` — restablece contraseña admin a la inicial vía `docker compose exec backend python scripts/reset_admin.py`.
- `load-images.bat` — carga imágenes `.tar` para instalaciones offline.

**Script backend standalone (nuevo):**
- `backend/scripts/create_backup.py` — backup manual con solo stdlib (`sqlite3.backup()`); sin dependencias de FastAPI ni BackupService.

**Documentación del cliente (nueva en `docs/`):**
- `INSTALACION.md` — guía paso a paso para el instalador (~30 min).
- `OPERACION.md` — operación diaria para el operador del gimnasio.
- `BACKUP.md` — respaldo automático/manual y procedimiento de restauración.
- `SOPORTE.md` — problemas comunes, soluciones y advertencia crítica sobre `docker compose down -v`.
- `ACTUALIZACION.md` — procedimiento de upgrade desde versión anterior con fallback manual.

**Documentación interna del publicador:**
- `docs/EMPAQUETADO.md` — proceso de build, export de imágenes `.tar` y checklist de entrega.

**Deuda técnica generada:** TD-61 (Feature Flags — diferido a F5), TD-62 (LAN multi-PC — diferido a F5/Local Plus), TD-63 (migración de volumen — mitigado por `upgrade.bat`).

**Auditoría (Paso 6):** Aprobada con observaciones. Observaciones resueltas en Paso 7: packaging documentado (`EMPAQUETADO.md`), advertencia `down -v` en `SOPORTE.md`, migración automatizada (`upgrade.bat` + `ACTUALIZACION.md`).

🔧 fix-td04-td50 **TD-04 + TD-50 — Cierre Edición Local (2026-06-19).**
- **TD-04 resuelto:** `AttendanceService.check_in()` y `get_voucher_status()` usan `(datetime.utcnow() + BOGOTA_OFFSET).date()` para `check_in_date`. Elimina la posibilidad de doble check-in para valeras usadas después de las 19:00 hora Bogotá. La comparación de vigencia (`end_date < now`) permanece en UTC (correcto). Import de `BOGOTA_OFFSET` añadido. Sin migración de BD ni impacto en datos históricos.
- **TD-50 resuelto:** `SaleService` incorpora `MemberRepository` en su constructor. `create_sale()` valida que `customer_id` (member_id canónico) existe antes de crear la venta; retorna HTTP 400 "Cliente no encontrado." si no. Sin cambios de esquema, frontend ni datos existentes.

| Archivo | Cambio |
|---|---|
| `backend/app/services/attendance_service.py` | Import `BOGOTA_OFFSET`; `today` y `attended_today` usan hora Bogotá |
| `backend/app/services/sale_service.py` | `MemberRepository` en constructor; validación explícita de `customer_id` |

🔧 fix-td42-td35 **TD-42 + TD-35 — Cierre Edición Local (2026-06-19).**

- **TD-42 resuelto:** Middleware de rate limiting custom para `POST /api/auth/login`. Sliding-window en memoria (`defaultdict[str, list[float]]`). Sin dependencias externas. Configuración centralizada en `config.py` (`login_rate_limit_window=60s`, `login_rate_limit_max_attempts=20`). Desactivado automáticamente cuando `debug=True`. Limpieza de timestamps expirados en cada request. Respuesta HTTP 429 genérica. Logger warning con IP y conteo. El middleware se registra ANTES de `CORSMiddleware` en el stack (índice 0 en `user_middleware`, interior tras `reversed()` del build) — la respuesta 429 pasa por CORS y tiene headers de origen. Estado en memoria, reset al reiniciar contenedor. 6/6 tests funcionales PASS.

- **TD-35 resuelto (parcial):** Actualización de dependencias Python con correcciones de seguridad acumuladas. `cryptography` mantenida en 41.0.7 (python-jose 3.3.0 incompatible con ≥42.x; CVEs de 41.x no aplican al app — sin endpoints PKCS12 ni multipart). 5/6 packages actualizados; 6 smoke tests PASS post-upgrade.

| Archivo | Cambio |
|---|---|
| `backend/app/main.py` | `_login_attempts` dict; middleware `_login_rate_limiter` (http) |
| `backend/app/core/config.py` | `login_rate_limit_window`, `login_rate_limit_max_attempts` |
| `backend/requirements.txt` | fastapi 0.104.1→0.115.6; uvicorn 0.24.0→0.30.6; sqlalchemy 2.0.23→2.0.36; pydantic 2.5.0→2.10.6; pydantic-settings 2.1.0→2.6.1 |

**Deuda técnica generada:** TD-64 (`python-jose` bloquea `cryptography ≥42.x` — reemplazar por `PyJWT` en F4).

🔧 plataforma-estrategia **Estrategia de Plataforma y Documentación Fundacional (2026-06-19).**
Sin cambios de código. Sesión de definición de producto y arquitectura de plataforma.

**Decisión aprobada:** Rhinopower pasa a ser el primer cliente de la plataforma, no el producto. El sistema evoluciona hacia una plataforma transversal multi-gimnasio denominada **gym-platform**.

**Decisiones de arquitectura aprobadas:**
- Repositorio único renombrado a `gym-platform` (sin repos adicionales, sin monorepo, sin ramas de larga duración)
- Separación Core/Premium mediante estructura de directorios `backend/app/modules/`
- Feature flags via variables de entorno (`MODULE_NOTIFICATIONS`, `MODULE_ACCESS_CONTROL`, etc.) — sin flags en base de datos
- Endpoint público `GET /api/config/features` — expone módulos activos al frontend
- Releases por cliente via git tags (`v1.1-local`, `v1.2-platform`, ...)
- Modelo ISV local (Docker en PC del gimnasio) — SaaS cloud diferido a F8+ (>20 clientes)

**Modelo comercial aprobado:**
- Licencia anual de uso (no perpetua, no SaaS mensual)
- Plan Starter $1.8M · Professional $4.2M · Premium $8.4M COP/año
- 9 módulos Premium como add-ons independientes (P-01 a P-09)
- Servicios profesionales por separado (implementación, migración, hardware)

**Documentación fundacional generada:**
| Documento | Contenido |
|---|---|
| `PRODUCT_VISION.md` | Visión, misión, mercado, propuesta de valor, principios |
| `PRODUCT_ROADMAP.md` | Roadmap 24m: F4 Platform Ready → F7 Intelligence |
| `PRODUCT_MODULES.md` | Catálogo completo: 7 Core + 9 Premium con flags, precios y dependencias |
| `LICENSING_STRATEGY.md` | Planes, add-ons, servicios, upsell, renovación, LTV y ARR proyectado |
| `PLATFORM_ARCHITECTURE.md` | Decisiones de arquitectura, ISV model, feature flags, Core/Premium separation |

**Roadmap aprobado (24 meses):**
- F4 Platform Ready (M1–6): feature flags, 2° cliente, P-01 Comunicación, P-07 Seguimiento, PyJWT migration
- F5 Premium Edition (M7–12): P-02 Cobros, P-03 Web, P-04 Acceso SW, P-08 Analítica
- F6 Digital & Access (M13–18): P-06 App Móvil, P-05 Hardware, P-08 Avanzada
- F7 Intelligence (M19–24): P-09 IA Predictiva, API pública

🔧 f4-c-licensing **F4-C — Super Admin Licensing y Gestión de Módulos.** · **Estado:** Implementado · Probado · Auditado · Aprobado

Sistema de licenciamiento comercial y control de módulos Premium desde UI de Super Admin. El ISV (desarrollador) puede activar/desactivar módulos por gimnasio desde el panel `/superadmin/licencia`, sin modificar `.env` ni código. Los operadores del gimnasio (Admin) no pueden modificar su propia configuración de módulos.

**Arquitectura de dos compuertas:**
- Gate 1 — `MODULE_REGISTRY` en código (`app/core/licensing.py`): catálogo técnico de módulos disponibles (constantes, no BD).
- Gate 2 — `gym_modules` en BD: estado comercial por gimnasio. Caché en memoria (`app/core/module_cache.py`): `_cache: dict[int, dict[str, bool]]`, invalidado explícitamente en cada write del Super Admin.

**Ajustes A1–A6 incorporados:**
- A1: Constantes de licenciamiento en `app/core/licensing.py` (no en capa `domain/`).
- A2: `LicensePanel.tsx` con todas las secciones inline (sin sub-componentes separados).
- A3: `GET /api/config/features` usa `has_gym(1)` → module_cache si existe, fallback a settings si no (compatibilidad con arranque frío o seed pendiente).
- A4: Routers Premium siempre registrados; enforcement por request con `require_module(key)` en `include_router()`.
- A5: Tokens sin claim `role` / `gym_id` defaultean a `role='admin'` / `gym_id=1` (backward compat).
- A6: Solo endpoints específicos (no `PUT /api/superadmin/license` genérico).

**Migración automática en startup (`init_db.py`):**
- `_add_column_if_missing("admin_users", "role", ...)` y `gym_id` — columnas nuevas sin ruptura.
- `_migrate_to_licensing_system()` — seed idempotente de Gym, GymLicense, GymModule desde estado `.env` existente.
- `_migrate_add_missing_modules()` — añade filas para nuevas claves MODULE_REGISTRY cada startup.
- `_seed_super_admin_user()` — solo si `SUPER_ADMIN_PASSWORD` está definido.

**Downgrade de plan:** módulos que pierden cobertura de plan quedan como `source='addon'`, `active=True`. El Super Admin decide explícitamente qué hacer.

**Endpoints (5 — Super Admin only, `require_super_admin`):**
- `GET /api/superadmin/panel` — GymLicensePanel completo.
- `PUT /api/superadmin/gym` — actualizar info del gimnasio.
- `PUT /api/superadmin/license/plan` — cambiar plan comercial.
- `PUT /api/superadmin/license/validity` — actualizar fechas de vigencia.
- `PATCH /api/superadmin/modules/{module_key}` — toggle de módulo individual.

**Frontend (`/superadmin/licencia`):**
- `LicensePanel.tsx`: GymSection (nombre/contacto), LicenseSection (plan + fechas), ModulesSection (toggle switches + badges de origen).
- `App.tsx`: entrada "Licencias" en `NAV_BOTTOM` con `roleRequired: 'super_admin'`; `SuperAdminGuard` en ruta.
- `AuthContext.tsx`: `role: UserRole` extraído del JWT; backward compat A5 aplicado.

**Variables `.env` nuevas:** `SUPER_ADMIN_PASSWORD`, `GYM_NAME`, `GYM_PLAN`. Las variables `MODULE_*` existentes se usan únicamente para el seed inicial.

### Archivos nuevos (f4-c-licensing)
| Archivo | Descripción |
|---|---|
| `backend/app/core/licensing.py` | `MODULE_REGISTRY`, `PLAN_MODULES`, `MODULE_DEPENDENCIES` |
| `backend/app/core/module_cache.py` | Caché en memoria: `load()`, `refresh_gym()`, `module_is_active()` |
| `backend/app/models/gym.py` | Modelos `Gym`, `GymLicense`, `GymModule` |
| `backend/app/schemas/gym.py` | Schemas Pydantic: `GymRead`, `LicenseRead`, `ModuleStatusRead`, `GymLicensePanel`, etc. |
| `backend/app/repositories/license_repository.py` | `LicenseRepository`: get_gym, get_active_license, get_modules, get_module |
| `backend/app/services/license_service.py` | `LicenseService`: get_panel, update_gym, change_plan, update_validity, toggle_module |
| `backend/app/api/routes/superadmin.py` | 5 endpoints Super Admin |
| `backend/scripts/reset_super_admin.py` | Reset password super_admin desde CLI |
| `frontend/src/pages/LicensePanel.tsx` | Panel completo con secciones inline (A2) |

### Archivos modificados (f4-c-licensing)
| Archivo | Cambio |
|---|---|
| `backend/app/models/admin_user.py` | `+role VARCHAR(20)`, `+gym_id INTEGER nullable` |
| `backend/app/models/__init__.py` | `+Gym, GymLicense, GymModule` exports |
| `backend/app/core/config.py` | `+super_admin_password`, `+gym_name`, `+gym_plan`; validator producción |
| `backend/app/database/init_db.py` | `+_migrate_to_licensing_system`, `+_migrate_add_missing_modules`, `+_seed_super_admin_user` |
| `backend/app/services/auth_service.py` | JWT `+role`, `+gym_id` en payload |
| `backend/app/api/deps.py` | `+require_super_admin`, `+require_module(key)` |
| `backend/app/api/routes/config.py` | A3: fallback module_cache → settings |
| `backend/app/main.py` | `+load_from_db()` startup; routers Premium siempre registrados con `require_module` (A4); `+superadmin router` |
| `frontend/src/types/index.ts` | `+UserRole`, `+GymInfo`, `+LicenseInfo`, `+ModuleStatus`, `+GymLicensePanel`, tipos Upsert |
| `frontend/src/services/api.ts` | `+getSuperAdminPanel`, `+updateGymInfo`, `+changeGymPlan`, `+updateLicenseValidity`, `+toggleModule` |
| `frontend/src/contexts/AuthContext.tsx` | `+role: UserRole` en `AuthState` y `parseToken`; A5 backward compat |
| `frontend/src/App.tsx` | `+SuperAdminGuard`; `+roleRequired` en `NAV_BOTTOM`; ruta `/superadmin/licencia` |
| `.env.example` | `+SUPER_ADMIN_PASSWORD`, `+GYM_NAME`, `+GYM_PLAN` |

### Validacion (f4-c-licensing)
- **Paso 5 (PASS con riesgos):** 35 tests. Sin defectos bloqueantes. Riesgos TD-67 a TD-70 registrados y diferidos.
- **Paso 5.5 (PASS con riesgos):** 22 tests de datos. Migración idempotente verificada. Compatibilidad con instalaciones previas a F4-C confirmada. Cero pérdida de datos históricos.
- **Paso 6 (Aprobada con observaciones):** calidad de código correcta. R-01/R-02 (Docker desactualizado) y R-04 (reset manual de contraseña en volumen existente) identificados como riesgos operativos. Resueltos antes del Paso 7.
- **Despliegue operativo (commit c3eb5b3):** migraciones ejecutadas sin errores sobre gym.db con datos históricos. Tablas `gyms`, `gym_licenses`, `gym_modules` creadas. 9 módulos en cache. `GET /api/superadmin/panel` responde 200.

---

### Procedimiento de primer acceso (f4-c-licensing)

1. Asegurarse de que `.env` contenga `SUPER_ADMIN_PASSWORD`, `GYM_NAME` y `GYM_PLAN`.
2. Reconstruir imágenes: `docker compose build && docker compose up -d`.
3. Abrir `http://localhost` e iniciar sesión con usuario `super_admin` y la contraseña definida en `SUPER_ADMIN_PASSWORD`.
4. El sistema redirige a `/change-password` — acceso al resto de la app bloqueado hasta completar el cambio.
5. Ingresar y confirmar la nueva contraseña definitiva.
6. Navegar a `http://localhost/superadmin/licencia` — el panel de licenciamiento muestra el gimnasio, la licencia activa y los módulos.

---

### Diferencia entre SUPER_ADMIN_PASSWORD y contraseña en BD

`SUPER_ADMIN_PASSWORD` tiene dos usos exclusivos, igual que `ADMIN_INITIAL_PASSWORD`:

| Cuándo se usa | Descripción |
|---|---|
| Seed inicial (`_seed_super_admin_user`) | Primer arranque sin usuario `super_admin` → crea `admin_users` con esta contraseña y `is_temporary=True`. Si el usuario ya existe, el seed se salta silenciosamente. |
| Reset manual (`reset_super_admin.py`) | Restablece la contraseña del super_admin existente al valor de `SUPER_ADMIN_PASSWORD` con `is_temporary=True`. |

**No se usa en runtime:** la contraseña activa del Super Admin vive en `admin_users.hashed_password` (DB). Cambiar `SUPER_ADMIN_PASSWORD` en `.env` después del primer login no tiene ningún efecto hasta la próxima ejecución de `reset_super_admin.py`.

**Caso especial (volumen existente con super_admin previo):** si la BD ya tenía un usuario `super_admin` de una sesión de pruebas anterior, el seed lo omite y la contraseña en BD puede no coincidir con `SUPER_ADMIN_PASSWORD`. Ejecutar `reset_super_admin.py` para sincronizarlas. TD-71.

---

### Reset de contraseña de emergencia (reset_super_admin.py)

Si el ISV pierde acceso al Super Admin o necesita restablecer la contraseña:

```bash
# Dentro del contenedor backend:
docker exec -it rhinopower-backend-1 python scripts/reset_super_admin.py

# O en entorno local con virtualenv activo (desde backend/):
python scripts/reset_super_admin.py
```

El script:
- Actualiza `hashed_password` al hash de `SUPER_ADMIN_PASSWORD` del `.env`.
- Establece `is_temporary=True` — el Super Admin debe cambiar la contraseña en el siguiente login.
- Nunca elimina ni recrea el usuario (usa `UPDATE`, no `DELETE+INSERT`).
- Falla con error descriptivo si `SUPER_ADMIN_PASSWORD` no está configurada.

---

### Flujo de activacion y desactivacion de modulos

1. Iniciar sesión como `super_admin` en `http://localhost`.
2. Navegar a **Licencias** en el sidebar (solo visible para `super_admin`).
3. En la sección **Módulos**: cada módulo tiene un toggle switch.
4. Al activar/desactivar, el cambio se persiste en `gym_modules` y se invalida el caché en memoria.
5. El módulo queda disponible o bloqueado para el Admin del gimnasio en la próxima request.
6. Los módulos incluidos en el plan aparecen con badge **Plan**; los activados manualmente fuera del plan aparecen con badge **Addon**.

---

### Flujo de cambio de plan

1. En el panel de Licencias, sección **Licencia** → botón **Cambiar**.
2. Seleccionar el nuevo plan (`starter`, `professional`, `premium`).
3. Al confirmar: `gym_modules` se recalcula — los módulos cubiertos por el plan nuevo se activan; los que salen del plan pasan a `source='addon'` pero permanecen `active=True` (TD-68).
4. El ISV debe revisar manualmente los módulos addon post-downgrade y desactivar los que no correspondan.

---

### Consideraciones de despliegue para futuras instalaciones

**Instalacion limpia (volumen vacio):** el seed `_seed_super_admin_user` crea el usuario `super_admin` con la contraseña de `SUPER_ADMIN_PASSWORD` y `is_temporary=True`. Flujo normal de primer acceso.

**Upgrade sobre volumen existente sin F4-C:** el startup ejecuta automáticamente las migraciones `role`/`gym_id` en `admin_users`, el seed de `gyms`/`gym_licenses`/`gym_modules` desde `.env`, y el seed del `super_admin`. Compatible con datos históricos de F1–F3.

**Upgrade sobre volumen con super_admin pre-existente (sesiones de prueba o deploy anterior):** el seed detecta que el usuario existe y lo omite. La contraseña en BD puede no coincidir con `SUPER_ADMIN_PASSWORD`. Ejecutar `reset_super_admin.py` antes del primer acceso. TD-71.

**Deuda tecnica generada:** TD-67 (`gym_id` sin FK en SQLite), TD-68 (módulos addon post-downgrade sin alerta visual), TD-69 (`_GYM_ID=1` hardcoded), TD-70 (toggle retorna 404 para module_key inválido), TD-71 (seed omite super_admin existente con contraseña desconocida).

---

🔧 f4-b-premium-frontend **F4-B — Módulos Premium y Frontend Dinámico.** · **Estado:** Implementado · Probado · Auditado · Aprobado

Integración frontend↔backend vía `GET /api/config/features`. Cero cambios de backend — F4-A ya implementaba registro condicional de routers.

**Cambios frontend:**
- `FeaturesContext` (nuevo): `createContext` → `useState(ALL_TRUE)` → fetch al montar → re-render solo si responde. Patrón idéntico a `AuthContext`. Estado inicial all-true preserva compatibilidad con Rhinopower (opt-out).
- `getFeatures()` en `api.ts`: reutiliza `req()` con `.catch(() => null)`. Mismo patrón que `getMeasurements`.
- `App.tsx`: `FeaturesProvider` envuelve `<Routes>`. `NAV` y `NAV_BOTTOM` añaden campo `moduleFlag?: keyof PremiumFeatures`. Sidebar filtra items con `!moduleFlag || premium[moduleFlag]`. Tienda → flag `store`; Configuración → flag `notifications`.
- `Dashboard.tsx`: panel "Notificaciones" condicionado a `{premium.notifications && ...}`. `Promise.allSettled` sin cambios — maneja 404 graceful si `notifications=false`.
- `MemberInfo.tsx`: sección "Medidas corporales" condicionada a `{premium.body_tracking && ...}`. `handleSave` no llama `upsertMeasurements` si `body_tracking=false` (evita 404 al guardar datos personales). `useEffect` de carga omite `getMeasurements` si módulo inactivo.
- `types/index.ts`: añade `PremiumFeatures` y `FeaturesResponse`.

**Modelo de fallback (Opción B, aprobado en Paso 3):** render inmediato con all-true. Cuando `getFeatures()` resuelve, re-render con valores reales. En ISV Local el delta es imperceptible (<100ms). Sin pantalla de carga adicional.

**Opt-out garantizado:** `ALL_TRUE` como estado inicial + defaults `True` en backend → instalaciones Rhinopower sin `MODULE_*` en `.env` ven todos los módulos siempre.

**Decisión: timeout de `getFeatures()` eliminado (Paso 4, aprobado por usuario).** Justificación: inconsistente con patrones de `api.ts`; sin valor significativo en modelo ISV local (endpoint responde <5ms, solo lee config); introduces complejidad innecesaria para un único endpoint. Patrón `req().catch(() => null)` es suficiente.

**Dependencia de contrato (observación de auditoría):** el frontend depende de que `GET /api/config/features` retorne `{ core: {...}, premium: { notifications: bool, body_tracking: bool, store: bool } }`. Cualquier evolución del contrato backend debe sincronizarse con `PremiumFeatures` en `types/index.ts`. Documentado en TD-65.

### Validación (f4-b-premium-frontend)
**Paso 5 — PASS con riesgos:** TypeScript PASS. Sin defectos funcionales. Sin regresiones. Rhinopower mantiene comportamiento equivalente al estado previo. TD-66 registrado (rutas premium accesibles por URL directa cuando módulo desactivado — baja prioridad, diferido a F5).

**Validación visual en Docker (4 escenarios — todos PASS):**
- Escenario A (todo defaults): sidebar muestra Dashboard/Clientes/Pagos/Asistencia/Tienda/Configuración. Panel Notificaciones visible. Sección Medidas corporales visible.
- Escenario B (`MODULE_STORE=false`): ítem Tienda desaparece del sidebar. Resto intacto.
- Escenario C (`MODULE_NOTIFICATIONS=false`): ítem Configuración desaparece del sidebar. Panel Notificaciones en Dashboard oculto.
- Escenario D (`MODULE_BODY_TRACKING=false`): Sección Medidas corporales en ficha de cliente oculta. Datos personales se guardan correctamente sin llamar `upsertMeasurements`.
- Estado restaurado a todos defaults al finalizar validación.
- Nota operativa: `docker compose up -d backend` (no `restart`) es requerido para que cambios de `.env` surtan efecto.

**Paso 6 — Auditoría APROBADA con observaciones:** implementación coincide con diseño aprobado. Sin regresiones. Riesgo TD-66 aceptado como baja prioridad.

### Archivos modificados (f4-b-premium-frontend)
| Archivo | Cambio |
|---|---|
| `frontend/src/types/index.ts` | `PremiumFeatures`, `FeaturesResponse` |
| `frontend/src/services/api.ts` | `getFeatures()` — req + catch null |
| `frontend/src/App.tsx` | `FeaturesProvider`; `moduleFlag` en NAV items; sidebar dinámico |
| `frontend/src/pages/Dashboard.tsx` | Panel Notificaciones condicional |
| `frontend/src/components/MemberInfo.tsx` | Sección Medidas + `upsertMeasurements` condicionales |

### Archivos nuevos (f4-b-premium-frontend)
| Archivo | Descripción |
|---|---|
| `frontend/src/contexts/FeaturesContext.tsx` | `FeaturesProvider` + `useFeatures()` hook |

---

🔧 f4-a-platform-infra **F4-A — Infraestructura de Plataforma (gym-platform).** · **Commit:** `9f2b12b` · **Estado:** Implementado · Probado · Auditado · Aprobado

- **TD-64 resuelto:** `python-jose 3.3.0` reemplazado por `PyJWT==2.9.0`. `cryptography` actualizado `41.0.7→43.0.3` (desbloqueado al eliminar jose). Tokens HS256 pre-migración compatibles (mismo formato Base64url). Import: `import jwt`; excepción: `jwt.PyJWTError`. 1 archivo modificado (`auth_service.py`).
- **Feature Flags:** 3 campos `module_*: bool` en `Settings` (`config.py`). Modelo opt-out para módulos existentes (defaults `True`); módulos nuevos en F4-B+ usarán `default=False` (opt-in). Flag `False` → router no registrado → HTTP 404 (ruta inexistente).
- **`GET /api/config/features`:** Nuevo endpoint público. Devuelve estado de módulos Core (siempre `true`) y Premium (desde flags). Router registrado antes de `_protected` en `main.py`. TD-65 generado para revisión de auth en F8+ (cloud).
- **Scaffolding `backend/app/modules/`:** Directorios `modules/` y `modules/premium/` con convención documentada. Módulos nuevos nacen aquí; código Core existente no se mueve.
- **Renombrado conceptual:** `project_name` → `"Gym Platform"`, `project_version` → `"1.2.0"`. `.env.example` header y sección `MODULE_*` actualizados.
- **Tag `v1.1-rhinopower`:** Creado antes de F4-A sobre commit `441f5d3`. Línea de referencia estable e inmutable para TD-51, rollback y soporte de Rhinopower.

### Archivos modificados (f4-a-platform-infra)
| Archivo | Cambio |
|---|---|
| `backend/requirements.txt` | `python-jose` → `PyJWT==2.9.0`; `cryptography 41.0.7→43.0.3` |
| `backend/app/services/auth_service.py` | `import jwt`; `except jwt.PyJWTError` |
| `backend/app/core/config.py` | `project_name/version`; campos `module_notifications/body_tracking/store` |
| `backend/app/main.py` | `config.router` público; routers Premium condicionales |
| `.env.example` | Header `Gym Platform`; sección `MODULE_*` documentada |

### Archivos nuevos (f4-a-platform-infra)
| Archivo | Descripción |
|---|---|
| `backend/app/api/routes/config.py` | `GET /api/config/features` — estado de módulos |
| `backend/app/modules/__init__.py` | Scaffolding con convención de organización |
| `backend/app/modules/premium/__init__.py` | Scaffolding Premium con convención de flags |

### Endpoints nuevos (f4-a-platform-infra)
`GET /api/config/features` — devuelve estado activo de módulos Core y Premium (público, sin auth)

## Estado oficial del proyecto — 2026-06-19

### Dos líneas paralelas e independientes

```
Gym Platform (línea Producto)        Rhinopower (línea Cliente)
─────────────────────────────        ──────────────────────────
F4-A ✅ Cerrada (9f2b12b)            Core v1.1 ✅ En producción
F4-B ✅ Cerrada (62844be)            tag: v1.1-rhinopower (441f5d3)
F4   ✅ Técnicamente completada      TD-51 ⏳ Pendiente ejecución
F5   🔒 No autorizado aún
```

> TD-51 pertenece exclusivamente a la línea Rhinopower. No bloquea ni condiciona la evolución de Gym Platform.

### Actividades operativas pendientes — Línea Rhinopower
- **TD-51** — Deploy producción Cliente Único Phase 1: ejecutar checklist sobre datos reales antes de `docker compose build backend`. Verificar V1–V4 sobre `customers`, `sales`, `members`. **DESBLOQUEADO** (TD-04, TD-50, TD-42, TD-35 completados). Programar ventana de despliegue cuando corresponda.

### Estado de cierre Edición Local
```
✅ TD-04  check_in_date Bogotá — resuelto
✅ TD-50  validación FK create_sale — resuelto
✅ TD-42  rate limiting login custom middleware — resuelto (6/6 PASS)
✅ TD-35  actualización deps CVEs — resuelto (cryptography pin justificado → TD-64)
⏳ TD-51  deploy producción — DESBLOQUEADO, pendiente ventana de despliegue
```

### Backlog funcional
- **f4-b-premium-frontend:** ✅ Completado (2026-06-19). Módulos Premium y Frontend Dinámico. FeaturesContext + getFeatures(). Sidebar dinámico. Dashboard/MemberInfo condicionales. Validado en Docker (4 escenarios). Ciclo completo Paso 1→7. Aprobado. TD-66 diferido a F5.
- **f4-a-platform-infra:** ✅ Completado (2026-06-19). Infraestructura de plataforma gym-platform. TD-64 PyJWT cerrado. Feature flags opt-out. GET /api/config/features. Scaffolding modules/premium/. Ciclo completo Paso 1→7. Aprobado con observaciones resueltas (commit 9f2b12b, tag v1.1-rhinopower intacto).
- **f2-auth-staff:** ✅ Completado (2026-06-19). JWT stateless, usuario admin único, flujo temporal/permanente, protección global via deps.py. Validado en Docker Compose. Ciclo completo Paso 1→7. Aprobado con observaciones (TD-58/59/60 registrados).
- **correct-start-date:** ✅ Completado (2026-06-18). Corrección de fecha de inicio de membresía — ciclo completo Paso 1→7. Aprobado con observaciones (TD-55/56/57 diferidos).
- **fix-normalize-date-str:** ✅ Completado (2026-06-18). `normalizeDateStr` corregida — Plan Día vence muestra día Bogotá correcto.
- **F1 Bloque B:** ✅ Completado (2026-06-18). SEC-010/012/015/017 resueltos.
- **TD-46:** ✅ Completado (2026-06-18). `_calculate_status` corregido a hora Bogotá.
- **TD-52/53/54:** ✅ Completado (2026-06-18). Normalización zona horaria Bogotá en Dashboard y MembershipService — 5 líneas en 2 archivos.
- **TD-35 (SEC-008):** ✅ Completado (2026-06-19). Dependencias actualizadas; cryptography 41.0.7 pinned (TD-64).
- **TD-42 (SEC-016):** ✅ Completado (2026-06-19). Rate limiting custom en login; otros endpoints diferidos a F5.
- **Notificaciones Fase 3:** canales adicionales (WhatsApp/SMS) o plantillas personalizables.
- **Tienda Fase D:** exportación de reportes o mejoras operativas.
- **Cliente Único Phase 2:** actualizar frontend para usar `member_id` directamente; eliminar tabla `customers`, `CustomerService` y columna `sales.customer_id` (prerrequisito: mover `CreditPayment` a su propio módulo — TD-49).

### Racionalización documental — 2026-06-19

Consolidación de 25 → 22 archivos .md activos + 2 archivados.

- **Creados:** `PROJECT_INDEX.md` (índice de orientación rápida), `docs/DEPLOYMENT_PLAYBOOK.md` (template de deploy multi-cliente).
- **Archivados en `docs/archive/`:** `ROADMAP_COMERCIALIZACION.md` (contradecía estado actual; §5 migrado a `PLATFORM_ARCHITECTURE.md`, §8 migrado a `PRODUCT_ROADMAP.md`), `REQUERIMIENTOS.md` (obsoleto — describía como pendiente lo ya implementado).
- **Eliminado:** `docs/MANUAL_OPERADOR.md` (contenido absorbido íntegramente por `MANUAL_USUARIO.md`).
- **Editados:** `PLATFORM_ARCHITECTURE.md` (añadida sección security-auditor + Human Gate), `PRODUCT_ROADMAP.md` (añadida estrategia de modelo de IA por fase; P-08 nombre canónico unificado), `LICENSING_STRATEGY.md` (eliminada duplicación de tablas de precios; fuente canónica: `PRODUCT_MODULES.md`; P-08 unificado a "Analítica Avanzada"), `PROJECT_INDEX.md` (añadido `PRODUCT_VISION.md`), `CLAUDE.md` (`PROJECT_INDEX.md` como primera lectura obligatoria; `FEATURE_SUMMARY.md` como segunda).
- **Nombre canónico P-08:** "Analítica Avanzada" — único en `PRODUCT_MODULES.md`, `PRODUCT_ROADMAP.md` y `LICENSING_STRATEGY.md`. La variación v1/v2 se expresa como "(entrega inicial v1)" y "(versión completa)", no como nombres distintos.
- **Cierre de racionalización documental:** una única fuente de verdad por dominio confirmada. Sin duplicidades activas.
