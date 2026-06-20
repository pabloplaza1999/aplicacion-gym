# ROADMAP_COMERCIALIZACION.md

> **ARCHIVADO — 2026-06-19**
> Este documento describe el roadmap original pre-plataforma (F0–F9 con modelo dual Local/Gestionado).
> Su estado actual contradice el proyecto real: F4 aquí = PostgreSQL; F4 real = Platform Ready (feature flags).
> Contenido migrado activo:
> - §5 (subagente security-auditor + Human Gate) → `PLATFORM_ARCHITECTURE.md`
> - §8 (estrategia de modelo de IA por fase) → `PRODUCT_ROADMAP.md`
> Referencias históricas a este archivo en `docs/BASELINE_SEGURIDAD.md` y `docs/RELEASE_F1_BLOQUE_A.md` son válidas como registro de lo ejecutado.

Hoja de ruta para llevar el sistema de gestión de gimnasio desde su estado actual
(herramienta local madura) hasta un **producto comercializable en dos ediciones**,
incluyendo la edición premium con web, app móvil y pagos online de membresía.

Documento autocontenido: cualquier desarrollador o modelo debe poder entender la
estrategia y el orden de ejecución sin acceder al historial de conversación.

> **Estado de este roadmap:** PLANEACIÓN. Aún no se ha implementado nada de lo aquí
> descrito. Cada fase se ejecuta mediante la metodología existente del proyecto
> (`paso1-valor` → `paso8-cierre`).

---

## 1. Modelo de producto: dos ediciones sobre un mismo código

La aplicación se comercializa en dos niveles que cubren necesidades y presupuestos
distintos. **Ambas ediciones salen del mismo código fuente**; las diferencias se
controlan por configuración (feature flags), nunca por bifurcación de código.

| | Edición **Local** (Básica) | Edición **Gestionada** (Premium) |
|---|---|---|
| Público | Gimnasios pequeños | Gimnasios que quieren web/móvil/pagos |
| Despliegue | Auto-hospedado: Docker en una PC del gym (LAN) | Hospedado por nosotros (contenedor + BD por cliente) |
| Red | LAN, sin exposición a internet | API pública internet-facing con TLS |
| Pago del cliente | **Pago único** (corre en su hardware) | **Suscripción** (cubre hosting + pasarela + mantenimiento) |
| Base de datos | SQLite (suficiente para ~100 clientes) | PostgreSQL (concurrencia web/móvil + webhooks) |
| Web pública | No | Sí |
| App móvil | No | Sí |
| Pagos online de membresía | No | Sí (vía pasarela/PSP) |
| Auth | Operadores (staff) | Staff + **miembros** |
| Parcheo de seguridad | Responsabilidad del cliente o mantenimiento pago | Centralizado (parchamos una vez → todos) |

**Por qué este modelo:** el "pago único" es incompatible con que nosotros hospedemos
(el host corre 24/7 y cuesta cada mes). La web + móvil + pagos "desde cualquier lugar"
es técnicamente imposible en LAN (la app móvil no alcanza una PC del gym). Por tanto
cada capacidad cae naturalmente en una edición distinta, pero **un solo código** las
sirve a ambas.

---

## 2. Principio transversal innegociable: un solo código + feature flags

La mayor fuente de deuda de seguridad sería **bifurcar el código por cliente**. Cada
fork multiplica el costo de aplicar un parche de seguridad (hay que portarlo a N ramas).

Reglas permanentes:

1. **Cero forks por cliente.** Las diferencias entre ediciones y las personalizaciones
   por cliente viven en **flags de configuración** (`portal_pagos`, `tienda`, etc.),
   no en ramas de código.
2. Un cliente que pida una mejora → se construye detrás de un flag (`feature.X = true`
   en su despliegue); otro cliente queda con `false`. Mismo parche de seguridad para ambos.
3. Una personalización solo justifica una rama si es estructuralmente incompatible, y en
   ese caso **se cobra el desarrollo a medida incluyendo su mantenimiento perpetuo**.
4. Un fix de seguridad debe poder llegar a todos los clientes (Local o Gestionado,
   personalizado o no) sin back-ports.

---

## 3. Mapa de fases

Las fases F0–F3 son **sin arrepentimiento** (sirven a ambas ediciones y deben hacerse
primero). F4–F8 construyen la edición Premium. F9 es operación continua.

| Fase | Nombre | Sirve a | Bloquea a |
|---|---|---|---|
| **F0** | Línea base de seguridad | Ambas | Todo |
| **F1** | Endurecimiento del empaquetado | Ambas | F2, F5 |
| **F2** | Autenticación y autorización (staff) | Ambas | F5, F6 |
| **F3** | Frontera de feature flags + Edición Local empaquetada | Ambas | F5 (Premium) |
| **F4** | Migración a PostgreSQL | Premium | F5, F7 |
| **F5** | Infraestructura hosted (A1) | Premium | F6, F7, F8 |
| **F6** | Auth de miembros + portal web | Premium | F7, F8 |
| **F7** | Integración de pagos (PSP) | Premium | F8 |
| **F8** | App móvil | Premium | — |
| **F9** | Cumplimiento + operación continua | Ambas | — |

**Hito 1 — Primer producto vendible endurecido:** al cerrar **F3** existe la Edición
Local lista para vender (pago único, LAN, segura por defecto).

**Hito 2 — Producto premium:** al cerrar **F7** existe pago de membresía online desde web;
**F8** lo extiende a móvil.

---

## 4. Detalle por fase

Cada fase produce un entregable verificable y pasa por un **gate de seguridad** antes de
cerrarse. La ejecución sigue el flujo `paso1` → `paso8` del proyecto.

### F0 — Línea base de seguridad
- **Objetivo:** saber de dónde se parte. Auditoría integral inicial (no había auditorías previas).
- **Entregable:** `docs/BASELINE_SEGURIDAD.md` con hallazgos triados (Severidad + Confianza)
  y un apartado "brecha hacia el escenario web+móvil+pagos".
- **Alcance de auditoría:** inventario y frontera de confianza (E0); auth/authZ (E1);
  endpoints sensibles `backup`/`payments`/`notifications` (E2); configuración —CORS, `debug`,
  docs, `0.0.0.0`, secretos `.env`— (E3); inyección/validación (E4); datos en reposo —SQLite,
  backups, logs con PII— (E5); dependencias `pip-audit`/`npm audit` (E6). Mapeado a **OWASP API Top 10**.
- **Gate:** ninguno (es el diagnóstico base).

### F1 — Endurecimiento del empaquetado
- **Objetivo:** imagen y configuración seguras por defecto. Sirve a Local y Gestionado.
- **Entregables:**
  - Perfil **dev vs producción** dirigido por entorno: `debug=False` forzado en prod,
    `/docs` y `/redoc` deshabilitados en prod, CORS con dominios explícitos.
  - Imagen Docker endurecida: usuario no-root, sin secretos en capas de la imagen, base mínima.
  - Secretos **por despliegue** (`SECRET_KEY`, BD, credenciales de correo) inyectados, nunca en la imagen ni en el repo.
  - Validación de arranque de `SECRET_KEY` (cierra TD-30).
  - Sanitizar logs 422 para no registrar el `input` del cliente (hallazgo de la auditoría de `main.py`).
- **Nota técnica `0.0.0.0`:** dentro de Docker es correcto; el control real es no publicar el
  puerto crudo en el host y poner un reverse proxy con TLS delante (se materializa en F5 para Premium).
- **Gate:** re-auditar config de producción; confirmar que ningún secreto queda en la imagen/repo.
- **Despliegue Bloque A:** procedimiento oficial en `docs/RELEASE_F1_BLOQUE_A.md` (checklist de pre-despliegue, pasos de rebuild/recreate, rollback y validación post-release para las dos instalaciones Local).

### F2 — Autenticación y autorización (staff)
- **Objetivo:** ningún endpoint operativo accesible sin identidad. Prerrequisito para exponer a internet.
- **Entregables:** login de operadores, roles (dueño/recepción), sesiones/JWT, dependencia de
  auth a nivel de aplicación, protección crítica de `backup` y `payments`.
- **Gate:** verificar que todo router sensible exige auth; probar acceso no autenticado (debe fallar).

### F3 — Frontera de feature flags + Edición Local empaquetada
- **Objetivo:** entregar la Edición Local lista para vender y dejar definida la frontera de flags.
- **Entregables:**
  - Catálogo de flags (`portal_pagos=off`, `tienda`, etc.) leídos de config por despliegue.
  - Paquete de Edición Local: Docker para PC del gym (LAN), pago único, instalación documentada.
  - Documento de entrega/instalación para el cliente Local.
- **Gate:** auditoría del paquete Local (superficie reducida por ser LAN).
- **HITO 1:** primer producto vendible endurecido.

### F4 — Migración a PostgreSQL (solo Premium)
- **Objetivo:** soportar concurrencia web + móvil + webhooks de pago. SQLite no aguanta múltiples
  escritores en una API pública.
- **Entregables:** capa de acceso a BD agnóstica del motor, scripts de migración SQLite→Postgres,
  Postgres para despliegues Gestionados. **SQLite se mantiene para la Edición Local.**
- **Relacionado:** al recrear el esquema, omitir `sales.member_id` legado (TD-19).
- **Gate:** verificar integridad de datos migrados; pruebas de concurrencia.

### F5 — Infraestructura hosted A1 (solo Premium)
- **Objetivo:** plataforma donde cada cliente Gestionado tiene su **propio contenedor + BD** (aislamiento).
- **Entregables:** VPS/host administrado, orquestación contenedor+BD por cliente, **reverse proxy con TLS**,
  gateway/routing (enrutar miembro → su gimnasio), backups centralizados, monitoreo, y una
  **vía de actualización/parcheo** central.
- **Gate:** auditoría de infraestructura — TLS válido, puertos no expuestos crudos, aislamiento entre clientes,
  secretos por despliegue, backups verificados.

### F6 — Auth de miembros + portal web (solo Premium)
- **Objetivo:** que el miembro (no solo el staff) tenga cuenta y vea su membresía en la web.
- **Entregables:** identidad de miembros, portal web, **autorización por objeto (BOLA, OWASP API1)** —
  el miembro A no puede ver/pagar la membresía del miembro B.
- **Relacionado:** cédula obligatoria para identidad de miembro (TD-03).
- **Gate:** pruebas de BOLA (intentar acceder a recursos de otro miembro debe fallar); pruebas de account takeover.

### F7 — Integración de pagos (PSP) (solo Premium)
- **Objetivo:** pagar la membresía online desde la web, con seguridad de pagos correcta.
- **Regla de oro:** **el backend nunca toca datos de tarjeta.** Se integra una pasarela/PSP
  (en Colombia: Wompi, PayU, Mercado Pago, ePayco, Bold) con checkout alojado/tokenización →
  queda en alcance PCI SAQ-A, fuera del PCI DSS pesado.
- **Entregables:**
  - Checkout vía PSP (la tarjeta va directo al PSP; el backend solo ve token/confirmación).
  - **Confirmación server-side**: el estado "pagado" se confirma contra el PSP, jamás por lo que diga el cliente.
  - **Webhooks** del PSP con verificación de **firma HMAC**, **idempotencia** y **anti-replay**.
  - Secretos del PSP por despliegue.
  - Activación de `portal_pagos=on` en Gestionado.
- **Gate:** auditoría de flujo de pago — ¿se confirma server-side? ¿el webhook verifica firma?
  ¿es idempotente? Nuevo hallazgo crítico vigilado: "estado de pago basado en input del cliente sin confirmación del PSP".
- **HITO 2:** pago de membresía online desde web.

### F8 — App móvil (solo Premium)
- **Objetivo:** extender web + pagos a móvil consumiendo la misma API.
- **Entregables:** app móvil (p. ej. React Native) contra la API existente; pago de membresía desde el móvil.
- **Gate:** auditoría de la superficie móvil (almacenamiento de tokens, transporte TLS, reuso de la auth de F6).

### F9 — Cumplimiento + operación continua (ambas)
- **Objetivo:** sostenibilidad legal y de seguridad en el tiempo.
- **Entregables:**
  - **Habeas Data — Ley 1581/2012** (Colombia): política de tratamiento de datos personales;
    aplica porque se procesan PII, pagos y datos de salud de terceros (miembros de los gimnasios cliente).
  - El subagente `security-auditor` operando con **Human Gate** sobre cada cambio futuro (ver §5).
  - Parcheo central periódico (Gestionado) y procedimiento de actualización (Local).
- **Gate:** revisión periódica de la línea base contra deriva.

---

## 5. Transversal: subagente `security-auditor` + Human Gate

A partir de F0, las auditorías de cambios futuros se delegan a un subagente de solo lectura
con flujo de aprobación humana obligatorio.

**Identidad y restricciones**
- Solo lectura. Herramientas: `Read, Grep, Glob`. Sin `Edit`/`Write`/`Bash` mutante.
  Su incapacidad técnica de modificar código *es* la primera mitad del gate.
- Alcance por defecto: el diff de la rama actual. Modo alterno: ruta objetivo.
- Alcance ampliado por este roadmap: además del código, audita **artefactos de despliegue**
  (`Dockerfile`, `docker-compose*.yml`, `.env.example`, `*.bat`) y, en Premium,
  **flujos de pago y handlers de webhook**.

**Esquema de reporte (por hallazgo)**
```
[SEC-NNN] <título>
Severidad:  Crítica | Alta | Media | Baja
Confianza:  Alta | Media | Baja
Ubicación:  archivo:línea
Riesgo:     <ruta de explotación en este contexto>
Recomendación: <fix mínimo, sin código>
OWASP:      <APIx>
```

**Escalas (calibradas a este proyecto)**

| Severidad | Criterio |
|---|---|
| Crítica | Explotable desde internet/LAN sin auth; exposición de pagos/PII/salud o descarga de BD |
| Alta | Explotable con condiciones; escalada de privilegios; falta de authZ por objeto |
| Media | Requiere acceso previo; defensa en profundidad ausente |
| Baja | Hardening / buena práctica sin ruta de explotación directa |

| Confianza | Criterio |
|---|---|
| Alta | Confirmado en código, ruta clara |
| Media | Probable, depende de contexto fuera del archivo |
| Baja | Heurístico, requiere verificación manual |

> Regla de cobertura: **reportar todo**, incluido Baja/Baja. El filtrado lo hace el humano en el
> gate, no el auditor.

**Máquina de estados del Human Gate**
```
AUDITAR (subagente, solo lectura)
   └─► HALLAZGOS.md (artefacto, IDs SEC-NNN)
         └─► REVISIÓN HUMANA (en el hilo principal)
               ├─ APROBADO  ─┐
               ├─ RECHAZADO ─┼─► registra decisión + razón
               └─ DIFERIDO  ─┘     (RECHAZADO/DIFERIDO → TECH_DEBT.md)
                     │
                     └─► APLICAR (solo IDs APROBADOS, vía paso4-implementar)
                           └─► RE-AUDITAR los IDs aplicados (cierra el ciclo)
```

**Reglas invariantes del gate**
1. El auditor nunca toca el código fuente; solo produce el artefacto.
2. Solo los IDs `APROBADO` pasan a `paso4-implementar`.
3. `RECHAZADO`/`DIFERIDO` se registran en `TECH_DEBT.md` con razón.
4. Tras aplicar, re-auditoría obligatoria de esos IDs.
5. La orquestación ocurre en el hilo principal: el subagente auditor **no** invoca directamente
   al de desarrollo; el traspaso es por `HALLAZGOS.md`.

---

## 6. Decisiones pendientes (bloqueantes por fase)

| Decisión | Necesaria antes de | Estado |
|---|---|---|
| Modelo de hosting confirmado = A1 (contenedor+BD por cliente) | F5 | Recomendado, por confirmar |
| ¿Cada cliente con su propia BD y secretos? (sí, por aislamiento) | F5 | Recomendado, por confirmar |
| Selección de PSP colombiano (Wompi/PayU/Mercado Pago/ePayco/Bold) | F7 | Pendiente |
| Frontera concreta de flags (qué es Local vs Premium) | F3 | Pendiente |
| Stack de la app móvil (React Native u otro) | F8 | Pendiente |

---

## 7. Relación con la deuda técnica existente

Elementos de `TECH_DEBT.md` que este roadmap convierte en relevantes o bloqueantes:

- **TD-03** (cédula no obligatoria): resolver en **F6** (identidad de miembros depende de un identificador estable).
- **TD-19** (`sales.member_id` legado): omitir al recrear el esquema en **F4** (migración Postgres).
- **TD-30** (SECRET_KEY no validada en arranque): resolver en **F1** (endurecimiento).
- **TD-26** (backup automático): ✅ resuelto; en **F5** se centraliza para Gestionado.
- **TD-04** (UTC en `check_in_date`): independiente, pero revisar antes de exponer datos a miembros (F6).

---

## 8. Modelo de IA recomendado por fase

Estrategia de selección de modelo de Claude para ejecutar este roadmap con el mejor
costo-beneficio. **La estrategia óptima es variar entre modelos, no usar uno solo.**

**Heurística:** *Diseño y gates de seguridad → Opus 4.8. Implementación → Sonnet 4.6 alto.
Exploración/búsqueda → Haiku 4.5.* Donde un bug pasado por alto causa daño real (auditorías,
auth, pagos, webhooks, BOLA) el modelo más inteligente paga su costo; donde el plan ya está
aprobado y solo se ejecuta, Sonnet rinde igual consumiendo mucha menos cuota.

| Fase | Modelo recomendado | Por qué |
|---|---|---|
| F0 auditoría base | **Opus 4.8** | Detección de vulnerabilidades = máximo riesgo |
| F1 endurecimiento | Diseño Opus → aplica Sonnet | Config sensible; ejecución mecánica |
| F2 auth staff | Opus (diseño) → Sonnet (impl) | El diseño de auth no admite errores |
| F3 flags + Edición Local | **Sonnet 4.6 alto** | Empaquetado, mayormente mecánico |
| F4 migración Postgres | Sonnet → Opus revisa migración | Bien definido; Opus valida integridad |
| F5 infra/TLS | Opus (diseño) → Sonnet (config) | TLS/aislamiento = crítico |
| F6 auth miembros + BOLA | **Opus 4.8** | Autorización por objeto, alto riesgo |
| F7 pagos/webhooks | **Opus 4.8** | El punto de mayor riesgo del proyecto |
| F8 móvil | Sonnet → Opus revisa tokens/transporte | Impl rutinaria; auth crítica |
| F9 cumplimiento + auditor | **Opus 4.8** | Las corridas del subagente `security-auditor` |

**Patrón:** diseño y gates en Opus; implementación en Sonnet. Cada gate de seguridad corre en
Opus aunque la fase se haya implementado en Sonnet.

**Mecánica en Claude Code:**
- Cambiar de modelo con `/model` en cualquier momento.
- El subagente `security-auditor` se fija a Opus en su frontmatter (`model: opus`) mientras el
  flujo de implementación corre en Sonnet — así audita siempre con el mejor modelo sin cambios manuales.

**Costo en plan Pro:** no se paga por token, pero Opus/Fable consumen los límites de uso
notablemente más rápido que Sonnet. Por eso se reserva Opus para los momentos de alto
apalancamiento (auditorías y gates) y Sonnet queda como caballo de batalla. **Fable 5** solo si
Opus 4.8 se traba en algo muy difícil (rara vez; quema cuota al doble).

---

## 9. Próximo paso recomendado

Ejecutar **F0 — Línea base de seguridad**: generar `docs/BASELINE_SEGURIDAD.md` con el estado
actual (código + Docker) y la brecha hacia el escenario web+móvil+pagos. Es el primer paso en
cualquier escenario y no implica modificar código.
