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
🔧 valeras-faseC Frontend asistencia/valeras: tipos CheckInResult y VoucherStatus (types/index.ts); api checkInAttendance (POST /attendance/check-in) y getVoucherStatus (GET /attendance/voucher-status/{document}). Nueva página pages/Attendance.tsx (input cédula, botón registrar ingreso + consultar valera, banner éxito/error con detail verbatim, visualización totales/consumidos/restantes/vencimiento/estado derivado vigente·agotada·vencida solo voucher). Navegación: ruta /attendance + acceso en App.tsx (sidebar real) y Navbar.tsx. Sin tocar backend salvo consumo de endpoints existentes; dashboard, pagos y current-membership sin cambios.

## Endpoints activos

### Members
GET/POST /api/members | GET/PUT/DELETE /api/members/{id}

### Membresías
POST /api/members/{id}/memberships | GET /api/members/{id}/memberships
GET /api/members/{id}/current-membership | POST /api/members/memberships/{id}/renew
PATCH /api/members/memberships/{id}/active (activar/desactivar manual)

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
| components/MemberInfo.tsx | fix7 — datos + medidas, validación |
| pages/Members.tsx | fix8 — deleteMember(id, true) hard delete |
| repositories/dashboard_repository.py | fix9 — get_memberships_by_status() por cliente vía end_date |
| pages/Payments.tsx | fix3 — member_name |
| types/index.ts | fix6 — BodyMeasurementUpsert separado |

## Próximo paso (Fase 2)
Registro de asistencia diaria → alertas vencimiento → reportes
