# BASELINE_SEGURIDAD.md

Línea base de seguridad del sistema — **Fase F0** del `ROADMAP_COMERCIALIZACION.md`.
Primera auditoría integral del proyecto (no había auditorías previas).

Documento autocontenido. Es **diagnóstico**: no modifica código. Los hallazgos aquí
listados deben pasar por el **Human Gate** (revisión humana → aprobar/rechazar/diferir)
antes de corregirse en F1 y siguientes.

- **Fecha:** 2026-06-12
- **Alcance:** código backend (`backend/app/`), empaquetado (`Dockerfile`, `docker-compose.yml`, `nginx.conf`, `.env.example`) y dependencias.
- **Método:** OWASP API Security Top 10 + revisión por capas (route→service→repository→model) + empaquetado.
- **Severidad calibrada al destino de producción** (host/Docker, potencialmente internet). Donde el uso actual localhost-dev mitiga, se indica.

---

## E0 — Inventario, frontera de confianza y clasificación de datos

**Stack:** FastAPI + SQLAlchemy 2.x + SQLite · React (Nginx estático) · contenedor `scheduler` (APScheduler).

**Superficie de API (10 routers, todos bajo `/api`):** members, memberships, payments, dashboard, plans, body_measurements, attendance, store, backup, notifications.

**Clasificación de datos (sensibilidad):**

| Dato | Tipo | Sensibilidad |
|---|---|---|
| `members` (nombre, documento, email, teléfono) | PII | Alta |
| `payments`, `store.sales`, `credit_payments` | Financiero | Alta |
| `body_measurements` | **Salud** | Alta |
| `attendance` | Comportamiento | Media |
| `notification_settings.smtp_password` | Credencial (cifrada Fernet) | Alta |
| Backups `gym.db` | Copia íntegra de todo lo anterior | Crítica |

**Frontera de confianza actual:** dev = localhost. Despliegue previsto = Docker con puertos `8000` (API) y `80` (frontend) publicados al host. Trayectoria del roadmap = internet-facing. **Las severidades asumen ese destino.**

---

## Resumen de hallazgos

| ID | Hallazgo | Severidad | Confianza | OWASP API |
|---|---|---|---|---|
| SEC-001 | Ausencia total de autenticación y autorización | **Crítica** | Alta | API2 |
| SEC-002 | Endpoints de pagos (CRUD financiero) accesibles sin auth | **Crítica** | Alta | API1/API5 |
| SEC-003 | Config SMTP escribible y envío de correo sin auth | **Alta** | Alta | API5/API8 |
| SEC-004 | Endpoints de backup sin auth (crear/listar) | **Alta** | Alta | API5 |
| SEC-005 | Puerto del backend publicado sin reverse proxy ni TLS | **Alta** | Alta | API8 |
| SEC-006 | Sin TLS/HTTPS — tráfico en claro | **Alta** | Alta | API8 |
| SEC-007 | Contenedor backend/scheduler corre como root | **Alta** | Alta | API8 |
| SEC-008 | `cryptography 41.0.7` + dependencias desactualizadas (CVEs) | **Alta** | Media | — |
| SEC-009 | `SECRET_KEY` vacía por defecto, sin validación ni enforcement por despliegue | **Alta** | Alta | API8 |
| SEC-010 | Docs OpenAPI (`/docs`,`/redoc`,`/openapi.json`) siempre expuestas | Media | Alta | API8/API9 |
| SEC-011 | `debug=True` por defecto, atado a `settings` | Media | Alta | API8 |
| SEC-012 | CORS `allow_credentials=True` + métodos/headers wildcard | Media | Alta | API8 |
| SEC-013 | Logs 422 registran el `input` del cliente (PII en logs) | Media | Alta | API8 |
| SEC-014 | SQLite y backups sin cifrar en reposo | Media | Alta | — |
| SEC-015 | Sin cabeceras de seguridad HTTP (HSTS, X-Frame-Options, CSP, X-Content-Type-Options) | Media | Alta | API8 |
| SEC-016 | Sin rate limiting (fuerza bruta / abuso de envío) | Media | Alta | API4 |
| SEC-017 | Errores exponen `str(e)` al cliente (fuga de info interna) | Media | Media | API8 |
| SEC-018 | Sin autorización por objeto (BOLA) — prepara F6 | Media | Alta | API1 |
| SEC-019 | Sin `TrustedHostMiddleware` (host header) | Baja | Media | API8 |
| SEC-020 | f-string en DDL de `init_db` (no explotable; inputs internos) | Baja | Alta | — |

---

## Hallazgos detallados

### SEC-001 — Ausencia total de autenticación y autorización · Crítica
- **Ubicación:** todo `backend/app/api/routes/*`. Confirmado: el único `Depends` en el código es `Depends(get_db)`. No hay JWT, OAuth, API key, sesión ni `current_user`.
- **Riesgo:** cualquiera con acceso de red (LAN o internet, según despliegue) lee y modifica clientes, membresías, pagos, asistencia, tienda; crea/borra pagos; cambia configuración. Es la **raíz** de SEC-002, 003, 004.
- **Mitigación actual:** solo localhost-dev. Desaparece al exponer en host.
- **Recomendación:** autenticación de operadores (staff) con roles — **F2**, prerrequisito de cualquier exposición.

### SEC-002 — Pagos CRUD sin auth · Crítica
- **Ubicación:** `api/routes/payments.py` — `POST /members/{id}/payments`, `DELETE /payments/{id}`, `GET /payments`, estadísticas.
- **Riesgo:** lectura total del historial financiero y manipulación (crear/borrar pagos) sin identidad. Fraude y fuga de datos financieros.
- **Recomendación:** auth + autorización (F2); proteger borrado con rol.

### SEC-003 — Config SMTP escribible + envío sin auth · Alta
- **Ubicación:** `api/routes/notifications.py` — `PUT /notifications/settings`, `POST /notifications/test-smtp`, `POST /notifications/run`.
- **Riesgo:** un actor no autenticado puede **sobrescribir la configuración SMTP** (host/usuario/credenciales) y **disparar envíos de correo** a los clientes. Vector de abuso de relay y de redirección de credenciales.
- **Mitiga parcialmente:** `smtp_password` se guarda cifrado (Fernet) y el envío usa STARTTLS con verificación de certificado. Pero la **escritura** de settings y el **disparo** quedan abiertos.
- **Recomendación:** auth + rol administrador para settings y run (F2).

### SEC-004 — Backup sin auth · Alta
- **Ubicación:** `api/routes/backup.py` — `POST /backup/manual`, `GET /backup/list`, `GET /backup/status`.
- **Riesgo:** creación de backups y enumeración de metadatos sin identidad (abuso de recursos, reconocimiento). **No existe endpoint de descarga del archivo**, por lo que la BD no es exfiltrable directamente vía API (por eso Alta, no Crítica).
- **Recomendación:** auth + rol; mantener sin endpoint de descarga directa.

### SEC-005 — Puerto backend publicado sin proxy ni TLS · Alta
- **Ubicación:** `docker-compose.yml` → `ports: "8000:8000"` y `"80:80"`.
- **Riesgo:** en un host con IP pública, la API (y `/docs`) quedan accesibles directamente, sin reverse proxy, sin TLS, sin filtrado.
- **Nota:** bindear `0.0.0.0` dentro del contenedor es correcto; el problema es **publicar el puerto crudo** en el host.
- **Recomendación:** reverse proxy (Caddy/Traefik/Nginx) con TLS delante; no publicar `8000` crudo — **F5**.

### SEC-006 — Sin TLS/HTTPS · Alta
- **Ubicación:** `nginx.conf` (listen 80), compose (sin 443/cert).
- **Riesgo:** credenciales (tras F2), PII y, en premium, datos de pago viajarían en claro.
- **Recomendación:** TLS terminado en el reverse proxy — **F5**.

### SEC-007 — Contenedor como root · Alta
- **Ubicación:** `backend/Dockerfile` — sin directiva `USER`; corre como root. Igual para `scheduler`.
- **Riesgo:** una vulnerabilidad de ejecución en la app otorga root dentro del contenedor, ampliando el impacto.
- **Recomendación:** usuario no-root en la imagen — **F1**.

### SEC-008 — Dependencias desactualizadas · Alta
- **Ubicación:** `backend/requirements.txt`. Versiones de 2023: fastapi 0.104.1, uvicorn 0.24.0, sqlalchemy 2.0.23, pydantic 2.5.0, apscheduler 3.10.4, **cryptography 41.0.7**.
- **Riesgo:** `cryptography 41.0.7` (la que cifra `smtp_password`) tiene CVEs conocidas corregidas en ≥42.x. El resto acumula correcciones de seguridad.
- **Recomendación:** actualizar y adoptar `pip-audit`/`npm audit` en el flujo — **F1**.

### SEC-009 — SECRET_KEY vacía por defecto · Alta
- **Ubicación:** `core/config.py` → `secret_key: str = ""`; `services/crypto_service.py` lanza solo al usarse.
- **Riesgo:** (a) arranca con cifrado deshabilitado sin avisar (TD-30); (b) si se reutiliza la misma `SECRET_KEY` entre los dos despliegues vendidos, comprometer uno permite descifrar el otro.
- **Recomendación:** validación de arranque + **secreto único por despliegue**, nunca compartido — **F1**.

### SEC-010 — Docs OpenAPI siempre expuestas · Media (Alta si internet)
- **Ubicación:** `main.py` — no se pasan `docs_url=None`/`openapi_url=None`.
- **Riesgo:** enumeración completa de endpoints y esquemas.
- **Recomendación:** deshabilitar en producción — **F1**.

### SEC-011 — debug=True por defecto · Media
- **Ubicación:** `core/config.py` → `debug: bool = True`; `main.py` → `debug=settings.debug`.
- **Riesgo:** si `.env` falta o se despliega mal, los 500 devuelven traceback. `.env.example` trae `DEBUG=false`, pero el **default del código** es inseguro.
- **Recomendación:** `False` forzado en perfil de producción — **F1**.

### SEC-012 — CORS laxo · Media
- **Ubicación:** `main.py` — `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
- **Riesgo:** superficie CORS amplia; cobra relevancia al introducir cookies/sesión (F2).
- **Recomendación:** orígenes, métodos y headers explícitos — **F1**.

### SEC-013 — PII en logs 422 · Media
- **Ubicación:** `main.py` — el handler registra `exc.errors()`, que en Pydantic v2 incluye el campo `input` enviado por el cliente.
- **Riesgo:** datos personales en logs en texto plano.
- **Recomendación:** omitir/sanitizar `input`; nivel `warning` — **F1**.

### SEC-014 — Datos en reposo sin cifrar · Media
- **Ubicación:** volumen `db-data` (SQLite + backups en `/app/data`).
- **Riesgo:** robo/acceso al host expone toda la BD y sus copias.
- **Recomendación:** cifrado del volumen/host y custodia de backups — **F5** (premium) / guía operativa (local).

### SEC-015 — Sin cabeceras de seguridad HTTP · Media
- **Ubicación:** `nginx.conf` — sin HSTS, X-Frame-Options, X-Content-Type-Options, CSP, Referrer-Policy.
- **Riesgo:** clickjacking, sniffing de tipo, ausencia de forzado HTTPS.
- **Recomendación:** añadir cabeceras en el proxy/nginx — **F1/F5**.

### SEC-016 — Sin rate limiting · Media
- **Riesgo:** fuerza bruta (tras F2), scraping de datos, abuso de `notifications/run`.
- **Recomendación:** rate limiting en el reverse proxy o middleware — **F5**.

### SEC-017 — Fuga de `str(e)` al cliente · Media
- **Ubicación:** `backup.py` y `notifications.py` — `HTTPException(detail=str(e))`.
- **Riesgo:** mensajes internos/trazas parciales al cliente.
- **Recomendación:** mensajes genéricos al cliente; detalle solo en logs — **F1**.

### SEC-018 — Sin autorización por objeto (BOLA) · Media (forward-looking)
- **Ubicación:** rutas con `{member_id}`/`{id}` (p. ej. `/members/{id}/payments`, `/measurements`).
- **Riesgo:** hoy cubierto por la ausencia total de auth (todo o nada). Al dar cuentas a **miembros** (F6), sin authZ por objeto el miembro A accedería a datos del miembro B.
- **Recomendación:** autorización por objeto al construir el portal de miembros — **F6**.

### SEC-019 — Sin TrustedHostMiddleware · Baja
- **Riesgo:** host header rebinding en despliegue expuesto.
- **Recomendación:** `TrustedHostMiddleware` con hosts permitidos — **F1/F5**.

### SEC-020 — f-string en DDL de migración · Baja (no explotable)
- **Ubicación:** `database/init_db.py:26` `ALTER TABLE {table} ADD COLUMN {ddl}` y `PRAGMA index_info({row[1]})`.
- **Riesgo:** **no explotable** — `table`/`ddl`/`row` son valores internos hardcodeados, no input externo. Se registra solo como defensa en profundidad.
- **Recomendación:** sin acción urgente; documentar invariante "inputs estáticos".

---

## Lo que ya está bien (postura positiva)

- **Sin inyección SQL encontrada:** ORM SQLAlchemy + `text()` con parámetros enlazados (`:sid`, `:s`). El único SQL con f-string usa valores internos (SEC-020).
- **Validación de entrada:** Pydantic v2 en todos los payloads (tipos Upsert separados de Read).
- **`smtp_password` cifrado en reposo** con Fernet.
- **SMTP con STARTTLS** y `ssl.create_default_context()` (verifica certificado).
- **`.dockerignore` y `.gitignore` excluyen `.env` y `*.db`** — secretos no entran a la imagen ni al repo.
- **Manejo de errores de negocio** correcto (p. ej. documento duplicado → 409, no 500 sin CORS).
- **Backups automáticos** ya implementados (TD-26 resuelto).

---

## Brecha hacia el escenario web + móvil + pagos (Premium)

Lo que falta para soportar con seguridad la edición Gestionada, mapeado a fases:

| Requisito faltante | Hallazgos relacionados | Fase |
|---|---|---|
| Auth de staff | SEC-001, 002, 003, 004 | F2 |
| TLS + reverse proxy | SEC-005, 006, 016 | F5 |
| Contenedor endurecido + secretos por despliegue + deps al día | SEC-007, 008, 009 | F1 |
| PostgreSQL (concurrencia web/móvil/webhooks) | — (SQLite no escala a API pública) | F4 |
| Auth de miembros + autorización por objeto (BOLA) | SEC-018 | F6 |
| Integración PSP + verificación de webhooks + confirmación server-side | — (no existe capa de pagos online) | F7 |
| Cumplimiento Habeas Data (Ley 1581/2012) | datos PII/salud/financieros de terceros | F9 |

---

## Resumen y prioridades

| Prioridad | Hallazgos | Acción |
|---|---|---|
| **Bloqueante para exponer a red** | SEC-001, 002, 003, 004, 005, 006 | Auth (F2) + TLS/proxy (F5) antes de cualquier publicación |
| **Endurecimiento inmediato (F1)** | SEC-007, 008, 009, 010, 011, 012, 013, 017 | Imagen no-root, deps al día, perfil prod, secreto por despliegue |
| **Defensa en profundidad** | SEC-014, 015, 016, 019 | Cifrado en reposo, cabeceras, rate limit, trusted host |
| **Forward-looking** | SEC-018 (BOLA) | Resolver al construir portal de miembros (F6) |
| **Sin acción urgente** | SEC-020 | Documentar invariante |

**Veredicto:** la lógica de negocio es sólida y sin inyección, pero **el sistema no está listo para exponerse a una red no confiable**: la ausencia total de autenticación (SEC-001) y de TLS, sumada a endpoints sensibles abiertos (pagos, SMTP, backup), lo hacen inseguro para venta en host/internet en su estado actual. Para la **edición Local en LAN** el riesgo es mucho menor, pero SEC-007/008/009/013 deben corregirse igual.

---

## Matriz de priorización definitiva — contexto Local (2 instalaciones)

Alcance bloqueado a **las dos instalaciones Local actuales**. No hay cliente SaaS/Premium,
ni requerimiento aprobado de portal web de miembros, app móvil o pagos online. Los riesgos
exclusivos de esos escenarios quedan **diferidos a fases futuras** y **no bloquean F1**.

**Reglas de priorización (contexto Local):**
- **P0** = obligatorio antes de instalar en los dos gimnasios.
- **P2** = recomendable / bajo esfuerzo (no bloquea).
- **P3** = deuda técnica aceptable.
- **Diferido** = riesgo exclusivo de SaaS/internet/portal/pagos; documentado, no aplica al alcance actual.

### Bloque A — F1: obligatorio para instalar (P0)

| ID | Hallazgo | Severidad | Impacto Local | Complejidad | Prio |
|---|---|---|---|---|---|
| SEC-005 | Puerto expuesto → bindear a `127.0.0.1` | Alta | Alto | Baja | **P0** |
| SEC-007 | Contenedor corre como root | Alta | Medio | Baja | **P0** |
| SEC-009 | `SECRET_KEY` vacía / key única por install | Alta | Medio | Baja | **P0** |
| SEC-011 | `debug=True` por defecto → forzar `False` | Media | Medio | Baja | **P0** |
| SEC-013 | PII en logs 422 (Habeas Data) | Media | Medio | Baja | **P0** |

5 hallazgos, todos de baja complejidad. **Este es el contenido de F1.** No requiere confirmar topología ni clasificación de frontends.

### Bloque B — Local, posterior o bajo esfuerzo (no bloquea F1)

| ID | Hallazgo | Severidad | Impacto Local | Prio | Fase / Nota |
|---|---|---|---|---|---|
| SEC-001 | Ausencia de auth | Crítica | según topología | **P0/P2** | **F2** — P0 si LAN multi-dispositivo · P2 si PC única aislada |
| SEC-002/003/004 | Pagos / SMTP / backup sin auth | Crítica/Alta | = SEC-001 | = SEC-001 | F2 (cubiertos al implementar auth) |
| SEC-008 | Deps con CVEs | Alta | Bajo (no explotable en nuestro uso) | **P2** | Hacer en F1 si es barato |
| SEC-010 | Docs OpenAPI expuestas | Media | Bajo | **P2** | Deshabilitar |
| SEC-012 | CORS wildcard | Media | Bajo | **P2** | ×2 frontends |
| SEC-015 | Sin cabeceras de seguridad | Media | Bajo | **P2** | ×2 frontends |
| SEC-017 | Fuga `str(e)` al cliente | Media | Bajo | **P2** | — |
| SEC-014 | Datos sin cifrar en reposo | Media | Bajo (robo físico) | **P2** | — |
| SEC-020 | f-string DDL (no explotable) | Baja | N-A | **P3** | Documentar invariante |

### Bloque C — Diferidos a fases futuras (no Local · documentar · no bloquean F1)

| ID | Hallazgo | Aplica a | Fase |
|---|---|---|---|
| SEC-006 | Sin TLS/HTTPS | Internet / VPN | F5 |
| SEC-016 | Sin rate limiting | Internet | F5 |
| SEC-018 | Sin autorización por objeto (BOLA) | Portal de miembros | F6 |
| SEC-019 | Sin `TrustedHostMiddleware` | Internet | F5 |

Sin requerimiento aprobado (sin SaaS, portal, pagos ni internet). Registrados para fases futuras.

### Revalidación SEC-008 (CVEs)

Las CVEs de las dependencias (cryptography 41.0.7, starlette, idna, etc.) son **DoS** o requieren
operaciones que **nuestra app no realiza** (RSA PKCS1v15, PKCS12 — usamos solo Fernet; API JSON sin
multipart). **Ninguna es RCE ni explotable de alta severidad en LAN.** Por eso baja de P0 a **P2** en
el contexto Local (vuelve a P1 en internet/Premium). Verificación autoritativa pendiente: `pip-audit`.

### Datos abiertos (no bloquean F1)

| Pendiente | Afecta a | Cuándo resolverlo |
|---|---|---|
| Topología real de cada gimnasio (PC única vs LAN multi-dispositivo) | Prioridad de auth (SEC-001/002/003/004) | Antes de **F2** |
| Frontends ¿Caso A (branding) o B (funcional)? | Deuda estructural + costo ×2 de SEC-012/015 | **Pendiente de clasificación** — sin registrar en TECH_DEBT hasta confirmar |

---

## Próximo paso

**Human Gate completado** (revisión y aprobación del usuario, 2026-06-12): se aprueba ejecutar
**F1 — Endurecimiento del empaquetado = Bloque A** (SEC-005, 007, 009, 011, 013) vía
`paso1-valor` → `paso8`. Auth (Bloque B / F2) queda secuenciada tras confirmar topología.
El factor "dos frontends" permanece **pendiente de clasificación** antes de registrarse en `TECH_DEBT.md`.
