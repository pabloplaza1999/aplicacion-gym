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

## TD-04 — UTC en restricción de asistencia diaria (check_in_date) ✅ RESUELTO

- **ID:** TD-04
- **Estado:** Resuelto (2026-06-19). Fix en `attendance_service.py`.
- **Solución aplicada:** `check_in` y `get_voucher_status` en `AttendanceService` ahora usan `(datetime.utcnow() + BOGOTA_OFFSET).date()` para calcular la fecha del día local. La comparación de vigencia (`membership.end_date < now`) permanece en UTC — correcto, `end_date` se almacena en UTC. La restricción UNIQUE `(membership_id, check_in_date)` sigue siendo coherente: ahora la fecha almacenada corresponde al día Bogotá, evitando doble check-in en el mismo día calendario local.
- **Archivos modificados:** `backend/app/services/attendance_service.py` — import `BOGOTA_OFFSET`; línea 63 (`today`); línea `attended_today` en `get_voucher_status`.

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

## TD-19 — Columna `sales.member_id` legado en base de datos ✅ RESUELTO

- **ID:** TD-19
- **Estado:** Resuelto — Cliente Único Phase 1 (2026-06-17). `member_id` reincorporada al ORM como FK canónica hacia `Member`. Ver TD-48 para el estado transitorio de `customer_id`.
- **Título (original):** Columna `member_id` existe en tabla `sales` pero ya no forma parte del ORM.
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
| TD-04 | ~~UTC en asistencias diarias: `check_in_date` sigue usando fecha UTC~~ | ✅ RESUELTO |
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
| TD-19 | Columna `sales.member_id` legado en BD, ignorada por ORM | ~~Baja~~ **RESUELTO** |
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
| TD-35 | ~~`cryptography 41.0.7` + deps desactualizadas con CVEs — SEC-008 (F1)~~ | ✅ RESUELTO |
| TD-36 | Docs OpenAPI expuestas en producción — SEC-010 (F1) | ~~Media~~ **RESUELTO** |
| TD-37 | `debug=True` por defecto en `config.py` — SEC-011 (F1) | ~~Media~~ **RESUELTO** |
| TD-38 | CORS permisivo: `allow_credentials` + métodos/headers wildcard — SEC-012 (F1) | ~~Media~~ **RESUELTO** |
| TD-39 | PII en logs 422: `exc.errors()` incluye `input` del cliente — SEC-013 (F1) | ~~Media~~ **RESUELTO** |
| TD-40 | SQLite y backups sin cifrar en reposo — SEC-014 (diferido F4) | Media |
| TD-41 | Sin cabeceras de seguridad HTTP en nginx — SEC-015 (F1) | ~~Media~~ **RESUELTO** |
| TD-42 | ~~Sin rate limiting en ningún endpoint — SEC-016~~ (login: resuelto; otros endpoints: diferido F5) | ✅ RESUELTO (parcial) |
| TD-43 | `str(e)` expuesto al cliente en errores de negocio — SEC-017 (F1) | ~~Media~~ **RESUELTO** |
| TD-44 | Sin `TrustedHostMiddleware` — SEC-019 (diferido F5) | Baja |
| TD-48 | Tabla `customers`, `CustomerService` y `sales.customer_id` mantenidos transitoriamente (Cliente Único Phase 1) | Baja |
| TD-49 | `CreditPayment` definido en `customer.py`, importado por `member_repository.py` — acoplamiento cruzado | Baja |
| TD-50 | ~~`POST /store/sales` acepta `customer_id` (member_id) inexistente — SQLite FK=0, sin validación explícita~~ | ✅ RESUELTO |
| TD-51 | Validación de actualización de producción para Cliente Único Phase 1 — pendiente auditoría sobre datos reales | Alta |
| TD-52 | ~~`get_memberships_by_status` y `get_members_by_plan` en `dashboard_repository.py` usan `datetime.utcnow()` — StatCards y tabla "Membresías por plan" incorrectos después de las 19:00 Bogotá~~ | ✅ RESUELTO |
| TD-53 | ~~`_enrich_membership` usa `datetime.utcnow()` para `days_remaining` — muestra días negativos desde las 19:00 Bogotá en el último día~~ | ✅ RESUELTO |
| TD-54 | ~~`_has_active_valid_voucher` y `get_active_voucher_warning` usan `datetime.utcnow()` — valera considerada inválida 5h antes de expirar localmente~~ | ✅ RESUELTO |
| TD-55 | `corrected_by` no registrado en auditoría de correcciones — diferido a F2 (auth staff) | Baja |
| TD-56 | GET historial de correcciones de membresía no implementado | Baja |
| TD-57 | Índice compuesto `(membership_id, corrected_at)` en `membership_correction_logs` no creado | Baja |
| TD-58 | `passlib[bcrypt]==1.7.4` incompatible con `bcrypt>=5.x` — pin explícito `bcrypt==4.0.1` requerido | Baja |
| TD-59 | `ADMIN_INITIAL_PASSWORD` en `.env` no cambia contraseña activa — requiere `reset_admin.py` explícito | Baja |
| TD-60 | Arranque bloqueado en producción si `.env` no incluye `JWT_SECRET_KEY` y `ADMIN_INITIAL_PASSWORD` antes del update | Media |
| TD-61 | Feature Flags por módulo — diferido a F5 | ~~Baja~~ **RESUELTO (F4-A)** |
| TD-62 | Acceso LAN multi-PC — diferido a Edición Local Plus / F5 | Media |
| TD-63 | Migración de volumen en actualizaciones pre-F3 → F3 (`aplicacion-gym_db-data` → `rhinopower_db-data`) — Mitigado por `upgrade.bat` | Baja |
| TD-64 | ~~`python-jose 3.3.0` (abandonado) bloquea upgrade de `cryptography` a ≥ 42.x~~ | ✅ RESUELTO |
| TD-65 | `GET /api/config/features` es público — revisar autenticación al evolucionar a cloud multi-tenant (F8+) | Baja |

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

**Resueltos en Cliente Único Phase 1 (`cliente-unico`, 2026-06-17):**
- TD-19: `sales.member_id` promovida a columna canónica del ORM; `Sale.member_id` + `Member` son ahora la entidad central de ventas. `sales.customer_id` pasa a ser la columna legado (ver TD-48). ✅

**Resueltos en F1 Bloque B — Endurecimiento de seguridad en runtime (`f1-bloque-b`, 2026-06-18):**
Ciclo completo Paso 1→7. Estado técnico: **Implementado · Probado · Auditado · Aprobado** (Paso 5 PASS · Paso 5.5 PASS sin impacto histórico · Paso 6 auditoría APROBADA con observaciones). DEF-01 (`connect-src`) identificado y resuelto dentro del mismo ciclo.
- TD-36 (SEC-010): OpenAPI docs deshabilitados en producción (`docs_url=None` cuando `debug=False`) ✅
- TD-38 (SEC-012): CORS explícito — métodos, headers y orígenes mínimos; `allow_credentials=False` ✅
- TD-41 (SEC-015): 4 headers de seguridad HTTP en Nginx (server-level, herencia correcta); CSP con Google Fonts y `connect-src localhost:8000` para despliegue single-PC ✅
- TD-43 (SEC-017): `except Exception` en `backup.py` y `notifications.py` retorna mensajes genéricos al cliente; `logger.error` preserva detalle técnico en logs del servidor ✅
- **Consideración de despliegue (no es deuda técnica):** Si el modelo de acceso cambia a LAN o Internet, actualizar `connect-src` en `nginx.conf` y `CORS_ORIGINS` en `.env` con el nuevo origen. No aplica al despliegue actual (single-PC).

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
- **Estado:** ✅ RESUELTO (F3 cierre, 2026-06-19).
- **Solución aplicada:** Actualizadas a versiones estables con correcciones de seguridad acumuladas. `cryptography` mantenida en `41.0.7` por incompatibilidad de `python-jose 3.3.0` con `cryptography ≥ 42.x` (ver TD-64). Los CVEs de `cryptography 41.x` (CVE-2024-26130, CVE-2024-0727) no afectan el app — ambos requieren serialización PKCS12 que nunca ocurre en gestión de gimnasio. CVE-2024-47874 (starlette multipart DoS) no afecta el app — no existen endpoints multipart/file-upload. Todos los smoke tests pasaron tras el upgrade.
- **Versiones actualizadas:** `fastapi: 0.104.1 → 0.115.6` (starlette 0.27.0 → 0.41.3), `uvicorn: 0.24.0 → 0.30.6`, `sqlalchemy: 2.0.23 → 2.0.36`, `pydantic: 2.5.0 → 2.10.6`, `pydantic-settings: 2.1.0 → 2.6.1`.
- **Versiones mantenidas con pin:** `cryptography==41.0.7` (TD-64), `python-jose==3.3.0`, `passlib==1.7.4` (TD-58), `bcrypt==4.0.1` (TD-58), `apscheduler==3.10.4`.
- **Módulos afectados:** `backend/requirements.txt`.
- **Prioridad:** Alta.

---

## TD-36 — Docs OpenAPI expuestas en producción · SEC-010

- **ID:** TD-36 · **Hallazgo F0:** SEC-010 (Media)
- **Estado:** ✅ RESUELTO (F1 Bloque B · `f1-bloque-b`, 2026-06-18). Validado en Paso 5 (PASS · `/docs`/`/redoc`/`/openapi.json` ausentes con `debug=False`); Paso 5.5 (sin impacto en datos); auditoría Paso 6 APROBADA. Sin defectos abiertos.
- **Solución aplicada:** `FastAPI(docs_url="/docs" if settings.debug else None, redoc_url="/redoc" if settings.debug else None, openapi_url="/openapi.json" if settings.debug else None)` en `main.py`. En desarrollo (`debug=True`) las rutas permanecen activas.
- **Descripción:** `/docs`, `/redoc` y `/openapi.json` están activos en todo momento. En producción exponen toda la superficie de la API sin necesidad de ingeniería inversa.
- **Módulos afectados:** `backend/app/main.py`.
- **Prioridad:** Media.

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
- **Estado:** ✅ RESUELTO (F1 Bloque B · `f1-bloque-b`, 2026-06-18). Validado en Paso 5 (PASS · preflight OPTIONS retorna métodos explícitos sin `allow-credentials`; origen no autorizado rechazado); Paso 5.5 (sin impacto en datos); auditoría Paso 6 APROBADA. Sin defectos abiertos.
- **Solución aplicada:** `CORSMiddleware(allow_credentials=False, allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"], allow_headers=["Content-Type"], allow_origins=settings.cors_origins)`. Orígenes tomados de `CORS_ORIGINS` en `.env` (configurados para `http://localhost`/`http://localhost:80` — consistente con despliegue single-PC actual).
- **Descripción:** `CORSMiddleware` con `allow_credentials=True` + `allow_methods=["*"]` + `allow_headers=["*"]`. Cuando se implemente auth por cookie/sesión (F2), este CORS puede habilitar ataques CSRF cross-origin.
- **Módulos afectados:** `backend/app/main.py`.
- **Prioridad:** Media.

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
- **Estado:** ✅ RESUELTO (F1 Bloque B · `f1-bloque-b`, 2026-06-18). Validado en Paso 5 (PASS · 4 headers presentes en los 3 location contexts; DEF-01 `connect-src` identificado y resuelto en el mismo ciclo; Dashboard carga con datos reales vía Nginx); Paso 5.5 (sin impacto en datos); auditoría Paso 6 APROBADA. Sin defectos abiertos.
- **Solución aplicada:** `add_header` a nivel `server {}` en `nginx.conf` con herencia correcta (cache via `expires`, no `add_header`, para no romper child locations). Headers aplicados: `X-Frame-Options "SAMEORIGIN"`, `X-Content-Type-Options "nosniff"`, `Referrer-Policy "strict-origin-when-cross-origin"`, `Content-Security-Policy` (incluye `fonts.googleapis.com`/`gstatic.com` para Google Fonts; `connect-src 'self' http://localhost:8000` consistente con despliegue single-PC actual). HSTS diferido a F5 (TLS pendiente).
- **Nota de despliegue:** Si el modelo de acceso cambia a LAN o Internet, actualizar `connect-src` en `nginx.conf` y `CORS_ORIGINS` en `.env` para incluir el nuevo origen.
- **Descripción:** `nginx.conf` no incluye `Strict-Transport-Security`, `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`, `Referrer-Policy`. Expone el frontend a clickjacking, MIME-sniffing y ataques de navegador.
- **Módulos afectados:** `frontend/nginx.conf`.
- **Prioridad:** Media.

---

## TD-42 — Sin rate limiting en ningún endpoint · SEC-016

- **ID:** TD-42 · **Hallazgo F0:** SEC-016 (Media)
- **Estado:** ✅ RESUELTO para login (F3 cierre, 2026-06-19). Rate limiting en otros endpoints diferido a F5.
- **Solución aplicada:** Middleware custom de sliding-window en `backend/app/main.py`. Sin dependencias externas (stdlib `time` + `collections.defaultdict`). Aplica únicamente a `POST /api/auth/login`. Desactivado cuando `debug=True`. Configuración centralizada en `config.py` (`login_rate_limit_window: int = 60`, `login_rate_limit_max_attempts: int = 20`). Limpieza automática de timestamps expirados en cada request. Respuesta HTTP 429 genérica sin exponer detalles internos. Registrado en `logger.warning` con IP y conteo. La respuesta 429 pasa por `CORSMiddleware` (exterior) — headers CORS presentes. Estado en memoria — reset al reiniciar contenedor (aceptable para Edición Local single-PC). Para LAN multi-PC, Docker masquerade hace que todos los clientes compartan el mismo bucket de IP (diferido TD-62/F5).
- **Tests funcionales (6/6 PASS):** login normal, exceder límite → 429, `/api/health` excluido, GET excluido, `debug=True` desactiva, limpieza de timestamps.
- **Módulos afectados:** `backend/app/main.py`, `backend/app/core/config.py`.
- **Prioridad:** Media.
- **Recomendación futura (F5):** Extender rate limiting a otros endpoints si se abre acceso LAN/Internet. Considerar `TrustedHostMiddleware` + IP real con `X-Forwarded-For` si se agrega reverse proxy externo.

---

## TD-43 — str(e) expuesto al cliente en errores de negocio · SEC-017

- **ID:** TD-43 · **Hallazgo F0:** SEC-017 (Media)
- **Estado:** ✅ RESUELTO (F1 Bloque B · `f1-bloque-b`, 2026-06-18) — scope acotado a `backup.py` y `notifications.py`. Validado en Paso 5 (PASS · mensajes genéricos al cliente; `logger.error` preserva detalle técnico en logs de servidor); Paso 5.5 (sin impacto en datos); auditoría Paso 6 APROBADA. Sin defectos abiertos en los módulos tratados.
- **Solución aplicada:** En `backup.py` y `notifications.py`: `except ValueError` → mensaje controlado al cliente (verificado que todos los `raise ValueError(...)` en los servicios afectados son mensajes de dominio en español); `except Exception` → mensaje genérico HTTP 500 + `logger.error("...: %s", e)` con detalle completo. `import logging` + `logger = logging.getLogger(__name__)` en ambos routes. `payments.py`, `store.py` y `members.py` mantienen `str(e)` para `ValueError` de dominio — patrón válido porque todos sus `raise ValueError` son mensajes explícitamente orientados al operador.
- **Descripción:** Múltiples endpoints hacen `raise HTTPException(status_code=400, detail=str(e))` capturando `ValueError`. Puede filtrar rutas internas, nombres de módulos u otros detalles del stack.
- **Módulos afectados:** `api/routes/payments.py`, `store.py`, `members.py` (múltiples handlers `except ValueError`).
- **Prioridad:** Media.

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

## TD-46 — `_calculate_status` compara `end_date` UTC contra `datetime.utcnow()` ✅ RESUELTO

- **ID:** TD-46
- **Estado:** Resuelto (2026-06-18).
- **Solución aplicada:** `today = datetime.utcnow() + BOGOTA_OFFSET` en `_calculate_status`. `BOGOTA_OFFSET` ya estaba importado desde `app.core.config`. Cambio de 1 línea; sin impacto histórico (cálculo en memoria).
- **Archivos modificados:** `backend/app/services/membership_service.py` — línea 66.

---

## TD-47 — `docker compose build frontend` puede servir bundle obsoleto (caché de contexto)

- **ID:** TD-47
- **Estado:** Abierto (operativo / infraestructura).
- **Descripción:** En este entorno (Docker Desktop / Windows), `docker compose build frontend` — incluso con `--no-cache` — reutilizó un contexto de build cacheado y compiló código fuente obsoleto, generando siempre el mismo hash de bundle (`index-CsOxx0Cq.js`) pese a cambios reales en `src/`. El navegador recibía la versión vieja y rota.
- **Riesgo:** Desplegar una versión antigua del frontend sin notarlo; los cambios de código no se reflejan en producción.
- **Diagnóstico confirmado:** Compilar montando el código fuente directamente (`docker run --rm -v "<host>/frontend:/app" -w /app node:20-alpine npm run build`) produjo un hash distinto y correcto, probando que el build normal usaba fuente obsoleta.
- **Procedimiento confiable de build (workaround):**
  1. `docker builder prune -f` antes de reconstruir, **o**
  2. Build local con `VITE_API_URL` explícita + `docker cp` (ver checklist abajo).
  Tras desplegar, verificar el hash en `index.html` del contenedor y hacer recarga dura en el browser.
- **Módulos afectados:** Pipeline de build del servicio `frontend` (Docker Compose).
- **Prioridad:** Media.
- **Recomendación futura:** Investigar la causa raíz (sincronización de archivos de Docker Desktop en Windows / caché de BuildKit) o añadir un paso de verificación de hash post-build al procedimiento de despliegue.
- **Lecciones aprendidas (incidente 2026-06-18):** tres capas de caché se activaron en el mismo ciclo de despliegue:
  1. **Caché BuildKit (ya documentado):** `docker builder prune -f` + `docker compose build frontend` falló durante `npm ci` (error de red en Docker Desktop). Se escaló a build local.
  2. **Build local sin `VITE_API_URL`:** el build local no hereda variables de `docker-compose.yml`. Sin la variable, Vite embebe `BASE = '/api'` (URL relativa). Nginx no tiene `proxy_pass` para `/api/*` → devuelve `index.html` (SPA fallback) → JSON parse error (`Unexpected token '<'`). Siempre inyectar explícitamente antes del build local: `$env:VITE_API_URL = "http://localhost:8000"`.
  3. **Caché de navegador:** tras `docker cp`, el browser puede seguir sirviendo el bundle anterior. Siempre hacer recarga dura (`Ctrl+Shift+R`) y confirmar en DevTools → Network que las peticiones van a `:8000`.
- **Checklist de despliegue frontend (build local + docker cp):**
  1. `$env:VITE_API_URL = "http://localhost:8000"`
  2. `cd frontend && npm run build`
  3. Verificar: `dist/assets/index-HASH.js` contiene `"localhost:8000"`
  4. `docker cp ./frontend/dist/. aplicacion-gym-frontend-1:/usr/share/nginx/html/`
  5. Verificar: `docker exec aplicacion-gym-frontend-1 sh -c "grep 'index-' /usr/share/nginx/html/index.html"`
  6. Browser: `Ctrl+Shift+R` (recarga dura)
  7. DevTools → Network: confirmar peticiones a `:8000`

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

---

## TD-48 — Tabla `customers`, `CustomerService` y columna `sales.customer_id` mantenidos transitoriamente (Cliente Único Phase 1)

- **ID:** TD-48
- **Título:** Artefactos del modelo antiguo `Customer` retenidos para compatibilidad durante la transición.
- **Descripción:** La iniciativa Cliente Único (Phase 1) migró toda la lógica de ventas a `Sale.member_id` + `Member` como entidad canónica. Sin embargo, se conservan deliberadamente para evitar regresiones en frontend:
  - Tabla `customers` en SQLite (con sus filas existentes).
  - Modelo ORM `Customer` en `models/customer.py`.
  - `CustomerService` en `services/customer_service.py`.
  - Columna `sales.customer_id` (ahora inerte — el backend ya no la escribe ni la lee para lógica nueva).
  - Los endpoints `/store/customers/*` son ahora alias sobre `MemberService`, no sobre `CustomerService`.
- **Riesgo:** La coexistencia genera confusión: `Sale` tiene dos columnas de FK (`member_id` canónica + `customer_id` legado), y `Customer`/`CustomerService` existen aunque no se usen en ningún flujo activo. Un desarrollador podría editar `CustomerService` creyendo que sigue activo.
- **Impacto:** Bajo en runtime. El frontend no necesita cambios (semantic reuse: `SaleCreate.customer_id` contiene un `member_id`, el backend lo mapea internamente). Riesgo medio de confusión para mantenimiento futuro.
- **Módulos afectados:** `backend/gym.db` (tabla `customers`), `models/customer.py`, `services/customer_service.py`, `sales.customer_id` (columna inerte).
- **Prioridad:** Baja.
- **Fase de limpieza:** Cliente Único Phase 2 — una vez el frontend deje de enviar `customer_id` y use `member_id` directamente, eliminar: tabla `customers`, `Customer`, `CustomerService`, columna `sales.customer_id`.
- **Why:** Se optó por diferir la limpieza para evitar regresiones en el frontend sin coordinación de deploy.
- **How to apply:** No modificar `CustomerService` ni la tabla `customers` — son artefactos congelados. Toda la lógica activa de ventas y clientes pasa por `MemberService` y `Sale.member_id`.

---

## TD-51 — Validación de actualización de producción para Cliente Único Phase 1

- **ID:** TD-51
- **Título:** El despliegue de Cliente Único Phase 1 en la instalación productiva del gimnasio no ha sido validado sobre los datos reales.
- **Descripción:** Cliente Único Phase 1 fue validada en el entorno de desarrollo (base de datos de desarrollo, 0 ventas, 0 clientes en `customers`). La instalación productiva puede tener un estado diferente. Antes del deploy en producción se deben ejecutar las validaciones V1–V4 definidas en el Paso 5.5 y verificar que no hay clientes solo-tienda con ventas asociadas (riesgo de pérdida de atribución).
- **Riesgo:** Alto si se despliega sin auditoría previa y existen ventas con `customer_id` de clientes sin `member_id`.
- **Impacto:** Ventas de clientes solo-tienda quedarían sin atribución (`customer_name=null`) en cartera y reportes post-deploy.
- **Módulos afectados:** `_migrate_sales_to_member_id()` en `init_db.py`, tabla `sales`, tabla `customers`.
- **Prioridad:** Alta — bloquea el deploy en producción.
- **Checklist pre-deploy (Paso 5.5):**
  1. `SELECT COUNT(*) FROM sales WHERE customer_id IS NOT NULL AND member_id IS NULL` — cantidad a migrar.
  2. `SELECT COUNT(*) FROM customers WHERE member_id IS NULL` — clientes solo-tienda (si > 0, evaluar impacto).
  3. `SELECT COUNT(*) FROM sales WHERE status='CANCELLED' AND ...` — ventas a purgar.
  4. Backup manual previo al rebuild.
  5. Rebuild + recreate + verificar logs de startup.
  6. Validar cartera, clientes y dashboard post-deploy.
- **Recomendación:** Ejecutar `/paso5.5` sobre la instalación productiva antes de hacer `docker compose build backend` en producción.

---

## TD-50 — `POST /store/sales` acepta member_id inexistente ✅ RESUELTO

- **ID:** TD-50
- **Estado:** Resuelto (2026-06-19).
- **Solución aplicada:** `SaleService` ahora incluye `MemberRepository` en su constructor. `create_sale()` valida explícitamente que `data.customer_id` corresponde a un `Member` existente antes de proceder; lanza `ValueError("Cliente no encontrado.")` → HTTP 400 si no existe. Sin cambios en BD ni en el frontend.

---

## TD-52 — Dashboard StatCards y tabla "Membresías por plan" usan `datetime.utcnow()` ✅ RESUELTO

- **ID:** TD-52
- **Estado:** Resuelto (2026-06-18). Corregido junto con TD-53 y TD-54 en una sola sesión de normalización de zona horaria.
- **Descripción:** `get_memberships_by_status` (línea 72) y `get_members_by_plan` (línea 144) en `dashboard_repository.py` calculan `days_remaining = (end_date - now).days` usando `now = datetime.utcnow()`. Mismo patrón corregido en `_calculate_status` (TD-46). Después de las 19:00 Bogotá, membresías que vencen "hoy" aparecen en el bucket `expired` en vez de `active`/`expiring` en las StatCards y en la tabla "Membresías por plan".
- **Riesgo:** Conteos del Dashboard inconsistentes con el badge de estado del cliente durante la ventana 19:00–00:00 Bogotá.
- **Impacto:** Medio. Afecta la información ejecutiva del Dashboard.
- **Módulos afectados:** `backend/app/repositories/dashboard_repository.py` — líneas 72 y 144.
- **Prioridad:** Media.
- **Solución futura:** Reemplazar `now = datetime.utcnow()` por `now = datetime.utcnow() + BOGOTA_OFFSET` en ambas funciones. `BOGOTA_OFFSET` ya está importado en el mismo archivo (línea 294 lo usa correctamente).

---

## TD-53 — `_enrich_membership` usa `datetime.utcnow()` para `days_remaining` ✅ RESUELTO

- **ID:** TD-53
- **Estado:** Resuelto (2026-06-18). Corregido junto con TD-52 y TD-54 en una sola sesión de normalización de zona horaria.
- **Descripción:** `_enrich_membership` en `membership_service.py` (línea 124) calcula `days_remaining = max(0, (membership.end_date - today).days)` con `today = datetime.utcnow()`. En el último día de vigencia, después de las 19:00 Bogotá, `days_remaining` devuelve 0 (cortado por `max(0,…)`) aunque el badge muestre `expiring`. La inconsistencia es visual: el número de días no coincide con el estado mostrado.
- **Riesgo:** El operador ve badge `expiring` pero `days_remaining = 0` en el detalle del cliente — puede generar confusión.
- **Impacto:** Bajo. Solo afecta `current-membership` y listados de membresías.
- **Módulos afectados:** `backend/app/services/membership_service.py` — línea 124.
- **Prioridad:** Baja.
- **Solución futura:** `today = datetime.utcnow() + BOGOTA_OFFSET` en `_enrich_membership`.

---

## TD-54 — `_has_active_valid_voucher` y `get_active_voucher_warning` usan `datetime.utcnow()` ✅ RESUELTO

- **ID:** TD-54
- **Estado:** Resuelto (2026-06-18). Corregido junto con TD-52 y TD-53 en una sola sesión de normalización de zona horaria.
- **Descripción:** Ambos métodos en `membership_service.py` (líneas 151 y 170) comparan `membership.end_date < now` con `now = datetime.utcnow()`. Una valera que vence a medianoche UTC (= 19:00 Bogotá) es tratada como inválida 5 horas antes del vencimiento local. Consecuencia potencial: el sistema podría permitir vender una nueva valera a las 19:30 Bogotá aunque la vigente no haya expirado localmente.
- **Riesgo:** Bajo. Las valeras son de uso diurno y el escenario exacto (compra de valera nueva después de las 19:00 Bogotá el día de vencimiento) es poco frecuente.
- **Impacto:** Bajo.
- **Módulos afectados:** `backend/app/services/membership_service.py` — líneas 151 y 170.
- **Prioridad:** Baja.
- **Solución futura:** Reemplazar `now = datetime.utcnow()` por `now = datetime.utcnow() + BOGOTA_OFFSET` en ambos métodos. Resolver junto con TD-52 y TD-53 en una sola sesión.

---

## TD-55 — `corrected_by` (quién hizo la corrección) no registrado en auditoría

- **ID:** TD-55
- **Título:** El campo `corrected_by` fue eliminado del diseño técnico y queda diferido a F2 (auth staff).
- **Descripción:** La tabla `membership_correction_logs` no registra qué usuario administrativo realizó la corrección. La omisión fue aprobada explícitamente en el Paso 3 para reducir complejidad antes de tener autenticación de personal (F2). Una vez implementado el sistema de auth, el campo puede añadirse con una migración idempotente (`ALTER TABLE ... ADD COLUMN corrected_by VARCHAR`).
- **Riesgo:** Trazabilidad de responsabilidad incompleta — se sabe *qué* se corrigió y *cuándo*, pero no *quién* lo hizo.
- **Impacto:** Bajo. En el contexto actual (un solo operador) no hay ambigüedad. Relevante solo cuando haya múltiples usuarios administrativos.
- **Módulos afectados:** `backend/app/models/membership_correction.py`, `backend/app/repositories/membership_correction_repository.py`, `backend/app/services/membership_service.py`.
- **Prioridad:** Baja — depende de F2 (auth staff).
- **Recomendación futura:** En F2, añadir `corrected_by: int (FK → staff_users.id, nullable)` a `membership_correction_logs` con migración idempotente. Propagar desde el endpoint (usuario autenticado via token) → servicio → repositorio.

---

## TD-56 — GET historial de correcciones de membresía no implementado

- **ID:** TD-56
- **Título:** El endpoint `GET /memberships/{id}/corrections` fue eliminado del Paso 3 para reducir alcance.
- **Descripción:** La tabla `membership_correction_logs` existe y es consultable vía `get_latest_for_membership()`, pero no hay endpoint público para listar el historial completo de correcciones de una membresía. La simplificación fue aprobada en el Paso 3 porque el operador no necesita auditar correcciones históricas desde la UI en este momento.
- **Riesgo:** No hay visibilidad del historial de correcciones desde la interfaz — solo se muestra `last_correction_at` y `last_correction_reason` en el detalle de la membresía.
- **Impacto:** Bajo. Los datos están en la BD y son auditables directamente con SQL si fuera necesario.
- **Módulos afectados:** `backend/app/repositories/membership_correction_repository.py` (faltaría método `get_all_for_membership`), `backend/app/api/routes/memberships.py` (endpoint GET faltante), `frontend/src/pages/Members.tsx` (UI faltante).
- **Prioridad:** Baja.
- **Recomendación futura:** Implementar `GET /api/members/memberships/{id}/corrections` que devuelva lista de `MembershipCorrectionLogRead` ordenada por `corrected_at DESC`. Mostrar como sección colapsable en el detalle de membresía.

---

## TD-57 — Índice compuesto `(membership_id, corrected_at)` en `membership_correction_logs` no creado

- **ID:** TD-57
- **Título:** La tabla de auditoría carece de índice compuesto para consultas de historial paginadas por membresía.
- **Descripción:** `membership_correction_logs` tiene índice individual en `membership_id` (via `index=True` en el modelo). Una consulta futura de historial ordenada por `corrected_at DESC` (TD-56) requeriría un índice compuesto `(membership_id, corrected_at)` para evitar sort en memoria. Identificado durante Paso 6 — Auditoría de `correct-start-date`.
- **Riesgo:** Ninguno en el volumen actual (~100 clientes, pocas correcciones por membresía). Solo relevante si el volumen crece significativamente o se implementa paginación del historial.
- **Impacto:** Bajo. Sin impacto funcional; solo rendimiento en consultas de historial.
- **Módulos afectados:** `backend/app/models/membership_correction.py`, `backend/app/database/init_db.py` (requeriría `CREATE INDEX IF NOT EXISTS`).
- **Prioridad:** Baja.
- **Recomendación futura:** Al implementar TD-56 (GET historial de correcciones), añadir `Index('ix_mcl_membership_corrected_at', 'membership_id', 'corrected_at')` al modelo o como `CREATE INDEX IF NOT EXISTS` en `init_db.py`.

---

## TD-58 — `passlib[bcrypt]==1.7.4` incompatible con `bcrypt>=5.x`

- **ID:** TD-58
- **Título:** Pin explícito `bcrypt==4.0.1` requerido para evitar incompatibilidad con passlib 1.7.4.
- **Descripción:** `passlib 1.7.4` (última versión estable) accede a `bcrypt.__about__.__version__` que fue eliminado en `bcrypt 5.x`. Sin el pin, `pip install passlib[bcrypt]` instala la última versión de bcrypt (5.x), que rompe el hash de contraseñas con `ValueError: password cannot be longer than 72 bytes` durante el detect_wrap_bug check de passlib. Descubierto durante el seed inicial de F2 Auth Staff.
- **Riesgo:** Si alguien reinstala dependencias sin el pin, el seed de `admin_user` falla en startup y el sistema arranca sin usuario admin (inutilizable en primer despliegue).
- **Impacto:** Bajo en instalaciones existentes (bcrypt ya anclado). Alto en instalaciones nuevas sin el pin.
- **Módulos afectados:** `backend/requirements.txt`.
- **Prioridad:** Baja.
- **Workaround aplicado:** `bcrypt==4.0.1` añadido explícitamente en `requirements.txt` como pin de compatibilidad.
- **Recomendación futura:** Actualizar a una versión de passlib compatible con bcrypt 5.x cuando esté disponible, o reemplazar passlib por `bcrypt` directamente para el hash de contraseñas (evita la dependencia intermedia).

---

## TD-59 — `ADMIN_INITIAL_PASSWORD` en `.env` no cambia contraseña activa del admin

- **ID:** TD-59
- **Título:** Cambiar `ADMIN_INITIAL_PASSWORD` en `.env` no actualiza la contraseña en DB sin ejecutar `reset_admin.py`.
- **Descripción:** `ADMIN_INITIAL_PASSWORD` se usa solo en dos momentos: (1) seed inicial del admin en `_seed_admin_user()`, (2) reset manual vía `scripts/reset_admin.py`. En runtime, la contraseña activa vive en `admin_users.hashed_password`. Un operador que modifique la variable en `.env` puede creer que la contraseña cambia automáticamente, pero no es así.
- **Riesgo:** Confusión operativa. El operador podría asumir que rotando `ADMIN_INITIAL_PASSWORD` en `.env` protege el sistema, sin ejecutar el reset.
- **Impacto:** Bajo — no afecta datos ni funcionamiento. Solo riesgo operativo.
- **Módulos afectados:** `backend/app/core/config.py`, `backend/scripts/reset_admin.py`, documentación operativa.
- **Prioridad:** Baja.
- **Documentado en:** FEATURE_SUMMARY.md — sección "Explicación de ADMIN_INITIAL_PASSWORD (TD-59)" y "Reset de contraseña de emergencia (reset_admin.py)".

---

## TD-60 — Arranque bloqueado si `.env` de producción no se actualiza antes del despliegue de F2

- **ID:** TD-60
- **Título:** Primera actualización a F2 en producción requiere `.env` con `JWT_SECRET_KEY` y `ADMIN_INITIAL_PASSWORD` antes de reiniciar el backend.
- **Descripción:** El validador `_validate_production_secrets` en `config.py` bloquea el arranque si `DEBUG=false` y faltan `JWT_SECRET_KEY` (o usa el valor dev) o `ADMIN_INITIAL_PASSWORD`. Una instalación existente que actualice el código sin actualizar `.env` primero quedará con el backend inaccesible hasta configurar las variables.
- **Riesgo:** App inaccessible en producción si el checklist de actualización no se sigue. El mensaje de error en consola es explícito y guía al operador.
- **Impacto:** Alto (app inaccessible) — pero solo ocurre si se omite el checklist. El fail-fast es intencional y preferible a un arranque con secretos débiles.
- **Módulos afectados:** `backend/app/core/config.py`.
- **Prioridad:** Media.
- **Documentado en:** FEATURE_SUMMARY.md — sección "Checklist de actualización para instalaciones existentes (TD-60)".

---

## TD-49 — `CreditPayment` definido en `customer.py` — dependencia cruzada con `member_repository.py`

- **ID:** TD-49
- **Título:** Modelo `CreditPayment` reside en `models/customer.py` pero es importado por `member_repository.py`.
- **Descripción:** `CreditPayment` es un modelo de dominio de ventas (abonos a crédito). Está definido en `models/customer.py` junto con `Customer`. Tras Cliente Único Phase 1, `member_repository.py` importa `CreditPayment` desde `customer.py` para calcular la deuda total de un miembro (`get_debt_total`). Esto crea un acoplamiento cruzado entre el módulo `member` y el módulo `customer`.
- **Riesgo:** Si `customer.py` se elimina en Phase 2, `member_repository.py` rompe en import. El desarrollador que limpie `customer.py` debe recordar mover `CreditPayment` primero.
- **Impacto:** Bajo en runtime. Solo riesgo de ruptura en limpieza de Phase 2 si no se coordina el orden de cambios.
- **Módulos afectados:** `backend/app/models/customer.py` (define `CreditPayment`), `backend/app/repositories/member_repository.py` (importa `CreditPayment`).
- **Prioridad:** Baja.
- **Recomendación futura:** En Phase 2, antes de eliminar `customer.py`, mover `CreditPayment` a `models/credit_payment.py` y actualizar todos los imports (`member_repository.py`, `sale_repository.py`, `init_db.py`).

---

## TD-61 — Feature Flags por módulo diferidos a F5 ✅ RESUELTO

- **ID:** TD-61
- **Estado:** Resuelto (F4-A, 2026-06-19).
- **Solución aplicada:** F4-A implementó el sistema de feature flags mediante variables de entorno `MODULE_*` en `.env`, leídas por `pydantic-settings` en `config.py`. Tres flags iniciales: `module_notifications`, `module_body_tracking`, `module_store`. Modelo opt-out para módulos ya en producción (default=True); módulos nuevos en F4-B+ usarán default=False (opt-in). Flag=False → router no registrado → HTTP 404. Endpoint público `GET /api/config/features` expone el estado de todos los módulos.
- **Archivos implementados:** `backend/app/core/config.py` (campos `module_*`), `backend/app/main.py` (registro condicional), `backend/app/api/routes/config.py` (endpoint features), `.env.example` (sección MODULE_*).
- **Descripción original:** F3 documenta las variables `.env` existentes como mecanismo de configuración por despliegue. No se implementó un sistema de flags activos porque no existen funcionalidades Premium que diferenciar de las Local. Un sistema de flags sin consumidores sería infraestructura prematura.
- **Módulos afectados:** `backend/app/core/config.py`, routers correspondientes.
- **Prioridad:** Baja — Resuelto.

---

## TD-63 — Migración de volumen en actualizaciones pre-F3 → F3

- **ID:** TD-63
- **Estado:** Mitigado por `upgrade.bat` (F3 Paso 7).
- **Descripción:** F3 introdujo `name: rhinopower` en `docker-compose.yml` y declaró el volumen con `name: rhinopower_db-data`. Instalaciones previas usaban el nombre del directorio como project name (ej. `aplicacion-gym_db-data`). Sin migración, Docker Compose crea un volumen vacío y los datos quedan inaccesibles.
- **Mitigación implementada:** `upgrade.bat` detecta automáticamente `aplicacion-gym_db-data`, migra los datos a `rhinopower_db-data` de forma estrictamente aditiva (nunca toca el volumen origen), valida que `gym.db` exista en el destino y solo entonces inicia los contenedores.
- **Módulos afectados:** `docker-compose.yml` (volumes), `upgrade.bat`, `docs/ACTUALIZACION.md`.
- **Prioridad:** Baja — resuelto para instalaciones conocidas (legacy `aplicacion-gym_db-data`).

---

## TD-65 — `GET /api/config/features` público — revisar en F8 (cloud)

- **ID:** TD-65
- **Estado:** Abierto — diferido a F8+.
- **Descripción:** El endpoint `GET /api/config/features` no requiere autenticación. Decisión justificada para despliegue local/LAN: el dato es metadata no sensible (flags booleanos), y el frontend necesitará consultarlo antes del login en F4-B. Para cloud multi-tenant (F8+), el endpoint debe protegerse para evitar enumeración de módulos por cliente.
- **Módulos afectados:** `backend/app/api/routes/config.py`.
- **Prioridad:** Baja.
- **Recomendación futura (F8+):** Añadir `Depends(require_active_user)` al router de `config` en `main.py` — cambio de 1 línea cuando el contexto de despliegue lo requiera.

---

## TD-64 — `python-jose 3.3.0` bloquea upgrade de `cryptography` a ≥ 42.x ✅ RESUELTO

- **ID:** TD-64
- **Estado:** Resuelto (F4-A, 2026-06-19).
- **Solución aplicada:** `python-jose[cryptography]==3.3.0` reemplazado por `PyJWT==2.9.0`. `cryptography` actualizado de `41.0.7` a `43.0.3` (desbloqueado al eliminar la dependencia de jose). Cambio en 2 archivos: `requirements.txt` y `auth_service.py` (import + excepción). Tokens HS256 pre-migración válidos sin re-login (mismo formato Base64url, mismo algoritmo y clave).
- **Estado original:** Abierto — diferido a F4.
- **Descripción:** `python-jose 3.3.0` (última versión, proyecto inactivo desde 2021) usa APIs de `cryptography` que fueron modificadas en la serie 42.x. El pin `cryptography==41.0.7` es necesario mientras `python-jose` siga siendo la librería JWT. Los CVEs que exigen ≥ 42.x (CVE-2024-26130, CVE-2024-0727) no afectan al app de gestión de gimnasio — ambos requieren serialización PKCS12 ausente en el app. Para JWT HS256 (uso real), no hay vulnerabilidad activa.
- **Riesgo:** Bajo en operación actual. Medio en instalaciones futuras con mayores requisitos de seguridad.
- **Módulos afectados:** `backend/requirements.txt`, `backend/app/api/routes/auth.py`, `backend/app/services/auth_service.py`.
- **Prioridad:** Baja.
- **Recomendación futura (F4):** Reemplazar `python-jose[cryptography]==3.3.0` por `PyJWT>=2.8.0` (mantenido activamente, compatible con `cryptography 42+`). Actualizar imports en `auth_service.py`: `from jose import jwt` → `import jwt`. Cambio en 1 archivo (`auth_service.py`); no requiere cambios de BD ni de frontend.

---

## TD-66 — Rutas Premium accesibles por URL directa cuando módulo desactivado

- **ID:** TD-66
- **Estado:** Abierto — aceptado, diferido.
- **Descripción:** Con `module_store=false` o `module_notifications=false`, el sidebar oculta los items correspondientes pero las rutas React Router `/tienda` y `/configuracion` siguen registradas. Un operador que escriba la URL directamente puede acceder a la página, que fallará con errores de carga (backend devuelve 404 en todos los endpoints del módulo desactivado).
- **Riesgo:** Bajo. En ISV Local el backend es la capa de control real. El frontend falla graceful — las páginas muestran errores pero no exponen datos ni permiten escrituras. No es un vector de seguridad (mismo usuario único).
- **Impacto:** UX degradada si el operador navega directamente a una URL de módulo desactivado.
- **Módulos afectados:** `frontend/src/App.tsx` (registro de rutas), `frontend/src/pages/Store.tsx`, `frontend/src/pages/Settings.tsx`.
- **Prioridad:** Baja.
- **Recomendación futura (F5+):** Añadir guard en las rutas protegidas por módulo usando `useFeatures()` en `ProtectedRoute` o un `<ModuleRoute moduleFlag="store">` wrapper.

---

## TD-62 — Acceso LAN multi-PC diferido a Edición Local Plus / F5

- **ID:** TD-62
- **Estado:** Abierto — diferido a F5 / Edición Local Plus.
- **Descripción:** El kit F3 soporta únicamente acceso desde la PC donde está instalado (localhost). Habilitar LAN multi-PC requiere configurar `BIND_ADDR`, `VITE_API_URL` con la IP local y gestionar reglas de firewall de Windows. Sin TLS (diferido a F5), exponer la API en la red local implica tráfico en claro.
- **Riesgo:** Gimnasios con múltiples terminales no pueden acceder desde todos los equipos.
- **Impacto:** Medio para gimnasios multi-PC. Bajo para el caso más común (una PC de recepción).
- **Módulos afectados:** `docker-compose.yml` (BIND_ADDR), `nginx.conf` (CORS), `.env` (VITE_API_URL), documentación.
- **Prioridad:** Media.
- **Recomendación futura (F5 / Local Plus):** Documentar procedimiento de configuración LAN y añadir sección de "instalación avanzada" en el kit con los pasos para BIND_ADDR + firewall + IP fija.
