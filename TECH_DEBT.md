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

## TD-04 — Uso de UTC en cálculos de vencimiento

- **ID:** TD-04
- **Título:** Vigencia, asistencias diarias y panel de alertas se calculan en UTC.
- **Descripción:** El backend usa `datetime.utcnow()` para calcular vencimientos, la restricción de una asistencia por cliente por día (`check_in_date`) y la clasificación de alertas de membresías en el Dashboard. El gimnasio opera en hora local (America/Bogota, UTC-5); cerca de la medianoche local puede haber desfase respecto a la fecha UTC.
- **Riesgo:** Una asistencia registrada tarde en la noche (hora local) podría contarse en el día UTC siguiente. Un cliente cercano al vencimiento podría aparecer en una categoría de alerta distinta (p. ej. "Hoy" vs "1 día") dependiendo de la hora local al cargar el Dashboard.
- **Impacto:** Bajo. Casos borde alrededor de la medianoche; poco frecuente en operación normal.
- **Módulos afectados:** `dashboard_repository.py` (`get_membership_alerts`, `get_members_by_plan`), `membership_service.py`, `attendance_service.py`, `attendance_repository.py`, `init_db`/seeds que usan fechas, `services/dashboard_service.py` (`days_overdue` en `DebtorAlert` — Dashboard Fase B, `days_overdue` en `MembershipAlert` — resumen-control-membresias).
- **Prioridad:** Baja.
- **Mitigación actual:** Mantener UTC para conservar comportamiento homogéneo en todo el sistema.
- **Solución futura:** Permitir configuración de zona horaria por gimnasio y realizar los cálculos utilizando dicha configuración. Impacta `get_membership_alerts`, `_calculate_status`, la restricción de check-in diario y el cálculo de `days_overdue` en alertas de cartera.

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
| TD-04 | UTC en vencimientos, asistencias diarias y alertas Dashboard (desfase en medianoche local) | Baja |
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
| TD-26 | Backup automático de volumen SQLite no implementado — riesgo de pérdida de datos en producción | Media |

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

---

## TD-26 — Backup automático de volumen SQLite no implementado

- **ID:** TD-26
- **Estado:** Abierto.
- **Descripción:** La base de datos `gym.db` vive en el volumen Docker `appparagym_db-data`. No existe mecanismo automatizado de backup. Un `docker compose down -v` ejecutado por error destruye los datos de forma permanente e irreversible. El README documenta el procedimiento manual de backup, pero no hay automatización ni salvaguarda técnica.
- **Riesgo:** Pérdida total de datos si el operador ejecuta `docker compose down -v` sin hacer backup previo.
- **Impacto:** Alto en producción si ocurre. Probabilidad baja si el operador sigue el README.
- **Módulos afectados:** Volumen `appparagym_db-data`, operaciones de mantenimiento del sistema.
- **Prioridad:** Media.
- **Why:** La arquitectura SQLite + volumen Docker es correcta para el tamaño del negocio, pero no incluye resiliencia operativa ante errores humanos.
- **How to apply:** Antes de cualquier despliegue en servidor de producción real, implementar un cron de backup diario en el host. El procedimiento está documentado en `README.md` (sección "Respaldo y restauración").
- **Recomendación futura:** Cron en el host que ejecute `docker run --rm -v appparagym_db-data:/data -v /ruta/backups:/backup alpine cp /data/gym.db /backup/gym_FECHA.db` diariamente.
