# PRODUCT_ROADMAP.md — Gym Platform

> Roadmap oficial de producto a 24 meses.
> Versión: 1.1 — actualizada 2026-06-19. Fecha base: junio 2026.

---

## Estado Oficial del Proyecto — 2026-06-19

El proyecto opera en **dos líneas paralelas e independientes**:

### Línea Producto — Gym Platform

| Ítem | Estado |
|---|---|
| F4-A — Infraestructura de Plataforma | ✅ **Cerrada** (commit `9f2b12b`, 2026-06-19) |
| F4-B — Módulos Premium y Frontend Dinámico | ✅ **Cerrada** (commit `62844be`, 2026-06-19) |
| F4 — Platform Ready (técnicamente completada) | ✅ **Cerrada técnicamente** |
| Renombrado conceptual a `Gym Platform` | ✅ Completado (`project_name`, `project_version 1.2.0`) |
| Feature flags backend + frontend operativos | ✅ Completado (F4-A + F4-B) |
| `GET /api/config/features` | ✅ Completado (F4-A) |
| PyJWT migration (TD-64) | ✅ Completado (F4-A) |
| Repo renombrado a `gym-platform` en GitHub | ⏳ Diferido |
| F5 — Premium Edition | 🔒 No autorizado — próxima ola cuando el producto alcance madurez definida |

### Línea Cliente — Rhinopower

| Ítem | Estado |
|---|---|
| Core Platform v1.1 | ✅ En producción (tag `v1.1-rhinopower`, commit `441f5d3`) |
| F3 — Local Edition | ✅ Cerrada |
| TD-51 — Deploy producción Cliente Único Phase 1 | ⏳ **Pendiente** — actividad operacional independiente; no bloquea línea Producto |

> **Regla de separación de líneas:** TD-51 pertenece exclusivamente a la línea Rhinopower. No bloquea ni condiciona la evolución de Gym Platform. F4-A y F4-B fueron ejecutadas y cerradas sin dependencia sobre TD-51.

---

## Principios del Roadmap

- **Los releases son tags de git**, no ramas. Cada cliente en producción corre sobre un tag conocido.
- **Los módulos Premium se activan por feature flag**, nunca por versión de software diferente.
- **No hay branches de larga duración.** El desarrollo Premium ocurre en feature branches de vida corta que se mergean a `main`.
- **Producto y cliente son líneas separadas.** El progreso de la línea Producto no depende del estado operativo de ningún cliente específico.
- **El objetivo actual es construir capacidades de producto**, no iniciar expansión comercial.

---

## OLA 1 — F4: Platform Ready ✅ TÉCNICAMENTE COMPLETADA
### Meses 1–6 · Tag objetivo: `v1.2-platform`

**Objetivo estratégico:** Poder instalar la plataforma en un segundo gimnasio, distinto de Rhinopower, sin modificar una sola línea de código.

### Entregas técnicas completadas
- `GET /api/config/features` — endpoint público que expone el estado de los módulos activos ✅
- Feature flags operativos en backend y frontend (F4-A + F4-B) ✅
- Sustitución de `python-jose` por `PyJWT` (TD-64) ✅
- Frontend dinámico: sidebar, rutas y contenido condicionados por flags ✅

### Entregas técnicas diferidas (no bloquean capacidad de segunda instalación)
- Repositorio renombrado en GitHub a `gym-platform` ⏳
- Módulo P-01 Comunicación Automatizada — diferido a siguiente ciclo
- Módulo P-07 Seguimiento Corporal standalone — diferido a siguiente ciclo

### Hito comercial de cierre
Primera instalación en un gimnasio que no sea Rhinopower, con contrato firmado. Diferido: el objetivo actual es madurez de producto, no expansión comercial.

---

## OLA 2 — F5: Premium Edition
### Meses 7–12 · Tag objetivo: `v1.3-premium`

**Objetivo estratégico:** Catálogo Premium con los módulos de mayor impacto directo en los ingresos del gimnasio. El gimnasio puede cobrar online y tener presencia digital propia.

### Entregas técnicas
- Módulo P-02 Cobros Online: integración con Wompi (Colombia, prioridad); MercadoPago en el mismo ciclo
- Módulo P-03 Ecosistema Digital v1: web pública del gimnasio, CMS básico administrable desde el panel, integración con Cobros Online para pagos desde la web
- Módulo P-04 Control de Acceso Software: QR desde el sistema, código numérico, bloqueo automático de acceso por membresía vencida, registro de entradas y salidas con timestamp
- Módulo P-08 Analítica Avanzada (entrega inicial v1): KPIs de retención, churn mensual, LTV básico, reportes exportables
- Soporte TLS/HTTPS en Docker — habilita acceso desde múltiples PCs en red local (recepción + administración)
- PayU como tercera pasarela de Cobros Online

### Hito comercial de cierre
Cinco clientes activos en producción. Al menos un cliente en Plan Professional. Al menos un Bundle Digital vendido (P-02 + P-03).

---

## OLA 3 — F6: Digital & Access
### Meses 13–18 · Tag objetivo: `v2.0-digital`

**Objetivo estratégico:** La marca del gimnasio en el celular de sus clientes. El gimnasio controla su acceso físico sin papel ni intervención manual.

### Entregas técnicas
- Módulo P-06 App Móvil Cliente v1 (React Native — iOS y Android):
  - Estado de membresía en tiempo real
  - QR de acceso generado desde la app
  - Historial de pagos del cliente
  - Notificaciones push de vencimiento y novedades
  - Renovación online de membresía integrada con Cobros Online
  - Perfil del cliente
- Módulo P-05 Control de Acceso Hardware: integración con lector de huella digital externo y tablet en modo kiosco como punto de ingreso autónomo
- Kit hardware comercializable: lector biométrico + tablet + accesorios + servicio de instalación
- Módulo P-08 Analítica Avanzada: LTV por segmento de plan, segmentación por comportamiento de asistencia y pago, dashboard gerencial, reportes ejecutivos exportables en PDF y Excel

### Hito comercial de cierre
App Móvil disponible en App Store y Google Play. Al menos un cliente con kit hardware de control de acceso instalado y operando. Ocho clientes activos en producción.

---

## OLA 4 — F7: Intelligence
### Meses 19–24 · Tag objetivo: `v2.1-intelligence`

**Objetivo estratégico:** Diferenciación por inteligencia de negocio. El gimnasio toma decisiones basadas en datos, no en intuición. La plataforma predice problemas antes de que ocurran.

### Entregas técnicas
- Módulo P-09 IA Predictiva v1:
  - Modelo de predicción de deserción: identifica clientes con alta probabilidad de no renovar en los próximos 30 días
  - Alertas preventivas al administrador con recomendaciones de acción personalizadas
  - Automatización de campañas de retención basadas en comportamiento histórico
  - Análisis de patrones de asistencia y correlación con renovación
- API pública v1 — evaluación de apertura para integraciones de terceros (contabilidad, wearables, equipos de gimnasio)
- Evaluación formal documentada: go/no-go para transición a modelo SaaS cloud (F8)

### Hito comercial de cierre
Diez clientes activos en producción. Decisión documentada sobre modelo cloud (F8) basada en demanda real medida, no en proyecciones.

---

## Tabla Resumen del Roadmap

| Ola | Período | Tag | Módulos nuevos entregados | Clientes objetivo |
|---|---|---|---|---|
| F3 (cerrada) | — | `v1.1-local` | Core completo (M-01 al M-07) | 1 (Rhinopower) |
| F4 — Platform Ready | M1–M6 | `v1.2-platform` | P-01 Comunicación, P-07 Seguimiento | 2–3 |
| F5 — Premium Edition | M7–M12 | `v1.3-premium` | P-02 Cobros, P-03 Web, P-04 Acceso SW, P-08 Analítica | 5+ |
| F6 — Digital & Access | M13–M18 | `v2.0-digital` | P-06 App Móvil, P-05 Acceso HW, P-08 Avanzada | 8+ |
| F7 — Intelligence | M19–M24 | `v2.1-intelligence` | P-09 IA Predictiva, API pública | 10+ |

---

## Fuera del Roadmap 24 Meses

Los siguientes ítems quedan diferidos a F8+ y **no deben planificarse ni diseñarse** hasta que la base de clientes ISV y las condiciones de mercado lo justifiquen:

- Arquitectura multi-tenant cloud (PostgreSQL compartido entre clientes)
- Modelo de suscripción mensual SaaS con cobro por uso o por miembro activo
- Panel de administración multi-gimnasio (superadmin para el proveedor)
- Facturación electrónica DIAN integrada
- Integraciones con sistemas contables (Siigo, Alegra, Helisa)
- Sincronización en tiempo real entre múltiples sedes
- Marketplace de integraciones de terceros
- Módulos de nómina o gestión de empleados

Incluir cualquiera de estos ítems antes del momento correcto genera deuda técnica sin retorno comercial.

---

## Estrategia de modelo de IA por fase

La estrategia óptima es variar entre modelos de Claude, no usar uno solo. Heurística: *diseño y gates de seguridad → Opus 4.8. Implementación → Sonnet 4.6. Exploración/búsqueda → Haiku 4.5.* Donde un error causa daño real (auditorías, auth, pagos, webhooks), el modelo más inteligente justifica su costo; donde el plan ya está aprobado y solo se ejecuta, Sonnet rinde igual.

| Tipo de trabajo | Modelo recomendado | Por qué |
|---|---|---|
| Auditorías de seguridad | **Opus 4.8** | Detección de vulnerabilidades = máximo riesgo |
| Diseño de auth / BOLA | **Opus 4.8** | El diseño de auth no admite errores |
| Flujos de pago y webhooks | **Opus 4.8** | Punto de mayor riesgo del proyecto |
| Gates de seguridad (cualquier fase) | **Opus 4.8** | Siempre con el mejor modelo |
| Implementación de features | **Sonnet 4.6** | Mecánico una vez aprobado el diseño |
| Configuración e infraestructura | Sonnet (Opus revisa) | Impl rutinaria; config crítica revisada en Opus |
| Exploración / búsqueda de código | **Haiku 4.5** | Bajo costo, suficiente para localización |

**Patrón:** diseño y gates en Opus; implementación en Sonnet. Cada gate de seguridad corre en Opus aunque la fase se haya implementado en Sonnet.

**Mecánica en Claude Code:** cambiar de modelo con `/model` en cualquier momento. El subagente `security-auditor` se fija a Opus en su frontmatter (`model: opus`) mientras el flujo de implementación corre en Sonnet.

**Costo en plan Pro:** Opus/Fable consumen los límites de uso notablemente más rápido que Sonnet. Por eso se reserva Opus para los momentos de alto apalancamiento (auditorías y gates). Fable 5 solo si Opus 4.8 se traba en algo muy difícil.
