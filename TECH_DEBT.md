# TECH_DEBT.md

Registro de deuda técnica y pendientes identificados durante las Fases A, B, B.5 (regla de valera única + corrección de renovación), C (frontend de asistencia) y correcciones post-lanzamiento (UNIQUE constraint attendances, purge huérfanas).

Este documento recopila **únicamente** los riesgos detectados en esas fases. No surge de un nuevo análisis de código. Su objetivo es que cualquier desarrollador o modelo entienda el contexto sin acceder al historial de la conversación.

Prioridad: **Alta** (afecta datos o reglas de negocio) · **Media** (afecta UX o consistencia) · **Baja** (cosmético / no funcional).

---

## TD-01 — Valeras agotadas/vencidas siguen apareciendo como activas en Dashboard y current-membership ✅ RESUELTO

- **ID:** TD-01
- **Estado:** Resuelto.
- **Solución aplicada:** `_enrich_membership` en `MembershipService` sobreescribe `status='exhausted'` cuando la valera está dentro de fecha pero `COUNT(attendances) >= entries_total`. `DashboardRepository.get_memberships_by_status` usa subquery correlacionada para contar asistencias por membresía y clasifica las agotadas en bucket `exhausted` (sale de `active`/`expiring`). `MembershipStatusSummary` gana campo `exhausted: int = 0`. Dashboard muestra StatCard "Valeras agotadas". Badge frontend cubre el nuevo estado con token `energy`.
- **Habilitado para futuro:** las valeras podrán incorporarse al panel de alertas usando el estado operativo real.
- **Archivos modificados:** `repositories/dashboard_repository.py`, `services/dashboard_service.py`, `services/membership_service.py`, `schemas/dashboard.py`, `frontend/src/types/index.ts`, `frontend/src/pages/Dashboard.tsx`, `frontend/src/components/Badge.tsx`, `frontend/src/index.css`.

---

## TD-02 — Posible coexistencia de valeras preexistentes en datos antiguos ✅ RESUELTO

- **ID:** TD-02
- **Estado:** Resuelto.
- **Solución aplicada:** `_deactivate_duplicate_active_vouchers()` en `init_db.py`, ejecutada en cada startup dentro de `_run_migrations()`. Detecta clientes con más de una valera `is_active=True`, conserva la más reciente (`start_date DESC, id DESC`) y desactiva las sobrantes con UPDATE SQL. Idempotente: no actúa si no hay duplicados.
- **Archivos modificados:** `database/init_db.py`.

---

## TD-03 — Cédula (document) no obligatoria ni garantizada única a nivel de negocio

- **ID:** TD-03
- **Título:** El check-in depende de la cédula, pero la cédula es opcional.
- **Descripción:** El flujo de asistencia identifica al cliente por su cédula (`document`). En el modelo `Member`, `document` es opcional (`nullable=True`). Un cliente sin cédula registrada no puede hacer check-in. Aunque la columna es `unique`, la ausencia de obligatoriedad permite clientes sin documento.
- **Riesgo:** Clientes con valera pero sin cédula quedan imposibilitados de registrar asistencia; fricción operativa en recepción.
- **Impacto:** Medio. Bloquea el caso de uso de asistencia para clientes sin documento.
- **Módulos afectados:** `models/member.py`, `schemas/member.py`, frontend de alta/edición de clientes, `attendance_service.py` (resolución por cédula).
- **Prioridad:** Media.
- **Recomendación futura:** Definir regla de negocio: hacer la cédula obligatoria para clientes que adquieran valeras (validación en el alta o al vender la valera), o permitir check-in por un identificador alternativo.

---

## TD-04 — UTC en restricción de asistencia diaria (check_in_date) — parcialmente resuelto

- **ID:** TD-04
- **Título:** La restricción UNIQUE `(member_id, check_in_date)` usa fecha UTC, no fecha Bogotá.
- **Estado:** **Parcialmente resuelto** — ver fix `fix-plan-dia-timezone`.
- **Descripción:** El backend almacena `check_in_date` como `date` UTC. Un cliente que registre asistencia entre las 19:00 y las 23:59 hora Bogotá obtiene `check_in_date` del día UTC siguiente, lo que podría permitir un doble check-in el día local correcto.
- **Qué fue corregido (fix-plan-dia-timezone):**
  - `_calculate_end_date` para Plan Día ahora calcula `end_date` como 23:59:59 hora Bogotá (no UTC).
  - `get_membership_alerts` clasifica alertas usando fecha Bogotá local (`datetime.utcnow() + BOGOTA_OFFSET`).
  - Visualización de todas las fechas de membresía en frontend usa `fmtBogotaDate` (timezone `America/Bogota`).
  - `BOGOTA_OFFSET = timedelta(hours=-5)` centralizado en `app/core/config.py`.
  - Migración correctiva aplicada a 6 registros históricos con lógica antigua (2026-06-12).
- **Riesgo residual:** `check_in_date` en tabla `attendances` sigue siendo fecha UTC. Si un cliente registra asistencia después de las 19:00 Bogotá, `check_in_date` corresponde al día siguiente UTC, lo que puede:
  - Permitir doble check-in en el día local.
  - Mostrar la asistencia en el día incorrecto en un historial futuro.
- **Impacto residual:** Medio. Afecta solo a clientes con valera que asistan después de las 19:00 Bogotá.
- **Módulos afectados pendientes:** `attendance_repository.py` (`create_attendance` — usa `datetime.utcnow().date()`), restricción `UNIQUE(member_id, check_in_date)`.
- **Prioridad:** Media.
- **Solución futura:** Usar `(datetime.utcnow() + BOGOTA_OFFSET).date()` al generar `check_in_date` en `AttendanceRepository.create_attendance`. Requiere validar que la restricción UNIQUE siga siendo coherente con la nueva fecha local.

---

## TD-05 — Renovación no desactiva la membresía anterior ✅ RESUELTO

- **ID:** TD-05
- **Estado:** Resuelto.
- **Solución aplicada:** `renew_membership` llama `deactivate_no_commit(old_membership.id)` antes de `create()`. El commit único de `create()` cubre ambas operaciones atómicamente. Membresía anterior queda `is_active=False` en el mismo ciclo de transacción.
- **Archivos modificados:** `repositories/membership_repository.py` (nuevo método `deactivate_no_commit`), `services/membership_service.py` (`renew_membership`).

---

## TD-06 — Visualización de valera limitada a la página de Asistencia

- **ID:** TD-06
- **Título:** La información de la valera no se muestra en el detalle del cliente.
- **Descripción:** En la Fase C, la visualización de ingresos (totales / consumidos / restantes), vencimiento y estado de la valera se implementó únicamente en la página de Asistencia. No se surface en la vista de detalle del cliente (`MemberInfo`) ni en current-membership, por la restricción de no modificar esas vistas.
- **Riesgo:** Para ver el estado de la valera de un cliente hay que pasar por la página de Asistencia; no es visible desde su ficha.
- **Impacto:** Bajo. Limitación de UX, sin afectar funcionalidad.
- **Módulos afectados:** Frontend `components/MemberInfo.tsx`, current-membership (consumo en frontend).
- **Prioridad:** Baja.
- **Recomendación futura:** Cuando se decida tocar el detalle del cliente, mostrar el resumen de la valera (consumo y estado) reutilizando el endpoint `GET /api/attendance/voucher-status/{document}` ya existente, solo para membresías tipo voucher.

---

## TD-07 — `Navbar.tsx` es código muerto

- **ID:** TD-07
- **Título:** Componente de navegación sin uso.
- **Descripción:** La navegación real de la aplicación vive en `App.tsx` (sidebar). El componente `components/Navbar.tsx` no está montado en la app. En la Fase C se actualizó por consistencia (se le agregó el enlace de Asistencia), pero sigue sin renderizarse.
- **Riesgo:** Confusión para futuros desarrolladores; mantenimiento duplicado de la lista de enlaces (App.tsx + Navbar.tsx).
- **Impacto:** Bajo. No afecta el funcionamiento.
- **Módulos afectados:** Frontend `components/Navbar.tsx`.
- **Prioridad:** Baja.
- **Recomendación futura:** Eliminar `Navbar.tsx` si se confirma que no se usará, o adoptarlo como componente único de navegación y retirar la lista embebida en `App.tsx`.

---

## TD-08 — Validación end-to-end en navegador no concluida

- **ID:** TD-08
- **Título:** Falta confirmación visual en navegador de la Fase C.
- **Descripción:** La Fase C se validó con compilación exitosa (`tsc --noEmit` sin errores), pruebas funcionales a nivel de servicio/ruta y verificación de endpoints operativos. La validación automatizada en navegador se detuvo antes de concluir, por lo que no hay confirmación visual automatizada del render, la navegación y la consola del navegador.
- **Riesgo:** Posibles problemas de render o de consola no detectados que no se reflejan en el typecheck.
- **Impacto:** Bajo. La lógica está validada por otras vías; el riesgo residual es de UI.
- **Módulos afectados:** Frontend (página Asistencia y navegación).
- **Prioridad:** Baja.
- **Recomendación futura:** Ejecutar una prueba manual local en navegador siguiendo el checklist de pruebas manuales (carga de ruta, navegación desde el menú, check-in exitoso, asistencia duplicada, valera agotada, valera vencida, visualización de restantes, consola sin errores).

---

## TD-09 — Validación visual en navegador del rediseño UI pendiente

- **ID:** TD-09
- **Título:** Rediseño UI Pro Max no fue validado visualmente en navegador real.
- **Descripción:** La validación del Paso 5 se realizó via `tsc --noEmit`, `vite build` y análisis del CSS compilado. La extensión Chrome no estaba conectada, impidiendo captura de pantalla en runtime. El CSS generado es correcto (tokens success/energy, card-hover, badge-active verde, gradiente sidebar). Falta confirmar render visual real.
- **Riesgo:** Posibles problemas de render o layout no detectados que no afloran en el análisis estático.
- **Impacto:** Bajo. La lógica está validada; el riesgo residual es puramente visual.
- **Módulos afectados:** Dashboard, Sidebar (App.tsx), Badges en Members/Payments/Attendance.
- **Prioridad:** Baja.
- **Recomendación futura:** Abrir `http://localhost:5173` en Chrome y verificar: StatCards, sidebar activo, badges verdes/naranja, hover en renovaciones, barras de progreso h-2.

---

---

## TD-10 — Warning de valera no cubre coexistencia por TD-02/TD-05 ✅ RESUELTO (por transitividad)

- **ID:** TD-10
- **Título:** Warning de cambio a mensual no cubre escenario de dos membresías activas coexistentes.
- **Descripción:** La funcionalidad `valera-a-mensual` desactiva la valera activa (más reciente por `start_date`) al confirmar el cambio. Si un cliente tuviera dos valeras activas coexistentes (escenario previo a la regla de valera única — TD-02), solo se desactiva la más reciente. Adicionalmente, si el cliente tiene una membresía mensual activa coexistiendo con la valera (por TD-05), el `GET /current-membership` puede retornar la mensual en lugar de la valera, y el usuario renovaría sobre la membresía incorrecta.
- **Riesgo:** Escenario posible únicamente con datos históricos inconsistentes; en datos limpios post-regla el riesgo es nulo.
- **Impacto:** Bajo. Limitado a casos heredados de TD-02 y TD-05.
- **Módulos afectados:** `membership_service.py` (`get_active_voucher_warning`, `create_membership`, `renew_membership`), `Members.tsx`.
- **Prioridad:** Baja.
- **Recomendación futura:** Resolver primero TD-02 (auditoría de coexistencias) y TD-05 (desactivar membresía anterior al renovar); con esos resueltos, TD-10 queda cubierto automáticamente.

---

## TD-11 — Botón "Renovar/Crear" sin indicador de carga durante consulta de warning

- **ID:** TD-11
- **Título:** Falta feedback visual mientras se resuelve `GET /active-voucher-warning`.
- **Descripción:** Al hacer clic en "Renovar membresía" o "Crear membresía" con un plan mensual seleccionado, el frontend llama `GET /active-voucher-warning` antes de proceder. Durante esa llamada (tipicamente <200ms en local), el botón no muestra spinner ni estado deshabilitado. En conexiones lentas podría dar la impresión de que el clic no registró.
- **Riesgo:** Cosmético / UX menor. No afecta la integridad del flujo.
- **Impacto:** Bajo. Solo en redes lentas o alta carga del servidor.
- **Módulos afectados:** `frontend/src/pages/Members.tsx` — handlers `handleNewMembership` y `handleRenew`.
- **Prioridad:** Baja.
- **Recomendación futura:** Agregar un estado `checkingWarning` que deshabilite el botón y muestre "Verificando..." durante la consulta de warning, antes de mostrar el banner o proceder.

---

## TD-12 — Dashboard KPI no contabiliza membresías congeladas ✅ RESUELTO

- **ID:** TD-12
- **Estado:** Resuelto.
- **Solución aplicada:** `get_memberships_by_status` ahora distingue `frozen_at IS NOT NULL` y las cuenta en un bucket `frozen` separado. `MembershipStatusSummary` expone el campo `frozen: int`. El Dashboard muestra una StatCard "Congeladas" con el conteo.
- **Archivos modificados:** `dashboard_repository.py`, `dashboard_schemas.py`, `dashboard_service.py`, `frontend/src/types/index.ts`, `frontend/src/pages/Dashboard.tsx`.

---

## TD-13 — Sin límite de ciclos de congelación por membresía ✅ RESUELTO

- **ID:** TD-13
- **Estado:** Resuelto.
- **Solución aplicada:** Columna `freeze_count INTEGER DEFAULT 0` añadida al modelo `Membership` con migración idempotente. El repositorio incrementa `freeze_count` en cada `unfreeze()`. El servicio valida `freeze_count >= MAX_FREEZE_CYCLES (3)` antes de congelar y lanza `FreezeLimitReachedError` (→ HTTP 400).
- **Archivos modificados:** `models/membership.py`, `database/init_db.py`, `repositories/membership_repository.py`, `services/membership_service.py`.

---

## TD-14 — `response_model=dict` en GET /store/products

- **ID:** TD-14
- **Título:** Endpoint de listado de productos sin schema tipado en `response_model`.
- **Descripción:** `GET /store/products` declara `response_model=dict`. FastAPI no valida ni documenta el shape de la respuesta en Swagger. El frontend tipifica correctamente con `ProductListResponse`, pero la documentación automática de la API queda incompleta.
- **Riesgo:** Sin impacto en runtime. Swagger no refleja la estructura real del response.
- **Impacto:** Bajo. Solo afecta documentación de la API.
- **Módulos afectados:** `api/routes/store.py` — endpoint `get_products`.
- **Prioridad:** Baja.
- **Recomendación futura:** Crear schema `ProductListResponse` en `schemas/product.py` (con `total: int` e `items: List[ProductRead]`) y usarlo como `response_model`.

---

## TD-15 — `update_stock` en `ProductRepository` sin uso

- **ID:** TD-15
- **Título:** Método `update_stock` definido pero no utilizado por los servicios.
- **Descripción:** `ProductRepository.update_stock()` fue definido como interfaz limpia para modificar el stock, pero `InventoryService` y `SaleService` modifican `product.stock` directamente sobre el objeto ORM. Si en el futuro se agrega lógica de auditoría o validación dentro de `update_stock`, no se ejecutará.
- **Riesgo:** Divergencia silenciosa si `update_stock` evoluciona. Actualmente sin impacto.
- **Impacto:** Bajo.
- **Módulos afectados:** `repositories/product_repository.py`, `services/inventory_service.py`, `services/sale_service.py`.
- **Prioridad:** Baja.
- **Recomendación futura:** Hacer que los servicios llamen `repo.update_stock()` en lugar de mutar el atributo directamente, o eliminar el método si se decide mantener el patrón de mutación directa.

---

## TD-16 — Trazabilidad de anulación/reposición solo por texto libre

- **ID:** TD-16
- **Título:** Los movimientos de reposición al anular una venta no referencian estructuralmente al movimiento `sale` original.
- **Descripción:** Al anular una venta, `cancel_sale` crea movimientos de tipo `adjustment` con nota `"Anulacion venta #ID"`. No existe campo que vincule el ajuste de reposición con el movimiento `sale` correspondiente. La trazabilidad depende de parsear el texto de la nota.
- **Riesgo:** Reportes de trazabilidad exacta en Fases B/C deberán parsear texto en lugar de hacer JOIN por ID. Mayor fragilidad ante cambios en el formato de la nota.
- **Impacto:** Bajo en Fase A. Medio en Fase C (reportes).
- **Módulos afectados:** `services/sale_service.py` (`cancel_sale`), `models/inventory.py`.
- **Prioridad:** Baja.
- **Recomendación futura:** Agregar columna `cancelled_movement_id` (FK nullable a `inventory_movements`) en `InventoryMovement`, o un campo `reversal_of_sale_id` distinto de `sale_id`, para vincular estructuralmente la reposición con la venta anulada.

---

## TD-17 — Eliminación de producto no restaura stock si la venta tenía descuento

- **ID:** TD-17
- **Título:** Al eliminar un producto con ventas, el stock resultante puede quedar inconsistente con el historial.
- **Descripción:** `delete_product` elimina los `sale_items` y las ventas vacías sin reponer el stock descontado por esas ventas. El stock actual del producto ya refleja esas salidas, pero al eliminar el producto también se pierde el historial que las justificaba. No hay impacto en runtime porque el producto desaparece, pero si en el futuro se agrega soft-delete o archivado, el stock final quedaría sin respaldo en movimientos.
- **Riesgo:** Bajo. Solo relevante si se introduce soft-delete de productos en el futuro.
- **Impacto:** Bajo.
- **Módulos afectados:** `services/product_service.py` (`delete_product`), `repositories/sale_repository.py`.
- **Prioridad:** Baja.
- **Recomendación futura:** Si se introduce soft-delete, registrar un movimiento de ajuste que lleve el stock a 0 antes de archivar, para que el historial quede completo.

---

## TD-18 — Ajuste de stock desde formulario de edición no valida stock negativo resultante

- **ID:** TD-18
- **Título:** Editar stock a un valor menor que las ventas pendientes podría dejar stock negativo.
- **Descripción:** Al editar un producto y reducir el stock actual, el frontend calcula el `diff` y llama `registerAdjustment`. El servicio valida que el resultado no sea negativo (`stock_after < 0`), pero ese error llega al usuario como mensaje genérico de ajuste, no como validación del campo. Si el usuario escribe `0` en el campo de stock pero hay ventas en curso que ya descontaron unidades, el error podría ser confuso.
- **Riesgo:** Bajo. El backend rechaza correctamente; solo es un problema de UX de error.
- **Impacto:** Bajo.
- **Módulos afectados:** Frontend `ProductForm` en `Store.tsx`, `services/inventory_service.py`.
- **Prioridad:** Baja.
- **Recomendación futura:** Mostrar el stock actual como referencia no editable y el campo de ajuste como delta (`+N` / `-N`), igual que en el modal de inventario, para evitar confusión entre "stock absoluto" y "cantidad de ajuste".

---

## TD-19 — Columna `sales.member_id` legado en base de datos

- **ID:** TD-19
- **Título:** Columna `member_id` existe en tabla `sales` pero ya no forma parte del ORM.
- **Descripción:** En la Fase B se eliminó `member_id` del modelo ORM `Sale` para usar `customer_id` como relación principal. La columna sigue existiendo físicamente en SQLite (no es posible DROP COLUMN en versiones <3.35 sin recrear la tabla). SQLAlchemy la ignora, pero ocupa espacio y puede confundir inspecciones directas de la BD.
- **Riesgo:** Bajo. La migración histórica ya leyó los valores de `member_id` para crear los `Customer` correspondientes. La columna es desde ahora inerte.
- **Impacto:** Bajo. Solo espacio y claridad en inspección directa de BD.
- **Módulos afectados:** `backend/gym.db` — tabla `sales`.
- **Prioridad:** Baja.
- **Recomendación futura:** Si se migra a PostgreSQL o se hace una recreación completa de la BD, omitir `member_id` de la nueva definición de `sales`.

---

## TD-20 — `purge_orphaned_cancelled` (botón manual) itera en Python en lugar de SQL puro

- **ID:** TD-20
- **Título:** `SaleRepository.purge_orphaned_cancelled` usa iteración Python (load + delete por registro) en lugar de DELETE SQL en bloque.
- **Descripción:** La función carga los registros huérfanos con `.all()` y luego llama `delete_sale_cascade` para cada uno. Funciona correctamente para el volumen actual (~100 clientes), pero es ineficiente si hubiera muchas ventas canceladas acumuladas.
- **Riesgo:** Bajo. Para el volumen del negocio no representa un problema real.
- **Impacto:** Bajo. Solo rendimiento en escenario hipotético de muchas ventas canceladas acumuladas.
- **Módulos afectados:** `backend/app/repositories/sale_repository.py` → `purge_orphaned_cancelled`.
- **Prioridad:** Baja.
- **Recomendación futura:** Reemplazar por DELETE SQL en bloque usando la misma estrategia de subquery estática que usa `_purge_orphaned_cancelled_sales` en `init_db.py`.

---

## TD-21 — FK `credit_payments.sale_id` sin CASCADE DELETE + reutilización de IDs en SQLite ✅ RESUELTO

- **ID:** TD-21
- **Estado:** Resuelto.
- **Solución aplicada:**
  1. `delete_sale_cascade` ahora elimina `credit_payments` explícitamente antes de borrar la venta.
  2. `delete_empty_sales` resuelve los IDs a eliminar en Python y limpia sus `credit_payments` antes del DELETE en bloque.
  3. `_purge_orphaned_cancelled_sales` en `init_db.py` elimina `credit_payments` antes de las ventas.
  4. Nueva función `_purge_orphaned_credit_payments()` en `init_db.py` (ejecutada en `_run_migrations`): limpia (a) credit_payments sin sale_id válido, y (b) credit_payments en ventas `payment_type='cash'` (invariante de negocio: ventas cash nunca generan abonos). Esta segunda condición cubre el escenario de reutilización de IDs por SQLite.
- **Archivos modificados:** `repositories/sale_repository.py`, `database/init_db.py`.

---

## TD-22 — `_STATE_PRIORITY` definida solo en `dashboard_repository.py`

- **ID:** TD-22
- **Título:** Constante de prioridad de estados no está en un módulo compartido.
- **Descripción:** `_STATE_PRIORITY = {"active": 5, "expiring": 4, "exhausted": 3, "frozen": 2, "expired": 1}` es privada al módulo `dashboard_repository.py` y la comparten los 3 métodos de ese mismo archivo. Si otro servicio o repositorio necesitara aplicar la misma lógica Best State Wins, debería duplicar la constante o importar desde un módulo de dominio.
- **Riesgo:** Duplicación silenciosa si futuras funcionalidades (ej. notificaciones, exportación) necesitan clasificar membresías.
- **Impacto:** Bajo. Actualmente el único consumidor es `DashboardRepository`.
- **Módulos afectados:** `repositories/dashboard_repository.py`.
- **Prioridad:** Baja.
- **Recomendación futura:** Extraer a `app/domain/membership_states.py` o similar si se detecta un segundo consumidor.

---

## TD-23 — `set_membership_active` carga el plan dos veces en el path de activación

- **ID:** TD-23
- **Título:** Doble llamada a `get_plan_by_id` en `set_membership_active(True)`.
- **Descripción:** Cuando `is_active=True`, el método carga el plan para verificar `plan_type` en la guardia y luego lo vuelve a cargar dentro de `_enrich_membership`. Son dos SELECT por PK en el mismo request.
- **Riesgo:** Ninguno en el volumen actual. Mínima ineficiencia.
- **Impacto:** Bajo. Solo afecta rendimiento en escenario hipotético de alta concurrencia.
- **Módulos afectados:** `services/membership_service.py` → `set_membership_active`.
- **Prioridad:** Baja.
- **Recomendación futura:** Extraer la carga del plan a una variable local antes de la guardia y pasarla a `_enrich_membership`.

---

## TD-24 — Modelo `Membership` sin columna `updated_at`

- **ID:** TD-24
- **Título:** Ausencia de auditoría temporal en membresías.
- **Descripción:** El modelo `Membership` no tiene campo `updated_at`. Durante el análisis forense del bug `fix-dashboard-expiring` fue imposible determinar exactamente cuándo las membresías duplicadas fueron desactivadas. La trazabilidad dependió de inferencia por patrones de IDs y fechas de creación.
- **Riesgo:** Diagnóstico más difícil en incidentes futuros que involucren cambios de estado de membresías.
- **Impacto:** Bajo. No afecta funcionalidad; solo observabilidad.
- **Módulos afectados:** `models/membership.py`, migración requerida (`ALTER TABLE memberships ADD COLUMN updated_at`).
- **Prioridad:** Baja.
- **Recomendación futura:** Agregar `updated_at = Column(DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)` con migración idempotente en `init_db.py`.

---

## TD-25 — Borrado de email desde UI no alcanzable con normalización actual del frontend

- **ID:** TD-25
- **Título:** El frontend no puede enviar `email: null` para borrar un email existente.
- **Descripción:** El contrato backend está completo: `email: null` o `email: ""` → sets NULL en BD. Sin embargo, el frontend normaliza campos vacíos con `?.trim() || undefined`, lo que convierte `""` en `undefined` (campo omitido en JSON). Esto significa que si el operador borra el campo email y guarda, el JSON no incluye `email`, y el backend aplica "no change". El backend está correcto; el frontend no expone el "delete" del email.
- **Riesgo:** El operador no puede borrar un email ya registrado desde la UI. Puede reemplazarlo por otro valor válido, pero no dejarlo vacío.
- **Impacto:** Bajo. El backend ya soporta la operación; solo falta exposición en frontend.
- **Módulos afectados:** `frontend/src/components/MemberInfo.tsx` (handleSave — email vacío → omitido en lugar de null).
- **Prioridad:** Baja.
- **Recomendación futura:** Distinguir en `MemberInfo` entre "campo vacío" (enviar `email: null`) y "campo no tocado" (omitir). Una solución simple: si el email original existía y el campo queda vacío al guardar, enviar explícitamente `email: null`.

---

## Resumen de prioridades

| ID | Título | Prioridad |
|----|--------|-----------|
| TD-01 | Valeras finalizadas no aparecen inactivas en Dashboard/current-membership | ~~Media~~ **RESUELTO** |
| TD-02 | Coexistencia de valeras preexistentes en datos antiguos | ~~Media~~ **RESUELTO** |
| TD-03 | Cédula no obligatoria pese a ser requerida para check-in | Media |
| TD-04 | UTC en asistencias diarias: `check_in_date` sigue usando fecha UTC (Plan Día y alertas ya corregidos) | Media |
| TD-05 | Renovación no desactiva la membresía anterior | ~~Media~~ **RESUELTO** |
| TD-06 | Visualización de valera solo en la página de Asistencia | Baja |
| TD-07 | `Navbar.tsx` es código muerto | Baja |
| TD-08 | Validación e2e en navegador no concluida | Baja |
| TD-09 | Rediseño UI Pro Max sin validación visual en navegador real | Baja |
| TD-10 | Warning de valera no cubre coexistencia por TD-02/TD-05 | ~~Baja~~ **RESUELTO** |
| TD-11 | Botón Renovar/Crear sin feedback durante consulta de warning | Baja |
| TD-12 | Dashboard KPI no contabiliza membresías congeladas | ~~Media~~ **RESUELTO** |
| TD-13 | Sin límite de ciclos de congelación por membresía | ~~Baja~~ **RESUELTO** |
| TD-14 | `response_model=dict` en GET /store/products | Baja |
| TD-15 | `update_stock` en repo sin uso | Baja |
| TD-16 | Trazabilidad anulación/reposición solo por texto libre | Baja |
| TD-17 | Eliminación de producto no restaura stock del historial (relevante si soft-delete futuro) | Baja |
| TD-18 | Ajuste de stock desde edición de producto sin validación UX de rango negativo | Baja |
| TD-19 | Columna `sales.member_id` legado en BD, ignorada por ORM | Baja |
| TD-20 | `purge_orphaned_cancelled` usa iteración Python en lugar de DELETE SQL en bloque | Baja |
| TD-21 | FK `credit_payments.sale_id` sin CASCADE DELETE + reutilización IDs SQLite | ~~Media~~ **RESUELTO** |
| TD-22 | `_STATE_PRIORITY` definida solo en `dashboard_repository.py`, no en módulo compartido | Baja |
| TD-23 | `set_membership_active` carga el plan dos veces en el path de activación | Baja |
| TD-24 | Modelo `Membership` sin columna `updated_at` (sin trazabilidad de cambios de estado) | Baja |
| TD-25 | Borrado de email desde formulario no persistido (normalize vacío a undefined, BD no se limpia) | Baja |
| TD-26 | Backup automático de volumen SQLite no implementado | ~~Media~~ **RESUELTO** |
| TD-27 | `import os` sin uso en `backup_service.py` | Baja |
| TD-28 | `backup_type` en `create_backup` acepta strings arbitrarios sin validación de enum | Baja |
| TD-29 | Límites de retención hardcodeados en `BackupModal` (30/10) en lugar de leerlos del backend | Baja |
| TD-30 | `SECRET_KEY` vacía no bloquea arranque — SEC-009 | ~~Alta~~ **RESUELTO** |
| TD-31 | Concurrencia scheduler + POST /run puede generar correo duplicado (ventana de segundos) | Baja |
| TD-32 | `page_size` sin validación de rango en GET /notifications/history | Baja |
| TD-33 | Scheduler sin healthcheck Docker — fallos solo visibles en logs del contenedor | Baja |
| TD-34 | Contenedor corre como root — SEC-007 (F1) | ~~Alta~~ **RESUELTO** |
| TD-35 | `cryptography 41.0.7` + deps desactualizadas con CVEs — SEC-008 (F1) | Alta |
| TD-36 | Docs OpenAPI expuestas en producción — SEC-010 (F1) | Media |
| TD-37 | `debug=True` por defecto en `config.py` — SEC-011 (F1) | ~~Media~~ **RESUELTO** |
| TD-38 | CORS permisivo: `allow_credentials` + métodos/headers wildcard — SEC-012 (F1) | Media |
| TD-39 | PII en logs 422: `exc.errors()` incluye `input` del cliente — SEC-013 (F1) | ~~Media~~ **RESUELTO** |
| TD-40 | SQLite y backups sin cifrar en reposo — SEC-014 (diferido F4) | Media |
| TD-41 | Sin cabeceras de seguridad HTTP en nginx — SEC-015 (F1) | Media |
| TD-42 | Sin rate limiting en ningún endpoint — SEC-016 (diferido F5) | Media |
| TD-43 | `str(e)` expuesto al cliente en errores de negocio — SEC-017 (F1) | Media |
| TD-44 | Sin `TrustedHostMiddleware` — SEC-019 (diferido F5) | Baja |

**Resueltos en fixes-post-tienda-b:**
- `UNIQUE(member_id, check_in_date)` en attendances → migrada a `(membership_id, check_in_date)` ✅
- Ventas CANCELLED huérfanas (customer_id NULL o FK rota) → purge_orphaned cubre ambos casos ✅
- Eliminación de cliente bloqueada por ventas CANCELLED → has_active_sales() excluye CANCELLED ✅

**Resueltos en fix-bug (2026-06-10) — modelo híbrido de clasificación y corrección Best State Wins client-oriented:**
- `get_memberships_by_status()`: Best State Wins — un cliente con múltiples membresías activas simultáneas (Opción D) clasifica por el mejor estado disponible (`active > expiring > exhausted > frozen > expired`).
- `get_membership_alerts()`: reescrito con unidad de análisis por **cliente**. Supresión: cliente con ANY membresía `state='active'` (>5 días) queda fuera de todos los buckets. `best_state='expired'` → Vencidas (membresía más recientemente vencida). `best_state='expiring'` → Hoy/3días/7días (membresía que vence más pronto). `best_state='exhausted'|'frozen'` → suprimido. Filtro `plan_type != 'voucher'` eliminado; todos los tipos incluidos. Corrige bug donde clientes con Plan Día vencido + mensual activo aparecían en Vencidas.
- `get_members_by_plan()`: sin deduplicación global — cada membresía contribuye al conteo de su plan; un cliente con mensual + Plan Día aparece en ambas filas; tabla renombrada a "Membresías por plan".
- Constante `_STATE_PRIORITY` extraída a nivel de módulo en `dashboard_repository.py` — compartida por los 3 métodos.

**Resueltos en fix-dashboard-expiring (2026-06-11):**
- Membresías no-voucher duplicadas (`is_active=True`) suprimían clientes de alertas y StatCard "Por vencer" → cleanup histórico en startup + `create_membership` con deactivación atómica + guardia en `set_membership_active` ✅

**Resueltos en sesión TD-prioridad-media (2026-06-10):**
- TD-05: `renew_membership` desactiva membresía anterior atómicamente (`deactivate_no_commit` + commit único) ✅
- TD-02: `_deactivate_duplicate_active_vouchers` en startup corrige coexistencias históricas de valeras ✅
- TD-10: resuelto por transitividad (TD-05 + TD-02) ✅
- TD-01: estado `exhausted` para valeras agotadas en `_enrich_membership` + subquery correlacionada en Dashboard ✅

**Resueltos en F1 Bloque A — Endurecimiento del empaquetado (`f1-bloque-a-hardening`, 2026-06-15):**
Ciclo completo Paso 1→7. Estado técnico: **Implementado · Probado · Auditado · Aprobado** (Paso 5 PASS con riesgos operativos · Paso 5.5 PASS sin impacto histórico · Paso 6 auditoría APROBADA). **Sin defectos abiertos.**
- TD-30 (SEC-009): validación de arranque de `SECRET_KEY` (obligatoria en prod, opcional en dev) centralizada en `Settings` ✅
- TD-34 (SEC-007): usuario no-root `gymuser` + entrypoint con reconciliación idempotente de permisos del volumen ✅
- TD-37 (SEC-011): `debug=False` por defecto ✅
- TD-39 (SEC-013): handler 422 saneado (sin `input`/PII) ✅
- SEC-005 (sin TD directo): bind parametrizado `${BIND_ADDR:-127.0.0.1}` con default loopback ✅
- **Actividad operativa de release pendiente (NO es deuda técnica):** rebuild + recreate de los contenedores en los entornos de producción actuales para materializar el endurecimiento (los contenedores en marcha siguen en las imágenes previas).

---

## TD-27 — `import os` sin uso en `backup_service.py`

- **ID:** TD-27
- **Estado:** Abierto.
- **Descripción:** `import os` en la línea 4 de `backup_service.py` no se utiliza en ningún método del servicio.
- **Riesgo:** Ninguno funcional. Lint warning cosmético.
- **Módulos afectados:** `backend/app/services/backup_service.py`.
- **Prioridad:** Baja.
- **Recomendación futura:** Eliminar la línea.

---

## TD-28 — `backup_type` en `create_backup` acepta strings arbitrarios

- **ID:** TD-28
- **Estado:** Abierto.
- **Descripción:** El parámetro `backup_type` de `BackupService.create_backup()` es un `str` libre. Un valor distinto de `'automatic'` o `'manual'` escribe en `manual/` sin validación explícita (el `else` del folder selection es el default).
- **Riesgo:** Ninguno en producción — el método solo se invoca desde rutas y scheduler controlados. Riesgo futuro si se expone a input externo.
- **Módulos afectados:** `backend/app/services/backup_service.py`.
- **Prioridad:** Baja.
- **Recomendación futura:** Usar `Literal['automatic', 'manual']` como tipo del parámetro o agregar validación explícita.

---

## TD-30 — SECRET_KEY vacía no bloquea arranque del sistema · SEC-009

- **ID:** TD-30 · **Hallazgo F0:** SEC-009 (Alta)
- **Estado:** ✅ RESUELTO (F1 Bloque A · `f1-bloque-a-hardening`). Validado en Paso 5 (PASS con riesgos operativos) y Paso 5.5 (sin impacto histórico); auditoría Paso 6 APROBADA. Sin defectos abiertos.
- **Solución aplicada:** `model_validator(mode="after")` en `Settings` (`config.py`) aborta el arranque si `secret_key` está vacía en producción (`debug=False`), con mensaje accionable que indica cómo generar la clave; en desarrollo (`debug=True`) se permite vacía con degradación. Corre para API y scheduler (ambos importan `settings`). `debug` default pasó a `False`. `.env.example` documenta la clave como obligatoria y **única por instalación**.
- **Descripción:** `secret_key: str = ""` en `core/config.py` — vacío por defecto. El sistema arranca normalmente; el error solo aparece al intentar usar SMTP (`encrypt`/`decrypt` lanzan `ValueError`). Un operador puede arrancar en producción sin `SECRET_KEY` en `.env` sin advertencia visible.
- **Riesgo:** Alto en producción sin `.env` bien configurado. Con `.env` correcto el riesgo operativo es bajo, pero la ausencia de validación en startup permite detectar el error solo en uso, no en arranque.
- **Módulos afectados:** `backend/app/services/crypto_service.py`, `backend/app/core/config.py`.
- **Prioridad:** Alta (ajustada desde Baja — ver F0 audit SEC-009).
- **Recomendación futura (F1):** Validación en startup: si `SECRET_KEY` vacía y notificaciones habilitadas → log CRITICAL o arranque abortado. Documentar en `.env.example`.

---

## TD-31 — Concurrencia scheduler + POST /run puede generar correo duplicado

- **ID:** TD-31
- **Estado:** Abierto.
- **Descripción:** El scheduler ejecuta `run_evaluation_cycle()` a las 08:00 AM. Si el operador presiona "Ejecutar ahora" en el Dashboard simultáneamente, ambas instancias cargan `sent_pairs` antes de que la otra haya persistido logs. La deduplicación en memoria (`sent_pairs.add(...)`) es local a cada instancia: un mismo cliente podría recibir el correo dos veces en el mismo ciclo.
- **Riesgo:** Bajo. Ventana de concurrencia de segundos; solo se activa si el operador ejecuta manualmente exactamente a las 08:00.
- **Impacto:** Un correo duplicado a uno o más clientes en una ejecución puntual.
- **Módulos afectados:** `backend/app/services/notification_service.py`, `backend/scheduler/main.py`, `backend/app/api/routes/notifications.py`.
- **Prioridad:** Baja.
- **Recomendación futura:** Añadir campo `is_running BOOLEAN DEFAULT FALSE` en `notification_settings` + UPDATE atómico antes del ciclo (advisory lock de SQLite) para serializar ejecuciones concurrentes.

---

## TD-32 — page_size sin validación de rango en GET /notifications/history

- **ID:** TD-32
- **Estado:** Abierto.
- **Descripción:** El parámetro `page_size: int = 20` no usa `Query(ge=1, le=100)` a nivel de FastAPI. El repositorio aplica `min(page_size, 100)` correctamente, pero un valor ≤ 0 llega al SQL como `LIMIT 0` (SQLite puede comportarse de forma inconsistente).
- **Riesgo:** Bajo. Sin autenticación externa, solo uso incorrecto interno.
- **Impacto:** Respuesta vacía o comportamiento inesperado ante `?page_size=0`.
- **Módulos afectados:** `backend/app/api/routes/notifications.py` → `get_history`.
- **Prioridad:** Baja.
- **Recomendación futura:** `page_size: int = Query(default=20, ge=1, le=100)` en el endpoint.

---

## TD-33 — Scheduler sin healthcheck Docker

- **ID:** TD-33
- **Estado:** Abierto.
- **Descripción:** El servicio `scheduler` en `docker-compose.yml` no tiene `healthcheck`. Si el proceso crashea y reinicia en bucle, no hay señal observable más allá de los logs del contenedor.
- **Riesgo:** Bajo. El scheduler tiene `try/except` en cada job; un fallo de APScheduler es visible en `docker compose logs scheduler`.
- **Impacto:** Bajo. Sin observabilidad automática del estado del scheduler.
- **Módulos afectados:** `docker-compose.yml`, `backend/scheduler/main.py`.
- **Prioridad:** Baja.
- **Recomendación futura:** Añadir endpoint `/scheduler/health` que devuelva última ejecución de cada job, o escribir un archivo de heartbeat en cada ejecución exitosa verificable por el healthcheck de Docker.

---

## TD-34 — Contenedor backend/scheduler corre como root · SEC-007

- **ID:** TD-34 · **Hallazgo F0:** SEC-007 (Alta)
- **Estado:** ✅ RESUELTO (F1 Bloque A · `f1-bloque-a-hardening`). Validado en Paso 5 (usuario real `gymuser`/10001 vía `docker top`; escenarios fresco y upgrade root-owned) y Paso 5.5 (chown = solo ownership, sin tocar contenido); auditoría Paso 6 APROBADA. Sin defectos abiertos.
- **Solución aplicada:** `backend/Dockerfile` crea usuario no-root `gymuser` (UID/GID 10001) e instala `gosu`. Nuevo `backend/docker-entrypoint.sh` arranca como root, hace `chown -R` idempotente de `/app/data` (R1: cubre upgrade sobre volumen existente con archivos root) y baja privilegios con `gosu gymuser`. Aplica por igual a backend y scheduler (comparten imagen). `.gitattributes` fuerza LF en `*.sh`.
- **Descripción:** `backend/Dockerfile` no incluye directiva `USER`. El proceso corre como root dentro del contenedor. Igual para el servicio `scheduler`. Una vulnerabilidad de ejecución en la app otorga root en el contenedor, ampliando el radio de daño a volúmenes y red de Docker.
- **Módulos afectados:** `backend/Dockerfile`, `docker-compose.yml` (servicio `scheduler`).
- **Prioridad:** Alta.
- **Recomendación futura (F1):** `RUN adduser --disabled-password gymuser && USER gymuser` en el Dockerfile (backend y scheduler).

---

## TD-35 — Dependencias desactualizadas con CVEs · SEC-008

- **ID:** TD-35 · **Hallazgo F0:** SEC-008 (Alta)
- **Estado:** Abierto — pendiente Human Gate F0.
- **Descripción:** `cryptography==41.0.7` (cifra `smtp_password`) tiene CVEs conocidas corregidas en ≥42.x. FastAPI 0.104.1, uvicorn 0.24.0, SQLAlchemy 2.0.23, pydantic 2.5.0, apscheduler 3.10.4: versiones de fin de 2023 con correcciones de seguridad acumuladas.
- **Módulos afectados:** `backend/requirements.txt`.
- **Prioridad:** Alta.
- **Recomendación futura (F1):** Actualizar a versiones estables actuales + adoptar `pip-audit` en el flujo de desarrollo.

---

## TD-36 — Docs OpenAPI expuestas en producción · SEC-010

- **ID:** TD-36 · **Hallazgo F0:** SEC-010 (Media)
- **Estado:** Abierto — pendiente Human Gate F0.
- **Descripción:** `/docs`, `/redoc` y `/openapi.json` están activos en todo momento. En producción exponen toda la superficie de la API sin necesidad de ingeniería inversa.
- **Módulos afectados:** `backend/app/main.py`.
- **Prioridad:** Media.
- **Recomendación futura (F1):** `docs_url=None, redoc_url=None` cuando `settings.debug=False`.

---

## TD-37 — debug=True por defecto en config · SEC-011

- **ID:** TD-37 · **Hallazgo F0:** SEC-011 (Media)
- **Estado:** ✅ RESUELTO (F1 Bloque A · `f1-bloque-a-hardening`). Validado en Paso 5 (prod `debug=False`, dev `debug=True`); auditoría Paso 6 APROBADA. Sin defectos abiertos.
- **Solución aplicada:** `debug: bool = False` por defecto en `config.py`. Producción es segura por defecto; desarrollo activa `DEBUG=true` explícitamente en su `.env`. `.env.example` ya traía `DEBUG=false`.
- **Descripción:** `debug: bool = True` en `core/config.py`. Sin `.env` correctamente configurado, el sistema arranca en modo debug (trazas detalladas, hot-reload, `/docs` activos).
- **Módulos afectados:** `backend/app/core/config.py`, `backend/app/main.py`.
- **Prioridad:** Media.
- **Recomendación futura (F1):** Cambiar default a `False`; `True` solo en `.env` de desarrollo explícito.

---

## TD-38 — CORS permisivo: allow_credentials + métodos/headers wildcard · SEC-012

- **ID:** TD-38 · **Hallazgo F0:** SEC-012 (Media)
- **Estado:** Abierto — pendiente Human Gate F0.
- **Descripción:** `CORSMiddleware` con `allow_credentials=True` + `allow_methods=["*"]` + `allow_headers=["*"]`. Cuando se implemente auth por cookie/sesión (F2), este CORS puede habilitar ataques CSRF cross-origin.
- **Módulos afectados:** `backend/app/main.py`.
- **Prioridad:** Media.
- **Recomendación futura (F1):** Listar orígenes, métodos y headers explícitamente; `allow_credentials=False` si se usa JWT en header (no cookie).

---

## TD-39 — PII en logs 422: input del cliente registrado en logger · SEC-013

- **ID:** TD-39 · **Hallazgo F0:** SEC-013 (Media)
- **Estado:** ✅ RESUELTO (F1 Bloque A · `f1-bloque-a-hardening`). Validado en Paso 5 (log 422 con `loc/type/msg`, sin `input` ni PII); auditoría Paso 6 APROBADA. Sin defectos abiertos.
- **Solución aplicada:** el handler `RequestValidationError` en `main.py` construye una lista saneada `{loc, type, msg}` por error y descarta `input`/`ctx` antes de loguear (nivel `warning`) y de responder. Se conserva el diagnóstico (campo + tipo + motivo) sin registrar el valor enviado por el cliente.
- **Descripción:** El handler `RequestValidationError` en `main.py` llama `logger.warning(exc.errors())`. Pydantic incluye el campo `input` con el valor enviado por el cliente, que puede contener nombre, cédula, email u otros PII.
- **Módulos afectados:** `backend/app/main.py` — handler `RequestValidationError`.
- **Prioridad:** Media.
- **Recomendación futura (F1):** Filtrar el campo `input` de cada error antes de loguear: `[{k: v for k, v in e.items() if k != "input"} for e in exc.errors()]`.

---

## TD-40 — SQLite y backups sin cifrar en reposo · SEC-014

- **ID:** TD-40 · **Hallazgo F0:** SEC-014 (Media)
- **Estado:** Abierto — diferido a F4/posterior.
- **Descripción:** `gym.db` y los archivos en `backups/` contienen PII + datos financieros + datos de salud sin cifrado en disco. Acceso al volumen Docker o al sistema de archivos del host expone toda la BD.
- **Módulos afectados:** Volumen `db-data`, `backend/app/services/backup_service.py`.
- **Prioridad:** Media.
- **Recomendación futura (F4):** Evaluar SQLCipher o cifrado del volumen a nivel de host. Prioritario si el servidor de producción es compartido o no es de confianza exclusiva.

---

## TD-41 — Sin cabeceras de seguridad HTTP en nginx · SEC-015

- **ID:** TD-41 · **Hallazgo F0:** SEC-015 (Media)
- **Estado:** Abierto — pendiente Human Gate F0.
- **Descripción:** `nginx.conf` no incluye `Strict-Transport-Security`, `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`, `Referrer-Policy`. Expone el frontend a clickjacking, MIME-sniffing y ataques de navegador.
- **Módulos afectados:** `frontend/nginx.conf`.
- **Prioridad:** Media.
- **Recomendación futura (F1):** Añadir bloque `add_header` con las cabeceras estándar. `HSTS` solo cuando TLS esté activo (F5).

---

## TD-42 — Sin rate limiting en ningún endpoint · SEC-016

- **ID:** TD-42 · **Hallazgo F0:** SEC-016 (Media)
- **Estado:** Abierto — diferido a F5.
- **Descripción:** No existe throttling. Pre-F2: vector de DoS de recursos. Post-F2: fuerza bruta en login queda abierta.
- **Módulos afectados:** `backend/app/main.py`, reverse proxy (pendiente F5).
- **Prioridad:** Media.
- **Recomendación futura (F5):** Rate limiting en el reverse proxy (Nginx/Caddy) + `slowapi` en FastAPI para endpoints de auth.

---

## TD-43 — str(e) expuesto al cliente en errores de negocio · SEC-017

- **ID:** TD-43 · **Hallazgo F0:** SEC-017 (Media)
- **Estado:** Abierto — pendiente Human Gate F0.
- **Descripción:** Múltiples endpoints hacen `raise HTTPException(status_code=400, detail=str(e))` capturando `ValueError`. Puede filtrar rutas internas, nombres de módulos u otros detalles del stack.
- **Módulos afectados:** `api/routes/payments.py`, `store.py`, `members.py` (múltiples handlers `except ValueError`).
- **Prioridad:** Media.
- **Recomendación futura (F1):** Mapear excepciones de dominio a mensajes controlados. `str(e)` solo para excepciones explícitamente diseñadas para el cliente (ej. `DuplicateDocumentError`, `InsufficientStockError`).

---

## TD-44 — Sin TrustedHostMiddleware · SEC-019

- **ID:** TD-44 · **Hallazgo F0:** SEC-019 (Baja)
- **Estado:** Abierto — diferido a F5.
- **Descripción:** FastAPI no valida el header `Host`. En un entorno con reverse proxy o multi-tenant, puede habilitar host-header injection.
- **Módulos afectados:** `backend/app/main.py`.
- **Prioridad:** Baja.
- **Recomendación futura (F5):** `TrustedHostMiddleware` con la lista de hosts permitidos, configurada por despliegue en `.env`.

---

## TD-29 — Límites de retención hardcodeados en `BackupModal`

- **ID:** TD-29
- **Estado:** Abierto.
- **Descripción:** `BackupModal.tsx` muestra `(data.automatic.length/30)` y `(data.manual.length/10)` como literales. Si `settings.max_auto_backups` o `settings.max_manual_backups` cambian en el backend, el label del frontend quedaría desactualizado.
- **Riesgo:** Desinformación visual al operador si se ajustan los límites de retención.
- **Módulos afectados:** `frontend/src/components/BackupModal.tsx`, `backend/app/schemas/backup.py` (requeriría exponer los límites en `BackupListResponse`).
- **Prioridad:** Baja.
- **Recomendación futura:** Añadir `max_auto: int` y `max_manual: int` a `BackupListResponse` y consumirlos en el modal.

---

## TD-45 — Teléfonos placeholder `0000000` en ~20 clientes migrados

- **ID:** TD-45
- **Estado:** Abierto.
- **Descripción:** Durante la migración inicial desde Excel, ~20 clientes no tenían teléfono registrado. Se usó `0000000` como placeholder para cumplir con el campo obligatorio del sistema.
- **Riesgo:** El scheduler de notificaciones podría intentar contactar números inválidos si en el futuro se integra SMS. Actualmente no hay impacto funcional.
- **Módulos afectados:** Tabla `members` — filas con `phone = '0000000'`.
- **Prioridad:** Baja.
- **Recomendación futura:** El operador debe actualizar los teléfonos desde la pestaña Info de cada cliente en la app. No requiere cambio de código.

---

## TD-46 — `_calculate_status` compara `end_date` UTC contra `datetime.utcnow()`

- **ID:** TD-46
- **Estado:** Abierto.
- **Descripción:** `MembershipService._calculate_status` compara `end_date` (almacenado como datetime UTC medianoche) contra `datetime.utcnow()`. En Bogotá (UTC-5), esto provoca que una membresía que vence el día X aparezca como `expired` desde las 19:00 del día X-1 hora local, es decir, ~5 horas antes del vencimiento real percibido por el operador.
- **Riesgo:** El dashboard y el badge de estado muestran `Vencida` el último día de la membresía del cliente, generando falsa alarma operativa y potencialmente bloqueando renovaciones al operador antes de tiempo.
- **Registros afectados:** Todos los clientes cuya membresía vence ese día. Con 50 clientes migrados, ocurre sistemáticamente en el último día de cada membresía.
- **Módulos afectados:** `backend/app/services/membership_service.py` — método `_calculate_status`.
- **Prioridad:** Media.
- **Recomendación futura:** Reemplazar `datetime.utcnow()` por `datetime.utcnow() + BOGOTA_OFFSET` en la comparación. Alternativamente, almacenar `end_date` como medianoche hora Bogotá y comparar contra `datetime.utcnow() + BOGOTA_OFFSET`. Leer `config.BOGOTA_OFFSET` ya disponible en el proyecto.

---

## TD-47 — `docker compose build frontend` puede servir bundle obsoleto (caché de contexto)

- **ID:** TD-47
- **Estado:** Abierto (operativo / infraestructura).
- **Descripción:** En este entorno (Docker Desktop / Windows), `docker compose build frontend` — incluso con `--no-cache` — reutilizó un contexto de build cacheado y compiló código fuente obsoleto, generando siempre el mismo hash de bundle (`index-CsOxx0Cq.js`) pese a cambios reales en `src/`. El navegador recibía la versión vieja y rota.
- **Riesgo:** Desplegar una versión antigua del frontend sin notarlo; los cambios de código no se reflejan en producción.
- **Diagnóstico confirmado:** Compilar montando el código fuente directamente (`docker run --rm -v "<host>/frontend:/app" -w /app node:20-alpine npm run build`) produjo un hash distinto y correcto, probando que el build normal usaba fuente obsoleta.
- **Procedimiento confiable de build (workaround):**
  1. `docker builder prune -f` antes de reconstruir, **o**
  2. compilar por montaje directo y desplegar el `dist/` resultante con `docker cp ./frontend/dist/. aplicacion-gym-frontend-1:/usr/share/nginx/html/`.
  Tras reconstruir la imagen, recrear el contenedor con `docker compose up -d --force-recreate frontend` y verificar el hash servido en `index.html`.
- **Módulos afectados:** Pipeline de build del servicio `frontend` (Docker Compose).
- **Prioridad:** Media.
- **Recomendación futura:** Investigar la causa raíz (sincronización de archivos de Docker Desktop en Windows / caché de BuildKit) o añadir un paso de verificación de hash post-build al procedimiento de despliegue.

---

## TD-26 — Backup automático de volumen SQLite no implementado ✅ RESUELTO

- **ID:** TD-26
- **Estado:** Resuelto.
- **Solución aplicada:** Servicio `scheduler` en Docker Compose ejecuta `sqlite3.backup()` diario a las 02:00 AM. Retención diferenciada 30 automáticos + 10 manuales en carpetas independientes. Backup manual desde Dashboard. `docs/MANUAL_TECNICO.md` actualizado con procedimiento de restauración.
- **Descripción:** La base de datos `gym.db` vive en el volumen Docker `appparagym_db-data`. No existe mecanismo automatizado de backup. Un `docker compose down -v` ejecutado por error destruye los datos de forma permanente e irreversible. El README documenta el procedimiento manual de backup, pero no hay automatización ni salvaguarda técnica.
- **Riesgo:** Pérdida total de datos si el operador ejecuta `docker compose down -v` sin hacer backup previo.
- **Impacto:** Alto en producción si ocurre. Probabilidad baja si el operador sigue el README.
- **Módulos afectados:** Volumen `appparagym_db-data`, operaciones de mantenimiento del sistema.
- **Prioridad:** Media.
- **Why:** La arquitectura SQLite + volumen Docker es correcta para el tamaño del negocio, pero no incluye resiliencia operativa ante errores humanos.
- **How to apply:** Antes de cualquier despliegue en servidor de producción real, implementar un cron de backup diario en el host. El procedimiento está documentado en `README.md` (sección "Respaldo y restauración").
- **Recomendación futura:** Cron en el host que ejecute `docker run --rm -v appparagym_db-data:/data -v /ruta/backups:/backup alpine cp /data/gym.db /backup/gym_FECHA.db` diariamente.
