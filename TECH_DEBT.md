# TECH_DEBT.md

Registro de deuda técnica y pendientes identificados durante las Fases A, B, B.5 (regla de valera única + corrección de renovación) y C (frontend de asistencia).

Este documento recopila **únicamente** los riesgos detectados en esas fases. No surge de un nuevo análisis de código. Su objetivo es que cualquier desarrollador o modelo entienda el contexto sin acceder al historial de la conversación.

Prioridad: **Alta** (afecta datos o reglas de negocio) · **Media** (afecta UX o consistencia) · **Baja** (cosmético / no funcional).

---

## TD-01 — Valeras agotadas/vencidas siguen apareciendo como activas en Dashboard y current-membership

- **ID:** TD-01
- **Título:** Valeras finalizadas no se reflejan como inactivas en vistas de estado.
- **Descripción:** La lógica de negocio trata una valera como "no vigente" cuando se agotan sus ingresos (`COUNT(attendances) >= entries_total`) o cuando vence (`end_date < hoy`). Sin embargo, el Dashboard y el endpoint current-membership derivan el estado solo de `end_date`/`is_active` y no consideran el consumo de ingresos, por lo que una valera agotada (pero aún dentro de fecha) puede seguir mostrándose como activa.
- **Riesgo:** Información engañosa: el dueño puede creer que un cliente tiene una valera utilizable cuando ya no le quedan ingresos.
- **Impacto:** Medio. No corrompe datos ni bloquea el check-in (que sí valida correctamente), pero confunde la lectura del estado del negocio.
- **Módulos afectados:** `dashboard_repository.py`, `dashboard_service.py`, endpoint current-membership (`membership_service.get_current_membership`), frontend Dashboard / detalle de cliente.
- **Prioridad:** Media.
- **Recomendación futura:** Incorporar el consumo de ingresos (COUNT de asistencias vs `entries_total`) al cálculo de estado de las membresías tipo voucher en Dashboard y current-membership, sin duplicar contadores (mantener `COUNT(attendances)` como fuente de verdad).

---

## TD-02 — Posible coexistencia de valeras preexistentes en datos antiguos

- **ID:** TD-02
- **Título:** La regla "una valera activa por cliente" no limpia coexistencias previas.
- **Descripción:** En la Fase B.5 se implementó el bloqueo que impide vender/renovar una nueva valera mientras exista otra activa vigente. Esa regla previene **nuevas** coexistencias, pero no corrige datos históricos donde un cliente ya tuviera dos o más valeras con `is_active=True`. Además, `get_active_voucher_membership` selecciona solo la más reciente por `start_date`, de modo que la validación evalúa una sola valera aunque existan varias.
- **Riesgo:** Datos inconsistentes previos a la regla pueden pasar desapercibidos; el consumo/visualización podría no reflejar la valera esperada.
- **Impacto:** Medio. Depende de si existen datos históricos con coexistencias; en una base limpia el riesgo es nulo.
- **Módulos afectados:** `membership_repository.py` (`get_active_voucher_membership`), `membership_service.py`, base de datos (`memberships`).
- **Prioridad:** Media.
- **Recomendación futura:** Script de auditoría/migración que detecte clientes con más de una valera `is_active=True` vigente y normalice (desactivar las sobrantes según criterio de negocio). Opcionalmente, una restricción a nivel de datos que garantice una sola valera activa por cliente.

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

## TD-04 — Manejo de zona horaria en UTC

- **ID:** TD-04
- **Título:** Vigencia y "una asistencia por día" se calculan en UTC.
- **Descripción:** El backend usa `datetime.utcnow()` para calcular vencimientos y para la restricción de una asistencia por cliente por día (`check_in_date`). El gimnasio opera en hora local; cerca de la medianoche local puede haber desfase respecto a la fecha UTC.
- **Riesgo:** Una asistencia registrada tarde en la noche (hora local) podría contarse en el día UTC siguiente, o un vencimiento podría adelantarse/atrasarse respecto a la expectativa local.
- **Impacto:** Bajo-Medio. Casos borde alrededor de la medianoche; poco frecuente pero posible.
- **Módulos afectados:** `membership_service.py`, `attendance_service.py`, `attendance_repository.py`, `init_db`/seeds que usan fechas.
- **Prioridad:** Baja.
- **Recomendación futura:** Definir explícitamente la zona horaria del negocio (p. ej. America/Bogota) y aplicar conversión consistente al calcular fechas de vencimiento y `check_in_date`.

---

## TD-05 — Renovación no desactiva la membresía anterior

- **ID:** TD-05
- **Título:** `renew_membership` crea una nueva membresía pero deja activa la anterior.
- **Descripción:** Al renovar, se crea una nueva membresía que inicia hoy, pero la membresía previa conserva su `is_active` y su estado derivado por fechas. No hay un cierre/desactivación automática de la anterior.
- **Riesgo:** Para valeras, una renovación podría chocar con la regla de "una valera activa por cliente" si la anterior sigue vigente; para mensuales, puede coexistir más de una membresía "activa" simultáneamente.
- **Impacto:** Medio. Comportamiento preexistente; interactúa con TD-02 y con la regla de valera única.
- **Módulos afectados:** `membership_service.py` (`renew_membership`), `membership_repository.py`.
- **Prioridad:** Media.
- **Recomendación futura:** Definir explícitamente la semántica de renovación: al renovar, marcar la membresía anterior como inactiva/cerrada (o documentar por qué se conserva), de forma coherente con la regla de valera única.

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

## Resumen de prioridades

| ID | Título | Prioridad |
|----|--------|-----------|
| TD-01 | Valeras finalizadas no aparecen inactivas en Dashboard/current-membership | Media |
| TD-02 | Coexistencia de valeras preexistentes en datos antiguos | Media |
| TD-03 | Cédula no obligatoria pese a ser requerida para check-in | Media |
| TD-04 | Cálculo de fechas en UTC (desfase en medianoche local) | Baja |
| TD-05 | Renovación no desactiva la membresía anterior | Media |
| TD-06 | Visualización de valera solo en la página de Asistencia | Baja |
| TD-07 | `Navbar.tsx` es código muerto | Baja |
| TD-08 | Validación e2e en navegador no concluida | Baja |
