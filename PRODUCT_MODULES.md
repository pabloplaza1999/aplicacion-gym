# PRODUCT_MODULES.md — Catálogo Oficial de Módulos

> Catálogo completo de módulos de Gym Platform: Core y Premium.
> Versión: 1.0 — aprobada por producto. Fecha: junio 2026.

---

## Criterio de Clasificación

Un módulo es **Core** si su ausencia hace que la plataforma no sea operativa para ningún gimnasio en ningún contexto. Es la base mínima que justifica la venta de cualquier plan.

Un módulo es **Premium** si agrega valor diferenciado por el que existe disposición a pagar adicional, o si tiene costo operativo externo (APIs de terceros, hardware, infraestructura adicional).

---

## Módulos Core

Incluidos en toda licencia sin excepción. No tienen feature flag. No pueden desactivarse.

---

### M-01 · Gestión de Miembros

Registro completo de clientes del gimnasio: datos personales, documento de identidad, fotografía, teléfono, correo y notas. Estado activo/inactivo. Búsqueda por nombre y documento con paginación. Historial de membresías y pagos por cliente. Soft delete con recuperación.

**Valor principal:** elimina el cuaderno de papel y la hoja de Excel como sistema de registro. Es la base de datos de clientes del gimnasio.

---

### M-02 · Membresías y Planes

Gestión del ciclo de vida completo de la membresía: creación, activación, vencimiento, congelamiento, corrección de fechas y renovación. Soporte para planes diarios, semanales, mensuales y períodos personalizados. Registro de fecha de inicio inmutable con log de auditoría. Alertas de vencimiento próximo configurables.

**Valor principal:** el gimnasio sabe exactamente qué clientes tienen membresía activa, cuáles vencen esta semana y cuáles están en mora.

---

### M-03 · Asistencia y Check-in

Registro de ingresos diarios por miembro (sistema de valerías). Control de si el cliente ya asistió hoy. Historial completo de asistencia por cliente y por fecha. Alerta visual cuando el cliente intenta hacer check-in con membresía vencida. Estadísticas de asistencia por período.

**Valor principal:** el recepcionista sabe en menos de 3 segundos si un cliente tiene derecho a ingresar hoy.

---

### M-04 · Pagos

Registro de pagos de membresías: método de pago, monto, fecha, concepto y notas. Historial completo por cliente. Dashboard de cobros del período (día, semana, mes). Sin procesamiento activo de pagos — eso corresponde al módulo Premium P-02.

**Valor principal:** el administrador cierra el mes sabiendo exactamente cuánto entró y de quién.

---

### M-05 · Dashboard Operativo

Panel de control en tiempo real: miembros activos, membresías próximas a vencer (configurables por días de anticipación), ingresos del día y del mes, asistencias del día, clientes sin membresía activa. Diseñado para ser la primera pantalla que ve el operador al abrir el sistema cada mañana.

**Valor principal:** en 10 segundos el dueño sabe el estado de su negocio sin abrir un solo reporte.

---

### M-06 · Autenticación y Seguridad

Login con JWT stateless. Rate limiting en el endpoint de autenticación (20 intentos por IP por ventana de 60 segundos — configurable). Cambio de contraseña con flujo de token temporal en primer acceso. Documentación de OpenAPI deshabilitada en producción. Validación de secretos obligatorios al arranque del sistema.

**Valor principal:** el sistema del gimnasio no es accesible para personas no autorizadas, incluso dentro de la red local.

---

### M-07 · Backup Automático

Backup diario automatizado del archivo de base de datos con retención configurable (30 copias por defecto). Backup manual desde el panel administrativo disponible en cualquier momento. Descarga directa de archivos de backup desde la interfaz. Scheduler independiente del proceso principal.

**Valor principal:** el gimnasio nunca pierde sus datos por un fallo de hardware. La recuperación es un proceso de 5 minutos.

---

## Módulos Premium

Requieren activación explícita mediante feature flag en el `.env` de la instalación. El backend rechaza todas las rutas de módulos inactivos con HTTP 403. El frontend no renderiza rutas ni navegación de módulos inactivos, independientemente del plan contratado.

---

### P-01 · Comunicación Automatizada
**Feature flag:** `MODULE_NOTIFICATIONS=true`
**Disponible desde:** Plan Starter (add-on) / incluido en Professional y Premium
**Precio add-on:** $600.000 COP / año
**Dependencias:** ninguna

Recordatorios automáticos de vencimiento de membresía por WhatsApp y correo electrónico. Configuración de umbrales de envío (días antes del vencimiento, número de recordatorios). Campañas promocionales desde el panel administrativo con segmentación básica. Módulo de reactivación de clientes inactivos con mensajes automatizados. Integración con WhatsApp Business API y servidor SMTP.

**Gatillo de compra:** el dueño del gimnasio menciona que tuvo clientes que no renovaron porque "se olvidaron". Este módulo los contacta automáticamente.

---

### P-02 · Cobros Online
**Feature flag:** `MODULE_PAYMENTS_ONLINE=true`
**Disponible desde:** Plan Starter (add-on) / incluido en Premium
**Precio add-on:** $1.200.000 COP / año
**Dependencias:** ninguna (se integra con P-03 y P-06, pero no los requiere)

Integración con pasarelas de pago colombianas: Wompi (prioridad), MercadoPago y PayU. Generación de links de pago individuales enviables por WhatsApp o correo. Renovación de membresías desde el link sin intervención del recepcionista. Conciliación automática de pagos recibidos con la membresía correspondiente. Cobros desde la web pública (requiere P-03) y desde la App Móvil (requiere P-06).

**Gatillo de compra:** el gimnasio recibe efectivo o transferencias manuales y pierde clientes que no pueden ir presencialmente a pagar.

---

### P-03 · Ecosistema Digital
**Feature flag:** `MODULE_DIGITAL_ECOSYSTEM=true`
**Disponible desde:** Plan Starter (add-on) / incluido en Premium
**Precio add-on:** $1.800.000 COP / año
**Dependencias:** ninguna. Se integra con P-02 para habilitar pagos desde la web (no obligatorio).

Página web pública del gimnasio con branding personalizado (nombre, colores, logo, descripción). Landing pages para promociones y campañas estacionales. CMS básico administrable desde el panel administrativo: fotografías, texto libre, horarios, servicios, precios. Integración con Cobros Online para que los visitantes de la web puedan adquirir o renovar membresías directamente.

**Gatillo de compra:** el gimnasio no tiene presencia digital propia o su web está desactualizada y no genera leads.

---

### P-04 · Control de Acceso — Software
**Feature flag:** `MODULE_ACCESS_CONTROL=true`
**Disponible desde:** Plan Starter (add-on) / incluido en Premium
**Precio add-on:** $1.200.000 COP / año
**Dependencias:** ninguna. Funciona sin hardware especializado desde el dispositivo de recepción existente.

Control de ingreso y egreso al gimnasio mediante QR (generado en el sistema, imprimible o desde App Móvil) y código numérico. Bloqueo automático de acceso cuando la membresía está vencida — sin intervención del recepcionista. Registro automático de entradas y salidas con fecha, hora y método de acceso. Historial de accesos por miembro consultable desde el panel. Panel de ingresos del día en tiempo real.

**Gatillo de compra:** el gimnasio tiene problemas con personas que entran sin membresía activa o el recepcionista no siempre puede validar manualmente.

---

### P-05 · Control de Acceso — Hardware
**Feature flag:** `MODULE_ACCESS_CONTROL=true` (mismo flag que P-04)
**Disponible desde:** requiere P-04 activo
**Precio:** $3.500.000 COP (kit hardware — pago único) + $600.000 COP / año (mantenimiento SW)
**Dependencias:** requiere P-04 operativo.

Lector biométrico de huella digital integrado al sistema de acceso. Tablet en modo kiosco como pantalla de ingreso autónoma en la entrada del gimnasio — el cliente registra su ingreso sin recepcionista. SDK biométrico integrado con la lógica de validación de membresía del sistema. Registro de ingreso automático por huella vinculado al historial del miembro.

**Gatillo de compra:** el gimnasio quiere eliminar completamente la dependencia del recepcionista para el control de ingreso, especialmente en horarios extendidos o de bajo flujo.

---

### P-06 · Aplicación Móvil para Clientes
**Feature flag:** `MODULE_MOBILE_APP=true`
**Disponible desde:** Plan Professional (add-on)
**Precio add-on:** $2.400.000 COP / año
**Dependencias:** requiere P-02 (Cobros Online) para habilitar renovación online. Se integra con P-04 para QR de acceso.

Aplicación iOS y Android bajo la marca del gimnasio (white-label). El cliente ve el logo y colores de su gimnasio, no el logo de Gym Platform. Funcionalidades: estado de membresía en tiempo real, QR de acceso generado desde la app, historial de pagos y asistencias del cliente, notificaciones push de vencimiento y novedades del gimnasio, renovación online de membresía integrada con Cobros Online, perfil del cliente editable.

**Gatillo de compra:** el gimnasio quiere diferenciarse de la competencia local y tener presencia directa en el celular de sus clientes. La App Móvil es el módulo de mayor visibilidad hacia los miembros del gimnasio.

---

### P-07 · Seguimiento Corporal
**Feature flag:** `MODULE_BODY_TRACKING=true`
**Disponible desde:** Plan Starter (add-on) / incluido en Professional y Premium
**Precio add-on:** $480.000 COP / año
**Dependencias:** ninguna.

Registro periódico de medidas corporales por cliente: peso, talla, circunferencias (cintura, cadera, pecho, brazos, muslos), porcentaje de grasa estimado y notas del entrenador. Fotografías de progreso con comparación visual entre fechas. Reportes gráficos de evolución física por cliente, exportables. Historial completo de mediciones por miembro.

**Gatillo de compra:** el gimnasio ofrece planes de entrenamiento personalizado o seguimiento nutricional y necesita documentar la evolución de sus clientes.

---

### P-08 · Analítica Avanzada
**Feature flag:** `MODULE_ANALYTICS=true`
**Disponible desde:** Plan Starter (add-on) / incluido en Professional y Premium
**Precio add-on:** $1.200.000 COP / año
**Dependencias:** se recomienda mínimo 6 meses de datos históricos en el sistema para que los indicadores sean estadísticamente representativos.

KPIs de retención y churn mensual (clientes que no renovaron sobre clientes que vencieron). Cálculo de LTV (lifetime value) por segmento de plan. Segmentación de clientes por comportamiento de asistencia (activos, en riesgo, inactivos). Análisis de ingresos por plan, por período y por canal de pago. Dashboard gerencial separado del dashboard operativo. Reportes ejecutivos exportables en PDF y Excel.

**Gatillo de compra:** el dueño toma decisiones de negocio basadas en intuición y quiere datos concretos para saber si está creciendo, estancado o perdiendo clientes.

---

### P-09 · Inteligencia Artificial Predictiva
**Feature flag:** `MODULE_AI=true`
**Disponible desde:** Plan Premium (add-on)
**Precio add-on:** $2.400.000 COP / año
**Dependencias:** requiere P-08 (Analítica Avanzada) activo y mínimo 12 meses de datos históricos en el sistema.

Modelo de predicción de deserción: identifica clientes con alta probabilidad de no renovar en los próximos 30 días, basado en patrones de asistencia, historial de pagos y comportamiento histórico. Alertas preventivas automáticas al administrador con recomendación de acción por cliente (llamar, enviar oferta, recordatorio personalizado). Automatización de campañas de retención activadas por el modelo predictivo. Reporte mensual de efectividad de las intervenciones de retención.

**Gatillo de compra:** el gimnasio ya tiene Analítica Avanzada, conoce su churn, y quiere actuar antes de que el cliente cancele en lugar de reaccionar después.

---

## Mapa de Dependencias

```
Core Platform (siempre activo — incluido en toda licencia)
  ├── P-01  Comunicación Automatizada    ← independiente
  ├── P-02  Cobros Online                ← independiente
  │     └── P-03  Ecosistema Digital     ← se integra con P-02 (pagos en web)
  │     └── P-06  App Móvil              ← requiere P-02 (renovación online)
  ├── P-04  Control de Acceso SW         ← independiente
  │     └── P-05  Control de Acceso HW   ← requiere P-04
  │     └── P-06  App Móvil              ← se integra con P-04 (QR)
  ├── P-07  Seguimiento Corporal         ← independiente
  └── P-08  Analítica Avanzada          ← independiente (requiere madurez de datos)
        └── P-09  IA Predictiva          ← requiere P-08
```

**Dependencias duras** (el sistema bloquea la activación si no se cumple):
- P-05 no puede activarse sin P-04
- P-09 no puede activarse sin P-08

**Dependencias de valor** (el módulo funciona, pero con capacidades reducidas sin el complemento):
- P-06 sin P-02: la app funciona, pero sin renovación online (la funcionalidad de mayor valor para el cliente)
- P-03 sin P-02: la web pública funciona, pero sin pasarela de pago integrada
- P-08 sin suficientes datos históricos: los indicadores son estadísticamente poco confiables

---

## Bundles Comerciales

Los bundles agrupan módulos con alta sinergia y ofrecen descuento sobre el precio separado.

| Bundle | Módulos incluidos | Precio | Ahorro vs. separados |
|---|---|---|---|
| Bundle Digital | P-02 + P-03 | $2.400.000 COP/año | 25% |
| Bundle Acceso | P-04 + P-06 | $3.000.000 COP/año | 20% |
| Bundle Inteligencia | P-08 + P-09 | $3.000.000 COP/año | 17% |
| Bundle Premium Total | P-01+P-02+P-03+P-04+P-08 | $5.400.000 COP/año | 30% |

---

## Tabla Resumen del Catálogo

| ID | Nombre | Tipo | Flag | Precio/año | Ola de entrega |
|---|---|---|---|---|---|
| M-01 | Gestión de Miembros | Core | — | Incluido | F3 ✅ |
| M-02 | Membresías y Planes | Core | — | Incluido | F3 ✅ |
| M-03 | Asistencia y Check-in | Core | — | Incluido | F3 ✅ |
| M-04 | Pagos | Core | — | Incluido | F3 ✅ |
| M-05 | Dashboard Operativo | Core | — | Incluido | F3 ✅ |
| M-06 | Autenticación y Seguridad | Core | — | Incluido | F3 ✅ |
| M-07 | Backup Automático | Core | — | Incluido | F3 ✅ |
| P-01 | Comunicación Automatizada | Premium | `MODULE_NOTIFICATIONS` | $600.000 | F4 |
| P-02 | Cobros Online | Premium | `MODULE_PAYMENTS_ONLINE` | $1.200.000 | F5 |
| P-03 | Ecosistema Digital | Premium | `MODULE_DIGITAL_ECOSYSTEM` | $1.800.000 | F5 |
| P-04 | Control de Acceso SW | Premium | `MODULE_ACCESS_CONTROL` | $1.200.000 | F5 |
| P-05 | Control de Acceso HW | Premium | `MODULE_ACCESS_CONTROL` | $3.500.000 único + $600.000/año | F6 |
| P-06 | App Móvil Cliente | Premium | `MODULE_MOBILE_APP` | $2.400.000 | F6 |
| P-07 | Seguimiento Corporal | Premium | `MODULE_BODY_TRACKING` | $480.000 | F4 |
| P-08 | Analítica Avanzada | Premium | `MODULE_ANALYTICS` | $1.200.000 | F5 |
| P-09 | IA Predictiva | Premium | `MODULE_AI` | $2.400.000 | F7 |
