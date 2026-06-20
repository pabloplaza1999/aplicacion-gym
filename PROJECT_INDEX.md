# PROJECT_INDEX.md — Gym Platform

Estado del proyecto al 2026-06-19.
Punto de entrada único: lea este archivo primero, luego los específicos que necesite.

---

## Estado actual

| Línea | Estado |
|---|---|
| **Gym Platform** (producto) | F4-A + F4-B ✅ cerradas. F5 🔒 no autorizada. |
| **Rhinopower** (cliente) | Core v1.1 en producción (tag `v1.1-rhinopower`). TD-51 pendiente (deploy independiente). |

El repositorio opera sobre `main`. Releases = tags de git. No hay ramas de larga duración.

---

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | React 18 + TypeScript + TailwindCSS + Vite 5 |
| Backend | FastAPI 0.115.x + Pydantic 2.10.x + SQLAlchemy 2.0.x |
| Auth | PyJWT 2.9.0 (migrado de python-jose en F4-A) |
| BD | SQLite (archivo `gym.db` en volumen Docker) |
| Runtime | Docker Compose (3 servicios: backend, frontend, scheduler) |

---

## Documentación por rol

| Quién | Lee primero | Lee si necesita |
|---|---|---|
| Claude (agente de desarrollo) | Este archivo → FEATURE_SUMMARY.md | TECH_DEBT.md · ARQUITECTURA.md · BASE_DATOS.md |
| Desarrollador externo | Este archivo → README.md → ARQUITECTURA.md | PLATFORM_ARCHITECTURE.md · PRODUCT_MODULES.md |
| Instalador externo | docs/MANUAL_TECNICO.md | docs/INSTALACION.md · docs/OPERACION.md |
| Usuario final | docs/MANUAL_USUARIO.md | — |
| Producto / comercial | PRODUCT_VISION.md · PRODUCT_ROADMAP.md | PRODUCT_MODULES.md · LICENSING_STRATEGY.md |

---

## Arquitectura de módulos

- **Core (M-01 a M-07):** siempre activos, sin feature flag.
- **Premium (P-01 a P-09):** activados por variable de entorno en `.env`.
- **Endpoint canónico:** `GET /api/config/features` → estado real de todos los flags.
- **Separación:** `modules/` puede importar `core/`; lo inverso está prohibido.

| Módulos activos en Rhinopower | Flags activos |
|---|---|
| Core completo + Notificaciones + Body Tracking | `MODULE_NOTIFICATIONS=true`, `MODULE_BODY_TRACKING=true` |

Catálogo completo: **PRODUCT_MODULES.md**

---

## Roadmap resumido

| OLA | Fase | Estado | Tag objetivo |
|---|---|---|---|
| 1 | F4 Platform Ready | ✅ Cerrada técnicamente | `v1.2-platform` |
| 2 | F5 Premium Edition | 🔒 No autorizada | `v1.3-premium` |
| 3 | F6 Digital & Access | Futuro | `v2.0-digital` |
| 4 | F7 Intelligence | Futuro | `v2.1-intelligence` |

Detalle completo: **PRODUCT_ROADMAP.md**

---

## Deuda técnica abierta — prioridad Alta

| ID | Descripción | Bloquea |
|---|---|---|
| TD-51 | Deploy producción Rhinopower (Cliente Único Phase 1) | Solo línea Rhinopower |

Lista completa: **TECH_DEBT.md**

---

## Patrones de desarrollo

```
Backend:  route → service → repository → model
Frontend: page → component → api.ts → types
Commits:  feat(scope): descripción
```

- Rutas estáticas antes que dinámicas.
- Payloads frontend: tipos `Upsert`.
- Callbacks: `onUpdated(): void`.
- Múltiples edits interdependientes en un archivo → usar Write completo (ver CLAUDE.md §Hook).

---

## Archivos clave por dominio

| Dominio | Archivo |
|---|---|
| Historia de implementación | FEATURE_SUMMARY.md |
| Deuda técnica | TECH_DEBT.md |
| Esquema BD + invariantes | BASE_DATOS.md · ARQUITECTURA.md |
| Plataforma ISV + flags + security-auditor | PLATFORM_ARCHITECTURE.md |
| Módulos y precios canónicos | PRODUCT_MODULES.md |
| Visión, misión, mercado objetivo | PRODUCT_VISION.md |
| Roadmap y estrategia IA por fase | PRODUCT_ROADMAP.md |
| Licenciamiento y upsell | LICENSING_STRATEGY.md |
| Deploy multi-cliente | docs/DEPLOYMENT_PLAYBOOK.md |
| Kit cliente Rhinopower | docs/EMPAQUETADO.md |
