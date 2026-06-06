# REQUERIMIENTOS.md

## Fase 1 ✅ Completada
**Clientes:** CRUD + búsqueda (nombre/teléfono) + soft delete (is_active)
Campos: nombre, teléfono, documento, notas, fecha_registro
Medidas corporales: edad(años), altura, hombro, pecho, cintura, cola, bíceps, antebrazo, pantorrilla, pierna (cm) + peso (kg)

**Planes:** nombre, precio, duración_días. Tipos: diario/mensual/trimestral/semestral

**Membresías:** asignar plan → calcular vencimiento automático → renovar
Estados: active / expiring (≤5 días) / expired

**Pagos:** registrar, eliminar, historial por cliente, vista global con nombre cliente
Métodos válidos: cash | transfer | qr | nequi

**Dashboard:** clientes activos, membresías por estado, ingresos mes, ingresos por plan, últimas 5 renovaciones

**Frontend:** tema oscuro, sidebar, 3 páginas (Dashboard / Clientes / Pagos)
Panel detalle cliente: tabs Info (datos + medidas) | Membresía | Pagos

## Fase 2 ⏳ Pendiente
Asistencia diaria | Alertas vencimiento | Reportes | WhatsApp

## Fase 3 ⏳ Pendiente
Exportaciones PDF/Excel | Backup | Multiusuario

## Reglas de negocio
- Medidas en cm, peso en kg
- Un cliente = una membresía activa a la vez
- Desactivación = soft delete
- Estadísticas agrupadas por mes calendario
