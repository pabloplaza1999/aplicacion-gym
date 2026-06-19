# PLATFORM_ARCHITECTURE.md — Arquitectura de Plataforma

> Decisiones de arquitectura oficiales de Gym Platform.
> Versión: 1.0 — aprobada por producto y arquitectura. Fecha: junio 2026.

---

## Principio Fundamental

**Una plataforma. Un repositorio. Múltiples instalaciones.**

El código fuente es único y no contiene referencias a clientes específicos. La diferenciación entre instalaciones vive exclusivamente en la configuración (`.env`) y los datos (`gym.db`), nunca en el código. Si para instalar en un nuevo cliente hace falta modificar código, la separación está rota.

---

## Decisiones de Arquitectura Aprobadas

Las siguientes decisiones son definitivas para el ciclo F4–F7 (24 meses). Cualquier propuesta de cambio requiere revisión de arquitectura y actualización de este documento.

| Decisión | Elección | Alternativas descartadas |
|---|---|---|
| Estrategia de repositorio | Repositorio único (`gym-platform`) | Repos por cliente, monorepo con tooling |
| Separación cliente/plataforma | `.env` + volumen Docker | Branches por cliente, código condicional |
| Activación de módulos | Feature flags (variables de entorno) | Flags en base de datos, versiones distintas |
| Branches de desarrollo | Feature branches cortos → `main` | Long-lived branches (Gitflow, ramas por cliente) |
| Releases por cliente | Git tags (`v1.1-local`, `v1.2-platform`) | Branches de release permanentes |
| Modelo de despliegue | ISV local (Docker en PC del cliente) | SaaS cloud (diferido a F8+) |
| Base de datos | SQLite (1 archivo por instalación) | PostgreSQL (diferido a F8+) |
| Tooling de monorepo | No se usa (diferido a F8+) | Nx, Turborepo |

---

## Modelo de Despliegue: ISV Local Edition

Gym Platform opera bajo el modelo **ISV (Independent Software Vendor) con instalación local**. Cada gimnasio recibe un Docker Compose stack completo que se ejecuta en su propia infraestructura (PC local o servidor en sede).

### Características del modelo
- Sin dependencia de conectividad permanente a internet para el Core (el sistema funciona en intranet local)
- Los datos del gimnasio residen en su propia infraestructura bajo su propio control
- Un Docker stack independiente por instalación — sin aislamiento en shared infrastructure
- Actualizaciones controladas y voluntarias por el operador del gimnasio
- Módulos Premium activables por configuración, sin cambio de versión de software

### Topología de despliegue por cliente

```
PC / Servidor del Gimnasio
  └── Docker Engine
        ├── Container: backend (FastAPI + uvicorn)
        │     └── Monta volumen: /app/data/gym.db
        ├── Container: frontend (Nginx + React build)
        └── Container: scheduler (APScheduler — backups automáticos)

Volumen Docker: gym_db-data
  └── gym.db           ← Base de datos del gimnasio (SQLite)
  └── backups/         ← Directorio de backups automáticos
```

### Cuándo evolucionar hacia cloud

La transición a modelo SaaS/cloud (F8+) se evaluará exclusivamente cuando se cumplan simultáneamente las tres condiciones siguientes:

1. La base de clientes ISV supera los 20 gimnasios activos en producción
2. Existe demanda documentada (no proyectada) de acceso multi-dispositivo sin instalación local
3. El equipo de producto tiene capacidad operativa para gestionar infraestructura cloud compartida con SLA

No se diseña para cloud antes de que estas condiciones se cumplan. Anticipar la arquitectura cloud implica sobre-ingeniería que retrasa la entrega de valor en el horizonte real del producto.

---

## Repositorio

| Atributo | Valor |
|---|---|
| Nombre | `gym-platform` |
| Tipo | Repositorio único (monolito modular) |
| Rama principal | `main` — siempre en estado desplegable |
| Estrategia de branches | Feature branches de vida corta (días, no semanas) que se mergean a `main` |
| Releases | Git tags semánticos por versión de plataforma |
| Branches de larga duración | No se usan — la diferencia entre clientes es configuración, no código |
| Cliente de referencia en código | Ninguno — el repositorio no contiene nombres de clientes |

### Convención de tags

| Tag | Descripción |
|---|---|
| `v1.1-local` | Core Platform — Local Edition (F3, actual) |
| `v1.2-platform` | Platform Ready — Feature flags + 2° cliente (F4) |
| `v1.3-premium` | Premium Edition — primeros módulos Premium (F5) |
| `v2.0-digital` | Digital & Access — App Móvil + Hardware (F6) |
| `v2.1-intelligence` | Intelligence — IA Predictiva (F7) |

### Identificación de versión por cliente

Cada cliente en producción corre sobre un tag conocido. El registro de qué cliente corre qué versión es responsabilidad del proveedor, no del sistema. Rhinopower corre `v1.1-local`. Cuando reciba el primer módulo Premium se actualizará a `v1.2-platform`. La actualización siempre es explícita y precedida de backup.

---

## Stack Tecnológico

| Capa | Tecnología | Versión aprobada |
|---|---|---|
| Frontend | React + TypeScript | 18 |
| Estilos | TailwindCSS | 3 |
| Build tool | Vite | 5 |
| Backend | FastAPI | 0.115.x |
| Validación | Pydantic v2 | 2.10.x |
| ORM | SQLAlchemy | 2.0.x |
| Base de datos | SQLite | local per-installation |
| Autenticación | PyJWT (migrado en F4-A desde python-jose) | 2.9.0 |
| Criptografía | cryptography (desbloqueado al eliminar python-jose) | 43.0.3 |
| Scheduler | APScheduler | 3.10.x |
| Contenedores | Docker + Docker Compose | — |

---

## Separación Core / Premium

### Principio de separación

El Core es el corazón estable de la plataforma. Los módulos Premium son extensiones opcionales. El flujo de dependencia es unidireccional: los módulos Premium pueden importar código del Core; el Core nunca importa código de un módulo Premium.

```
core/ → no importa de modules/     ← invariante de arquitectura
modules/ → puede importar de core/ ← permitido y esperado
modules/A/ → no importa de modules/B/ ← módulos sin acoplamiento entre sí
```

Cualquier violación de esta regla es un defecto de arquitectura que debe corregirse antes de mergearse a `main`.

### Estructura de directorios objetivo (F4)

```
gym-platform/
├── backend/
│   ├── app/
│   │   ├── core/                  ← Platform Core — estable, sin referencias a modules/
│   │   │   ├── config.py          ← Settings + feature flags
│   │   │   └── security.py
│   │   ├── api/
│   │   │   ├── routes/            ← Rutas Core (members, memberships, payments, ...)
│   │   │   └── deps.py
│   │   ├── modules/               ← Módulos Premium — pueden importar core/
│   │   │   ├── notifications/     ← P-01
│   │   │   │   ├── routes.py
│   │   │   │   ├── service.py
│   │   │   │   ├── repository.py
│   │   │   │   └── models.py
│   │   │   ├── payments_online/   ← P-02
│   │   │   ├── digital_ecosystem/ ← P-03
│   │   │   ├── access_control/    ← P-04 + P-05
│   │   │   ├── mobile_api/        ← P-06
│   │   │   ├── body_tracking/     ← P-07
│   │   │   ├── analytics/         ← P-08
│   │   │   └── ai/                ← P-09
│   │   ├── database/
│   │   └── models/                ← Modelos Core
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/                 ← Páginas Core
│       ├── modules/               ← Componentes Premium
│       ├── api/
│       └── types/
├── mobile/                        ← App Móvil (F6) — React Native
├── docker-compose.yml
├── .env.example                   ← Plantilla completa con todos los flags
└── scripts/
    └── setup.sh                   ← Generación automática de secretos
```

---

## Feature Flags

### Mecanismo de activación

Los feature flags son variables de entorno leídas al arranque del proceso por `pydantic-settings`. No existe tabla de configuración en base de datos. Los flags no cambian en caliente: su modificación requiere editar el `.env` y reiniciar el stack Docker.

Este diseño es intencional. La activación de un módulo Premium es un evento de negocio (el cliente contrató el módulo) que debe registrarse en el contrato del proveedor, no un switch que el operador del gimnasio pueda activar autónomamente.

### Convención de nombres y valores

| Módulo | Variable `.env` | Valor por defecto | Descripción |
|---|---|---|---|
| Comunicación Automatizada | `MODULE_NOTIFICATIONS` | `true` ¹ | P-01 |
| Cobros Online | `MODULE_PAYMENTS_ONLINE` | `false` | P-02 (F5) |
| Ecosistema Digital | `MODULE_DIGITAL_ECOSYSTEM` | `false` | P-03 (F5) |
| Control de Acceso | `MODULE_ACCESS_CONTROL` | `false` | P-04 + P-05 (F5/F6) |
| App Móvil | `MODULE_MOBILE_APP` | `false` | P-06 (F6) |
| Seguimiento Corporal | `MODULE_BODY_TRACKING` | `true` ¹ | P-07 |
| Tienda | `MODULE_STORE` | `true` ¹ | Core monetario actual |
| Analítica Avanzada | `MODULE_ANALYTICS` | `false` | P-08 (F5) |
| IA Predictiva | `MODULE_AI` | `false` | P-09 (F7) |

> ¹ Módulos ya en producción en todas las instalaciones actuales usan **opt-out** (`default=True`). Instalaciones nuevas que no contraten el módulo deben establecer explícitamente `MODULE_X=false`. Módulos nuevos a partir de F4-B usan **opt-in** (`default=False`).

### Endpoint de configuración

`GET /api/config/features` — endpoint público, sin autenticación requerida.

Retorna JSON con el estado de todos los módulos activos. El frontend lo consulta al iniciar la aplicación y construye la navegación, rutas y elementos de interfaz dinámicamente según los flags recibidos.

```json
{
  "core": {
    "members": true,
    "memberships": true,
    "attendance": true,
    "payments": true,
    "dashboard": true,
    "auth": true,
    "backup": true
  },
  "premium": {
    "notifications": true,
    "body_tracking": true,
    "store": true
  }
}
```

> Estructura implementada en F4-A. Los módulos Core siempre retornan `true`. Los módulos Premium reflejan el valor del flag `MODULE_*` en `.env`. El agrupamiento `core`/`premium` es la representación canónica del endpoint.

> **Nota sobre defaults (F4-A):** Los módulos ya en producción (notificaciones, seguimiento corporal, tienda) usan `default=True` (opt-out) para preservar compatibilidad con instalaciones existentes que no declaran los flags en `.env`. Módulos nuevos (F4-B+) usarán `default=False` (opt-in).

### Protección en backend

Un módulo con flag en `false` tiene su router **no registrado** en FastAPI al arranque. Las rutas del módulo no existen en la tabla de enrutamiento → HTTP 404 (no 403). No hay guardia de middleware ni dependencia activa que rechace la petición — la ruta simplemente no existe.

**Consecuencia:** si alguien accede directamente a la API, los módulos no contratados devuelven 404 (no accesible), no 403 (denegado). El comportamiento es semánticamente correcto para módulos desactivados en instalación local. Para cloud multi-tenant (F8+) se evaluará si 403 es más adecuado (TD-65).

La desactivación en el frontend (ocultar menús y rutas) es la capa de experiencia de usuario; la no-existencia del router en el backend es la capa de seguridad real.

---

## Separación Producto / Cliente / Configuración

| Capa | Contenido | Dónde vive | Quién lo controla |
|---|---|---|---|
| **Plataforma** | Código fuente, lógica de negocio, módulos | Repositorio `gym-platform` | Equipo de desarrollo |
| **Cliente** | Datos operativos, miembros, membresías, historial | Volumen Docker `gym_db-data` (local en el gymnasio) | El gimnasio |
| **Configuración** | Secretos, flags, nombre del gym, CORS, límites operativos | Archivo `.env` (por instalación, no en repo) | Proveedor en implementación |

**Regla crítica:** el repositorio no contiene datos de ningún cliente. El `.env` está en `.gitignore` y nunca forma parte del repositorio. El volumen de datos no se modifica durante actualizaciones de software.

---

## Proceso de Nueva Instalación

1. El proveedor entrega al operador del gimnasio el **Kit de Instalación**:
   - `docker-compose.yml` genérico (sin nombre de cliente)
   - `.env.example` con todos los parámetros documentados
   - `scripts/setup.sh` — script de configuración guiada

2. El script `setup.sh` genera automáticamente:
   - `SECRET_KEY` (clave Fernet para cifrado de credenciales en BD)
   - `JWT_SECRET_KEY` (secreto para tokens JWT)
   - Solicita interactivamente: `GYM_NAME`, `ADMIN_INITIAL_PASSWORD`, `CORS_ORIGINS`

3. El proveedor activa los módulos Premium contratados estableciendo los flags correspondientes a `true` en el `.env` generado.

4. `docker compose up -d` levanta los tres servicios (backend, frontend, scheduler).

5. El primer arranque del backend ejecuta `init_db()`, inicializa la base de datos y crea el usuario admin con la contraseña temporal definida en `.env`.

6. El operador accede desde el navegador de la red local y completa el cambio de contraseña en el primer login.

El proceso completo no requiere conocimiento técnico del dueño del gimnasio. La guía de instalación incluida en el kit describe cada paso con capturas de pantalla.

---

## Proceso de Actualización

El proceso de actualización nunca modifica los datos del cliente ni la configuración existente.

1. El proveedor notifica al cliente de la nueva versión disponible y el contenido del cambio.
2. El operador del gimnasio (o el proveedor remotamente) ejecuta un **backup manual** desde el panel antes de actualizar.
3. El proveedor entrega o el operador descarga la nueva imagen Docker.
4. `docker compose pull && docker compose up -d --force-recreate` reemplaza los contenedores con la nueva versión.
5. Las migraciones de base de datos se ejecutan automáticamente en el arranque del backend mediante Alembic.
6. Los módulos Premium activos permanecen activos — los flags en `.env` no se modifican salvo cuando se activan módulos nuevos contratados.

Si la actualización falla por cualquier motivo, el backup tomado en el paso 2 permite restaurar el estado anterior en menos de 5 minutos.

---

## Estrategia de Evolución Arquitectónica

La arquitectura actual es el punto de partida correcto para el horizonte de 24 meses. Cada ola de producto es compatible con la siguiente sin reescritura.

### F4 — Platform Ready
**F4-A ✅ Completado (2026-06-19, commit `9f2b12b`):** Feature flags operativos (`MODULE_*` en `.env`). Endpoint `GET /api/config/features` implementado como endpoint público. Scaffolding `backend/app/modules/premium/` para módulos F4-B+. Migración `python-jose` → `PyJWT==2.9.0`. `cryptography` actualizado a `43.0.3`. Sin cambios en la interfaz pública del API Core existente. Tag `v1.1-rhinopower` creado como línea inmutable de cliente.

**F4-B (pendiente):** Módulos P-01 Comunicación Automatizada y P-07 Seguimiento Corporal convertidos a Premium. Frontend consume `GET /api/config/features` dinámicamente.

### F5 — Premium Edition
Primeros módulos Premium activos en producción en instalaciones de clientes reales. Validación en producción de que el boundary `core/ → modules/` se mantiene bajo presión de desarrollo. TLS/HTTPS en Docker para habilitar acceso LAN multi-PC.

### F6 — Digital & Access
App Móvil como primer componente externo al Docker stack (directorio `/mobile` en el mismo repositorio, compilado y distribuido en App Store / Google Play). La app consume el mismo API REST del backend con autenticación JWT estándar. Sin cambios en el API Core para soportar la app — el API ya está diseñado para ser consumido por múltiples clientes.

Integración con hardware biométrico externo mediante SDK del proveedor del lector. El hardware es de terceros; el sistema gestiona la lógica de validación de membresía que decide si el hardware permite o bloquea el acceso.

### F7 — Intelligence
Capa de IA como servicio adicional dentro del stack Docker (contenedor Python independiente con modelo de ML). El modelo consume datos de la base de datos del gimnasio a través de queries de solo lectura. El contenedor de IA no modifica datos — solo genera predicciones que el backend expone como alertas.

### F8+ — Evaluación Cloud (fuera del roadmap 24m)
Si se decide avanzar hacia SaaS: el código de negocio no cambia. El cambio es de infraestructura: SQLite → PostgreSQL, Docker local → plataforma cloud, autenticación por instalación → autenticación multi-tenant. La separación `core/modules/` y la arquitectura de feature flags son compatibles con multi-tenancy sin reescritura del dominio de negocio. La decisión de avanzar a F8 se toma con datos reales de mercado, no de forma anticipada.
