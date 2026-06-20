# REQUERIMIENTOS.md

> **ARCHIVADO — 2026-06-19**
> Este documento describe el estado de requerimientos de las fases F1–F3 del proyecto original.
> El contenido marcado como "⏳ Pendiente" aquí lleva meses implementado.
> La fuente de verdad del estado actual es `FEATURE_SUMMARY.md`.

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

## Módulo Tienda ✅ Fase A completada

**Categorías:** CRUD + activar/desactivar + eliminar (bloqueado si tiene productos)

**Productos:** CRUD + activar/desactivar + eliminar (bloqueado si tiene ventas o movimientos)
Campos: nombre, categoría, precio venta, costo (opcional), stock, stock mínimo, descripción
Estado derivado: `is_low_stock = stock <= min_stock`

**Inventario:**
- Entrada de stock (`type=entry`) con nota opcional
- Ajuste de stock (`type=adjustment`, cantidad positiva o negativa) con nota obligatoria
- Historial de movimientos por producto
- Endpoint `/inventory/low-stock`: productos activos con stock ≤ min_stock
- Movimiento inicial automático al crear producto con `stock > 0`

**Ventas de contado:**
- Carrito multi-producto con descuento global y notas
- Venta atómica: valida stock de todos los ítems ANTES de cualquier escritura
- Descuento no puede hacer el total negativo (mínimo 0)
- `unit_price` es snapshot del precio al momento de la venta
- Anulación repone stock y crea movimiento `adjustment` de reposición
- Venta anulada no puede re-anularse

**Reglas de negocio tienda:**
- Categoría con productos no se puede eliminar
- Producto con ventas o movimientos no se puede eliminar (desactivar en su lugar)
- Producto inactivo no puede venderse
- `InsufficientStockError` → HTTP 409 (distingue de errores de validación 400)
- Ventas sin ítems → HTTP 422 (validación Pydantic `min_length=1`)

**Frontend:** página `/tienda` con tabs Productos / Ventas / Categorías
- Tab Productos: búsqueda, filtro por categoría, modal inventario/movimientos inline
- Tab Ventas: carrito de nueva venta + historial + anulación
- Tab Categorías: crear, activar/desactivar, eliminar

## Módulo Tienda ✅ Fase B — Implementado
Customer independiente vinculable a Member (1:1 opcional) | Ventas a crédito (payment_type=credit) | Estados PAID/PARTIAL/PENDING/CANCELLED | Abonos inmutables (CreditPayment) | KPIs cartera en módulo Tienda | Creación rápida de cliente desde carrito | Búsqueda clientes por nombre/documento/teléfono

## Módulo Tienda ✅ Fase C — Implementado
Reportes operativos: endpoint único GET /api/store/reports. Tres bloques fijos:
- Ventas (filtrados por período): total, ingresos, contado/crédito, abonos cobrados, ticket promedio, top 5 productos por SQL.
- Cartera (siempre actual): saldo pendiente, clientes con deuda, pendientes, parciales, deuda más antigua.
- Inventario (siempre actual): hasta 10 productos con bajo stock.
Ventas CANCELLED excluidas de todos los KPIs. Filtro de fecha solo afecta bloque Ventas.
Frontend: tab Reportes en /tienda con selector Hoy / Esta semana / Este mes / Personalizado.
Fix TD-21 incluido: delete_sale_cascade y delete_empty_sales limpian credit_payments; startup purga registros huérfanos e inválidos.

## Fase 2 ⏳ Pendiente
Alertas vencimiento | Reportes membresías | WhatsApp

## Fase 3 ⏳ Pendiente
Exportaciones PDF/Excel | Backup | Multiusuario

## Reglas de negocio
- Medidas en cm, peso en kg
- Un cliente = una membresía activa a la vez
- Desactivación = soft delete
- Estadísticas agrupadas por mes calendario
