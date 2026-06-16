# RELEASE_F1_BLOQUE_A.md

**Procedimiento oficial de despliegue — F1 Bloque A (Endurecimiento del empaquetado).**

Este documento es el runbook autoritativo para aplicar el endurecimiento F1 Bloque A en las
**dos instalaciones Local** existentes. Es operativo: lo ejecuta el técnico de despliegue.
No describe cambios de código; el código correspondiente ya está publicado en `origin/main`
(commit `d2feaea`, feature `2861e8e`).

**Cambios que aplica este release:**
- Contenedores no-root (`gymuser`) + reconciliación idempotente de permisos del volumen (SEC-007).
- `SECRET_KEY` obligatoria en producción (SEC-009).
- `debug=False` por defecto (SEC-011).
- Bind parametrizado `BIND_ADDR` con default loopback (SEC-005).
- Logs de validación 422 sin PII (SEC-013).

**Regla de oro:** desplegar **un gimnasio primero (canary)**, validarlo por completo, y solo
entonces el segundo.

---

## Advertencias críticas previas

1. **`SECRET_KEY` es obligatoria.** Con `DEBUG=false`, el backend **no arranca** sin
   `SECRET_KEY`. Un gimnasio que nunca configuró notificaciones probablemente **no la tiene**:
   debe generarse **antes** del recreate o el backend entrará en crash-loop.
2. **No cambiar una `SECRET_KEY` existente.** Si el gimnasio ya usa SMTP, su `smtp_password`
   está cifrado con la clave actual; cambiarla **rompe el descifrado**.
   Regla: *si existe, se conserva; si no existe, se genera.*

---

## A. Checklist de pre-despliegue (por gimnasio)

- [ ] **Topología confirmada:** ¿PC única o LAN multi-dispositivo? (determina `BIND_ADDR` y si
  hay que rebuild del frontend).
- [ ] **`SECRET_KEY`:**
  - [ ] ¿Existe ya en el `.env`? → **conservarla**.
  - [ ] ¿No existe? → generar una **única** para este gimnasio:
    `docker run --rm python:3.11-slim python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
  - [ ] Confirmar que **no se reutiliza** la misma clave entre los dos gimnasios.
- [ ] **`BIND_ADDR` definido en `.env`:**
  - PC única → `BIND_ADDR=127.0.0.1` (default).
  - Multi-dispositivo → `BIND_ADDR=<IP-LAN-de-la-PC>` (o `0.0.0.0`) **y**
    `VITE_API_URL=http://<IP-LAN>:8000` (requiere rebuild del frontend).
    Nota: sin autenticación (F2), exponer en LAN es un riesgo residual aceptado.
- [ ] **`.env` completo y coherente:** `DEBUG=false`, `DATABASE_URL=sqlite:////app/data/gym.db`,
  `CORS_ORIGINS`, `VITE_API_URL` acorde a la topología.
- [ ] **Respaldo previo realizado** (sección B.1) y verificado (archivo existe y pesa > 0).
- [ ] **Ventana de mantenimiento** acordada (downtime breve durante recreate).
- [ ] **Acceso a la PC** del gimnasio y a Docker operativo.
- [ ] **Verificaciones previas al rebuild:**
  - [ ] `git status` limpio en la copia del gimnasio (o confirmar que no hay cambios locales que
    se perderían).
  - [ ] `docker compose ps` muestra los 3 servicios actuales sanos (estado de partida conocido).
  - [ ] Espacio en disco suficiente para la nueva imagen.

---

## B. Procedimiento de despliegue paso a paso

Ejecutar en la PC del gimnasio, desde la carpeta del proyecto. Estado de partida: contenedores
antiguos corriendo.

### B.1 — Backup previo (obligatorio)

Copiar la BD **fuera** del volumen, al host:

```bash
docker run --rm -v appparagym_db-data:/data -v "%CD%\backups_host":/backup alpine \
  sh -c "cp /data/gym.db /backup/gym_PRE_F1_$(date +%Y-%m-%d_%H-%M).db"
```

- [ ] Verificar que el archivo existe en `backups_host\` y pesa > 0.
- [ ] (Opcional, refuerzo) Disparar un backup manual desde el Dashboard antes de tumbar.

### B.2 — Actualización del código

```bash
git fetch origin
git log --oneline -1 origin/main      # debe mostrar d2feaea
git checkout main && git pull origin main
```

- [ ] Confirmar que `HEAD` = `d2feaea` (F1 Bloque A publicado).

### B.3 — Rebuild de imágenes (no recrea aún)

Retaggear las imágenes actuales para habilitar rollback y luego construir:

```bash
docker tag appparagym-backend   appparagym-backend:pre-f1
docker tag appparagym-frontend  appparagym-frontend:pre-f1
docker tag appparagym-scheduler appparagym-scheduler:pre-f1
docker compose build
```

- [ ] Build termina sin error (incluye `gosu` + usuario `gymuser`).

### B.4 — Recreate (aplica el endurecimiento)

```bash
docker compose up -d
```

- En el primer arranque, el entrypoint reconcilia permisos del volumen (`chown` a `gymuser`).
  Es idempotente.
- Si se modificó `VITE_API_URL` (multi-dispositivo): el `build` ya rehorneó el frontend; el
  `up -d` lo recrea.

### B.5 — Verificación post-arranque inmediata

```bash
docker compose ps                     # 3 servicios "Up"; backend "healthy"
docker compose logs backend   --tail 20
docker compose logs scheduler --tail 20
```

- [ ] Backend sano (sin traza de `SECRET_KEY` faltante).
- [ ] Scheduler muestra "Scheduler iniciado — backup 02:00 · notificaciones 08:00".
- Continuar a la sección **D** (validación post-release).

---

## C. Plan de rollback

Disparadores: backend en crash-loop (típicamente `SECRET_KEY` faltante), frontend no carga, o
cualquier verificación de la sección D falla y no se resuelve rápido.

### C.1 — Rollback rápido (vuelta a la versión anterior)

```bash
git checkout 7ec7ff8                  # commit previo a F1 (estado anterior conocido)
docker compose up -d --build
```

- Las variables nuevas del `.env` (`SECRET_KEY`, `BIND_ADDR`) son **inertes** para el código
  viejo: no estorban.
- **Permisos:** el código viejo corre como root y puede leer/escribir los archivos ya
  re-poseídos por `gymuser` (root accede a todo): la BD sigue operativa sin tocar datos.

### C.2 — Rollback con las imágenes retaggeadas (si el build fallara)

```bash
docker tag appparagym-backend:pre-f1   appparagym-backend
docker tag appparagym-frontend:pre-f1  appparagym-frontend
docker tag appparagym-scheduler:pre-f1 appparagym-scheduler
docker compose up -d
```

### C.3 — Restauración de datos (solo si la BD se corrompiera — improbable)

Detener servicios y restaurar el backup B.1 dentro del volumen:

```bash
docker compose down
docker run --rm -v appparagym_db-data:/data -v "%CD%\backups_host":/backup alpine \
  sh -c "cp /backup/gym_PRE_F1_<FECHA>.db /data/gym.db"
docker compose up -d
```

El `chown` del entrypoint no altera contenido; este paso es solo una red de seguridad ante un
fallo de datos imprevisto.

### C.4 — Qué validar antes de declarar el rollback exitoso

- [ ] Backend `healthy`, frontend carga, operación normal.
- [ ] Conteos de clientes/membresías/pagos coinciden con lo previo (sin pérdida).

---

## D. Checklist de validación post-release

Declarar éxito solo si **todos** los ítems pasan. Reemplazar `<BIND>` por `127.0.0.1`
(PC única) o la IP LAN según `BIND_ADDR`.

- [ ] **Backend operativo:** `curl http://<BIND>:8000/api/health` → `{"status":"ok"}`.
- [ ] **Frontend operativo:** abrir `http://<BIND>/` en el navegador; carga el Dashboard; datos
  visibles (clientes/membresías).
- [ ] **Scheduler activo:** `docker compose logs scheduler` muestra el arranque y los jobs
  programados.
- [ ] **Usuario efectivo no-root:**
  - `docker top appparagym-backend-1 -o user,cmd` → USER **10001** en uvicorn.
  - `docker top appparagym-scheduler-1 -o user,cmd` → USER **10001**.
- [ ] **Backup manual:** botón en Dashboard (o `POST /api/backup/manual`) → 200 y aparece archivo
  nuevo en `manual/` propiedad `gymuser`.
- [ ] **Backup automático:** confirmar que existe el backup inicial del arranque en `automatic/`
  (`docker exec appparagym-backend-1 ls -l /app/data/backups/automatic`), propiedad `gymuser`.
- [ ] **Confirmación `SECRET_KEY`:** backend arrancó sin error de clave; (si usa SMTP)
  `POST /api/notifications/test-smtp` funciona (descifrado OK → no se cambió la clave).
- [ ] **Confirmación `BIND_ADDR`:**
  - `docker compose ps` → puertos publicados como `<BIND>:8000` y `<BIND>:80`.
  - PC única: desde **otra** máquina de la red, `http://<IP-PC>:8000/api/health` **no** responde
    (exposición reducida).
  - Multi-dispositivo: desde otro dispositivo, el frontend carga y opera contra `<IP-LAN>:8000`.
- [ ] **Operación funcional mínima:** crear un cliente de prueba, registrar un pago, eliminarlos
  (sin errores) — confirma escritura `gym.db` end-to-end.
- [ ] **Datos intactos:** conteos de clientes/membresías/pagos iguales a los previos al
  despliegue.

Repetir A–D en el **segundo gimnasio** tras el éxito del canary.

---

## E. Resumen operativo de las dos instalaciones

| Ítem | Gimnasio 1 (canary) | Gimnasio 2 |
|---|---|---|
| Topología | confirmar | confirmar |
| `BIND_ADDR` | `127.0.0.1` salvo multi-dispositivo | `127.0.0.1` salvo multi-dispositivo |
| `SECRET_KEY` | única — conservar si existe | única **distinta** — conservar si existe |
| Rebuild frontend (`VITE_API_URL`) | solo si multi-dispositivo | solo si multi-dispositivo |
| Orden | **primero**, validar completo | tras éxito del canary |

---

## Referencias

- Endurecimiento implementado: `docs/BASELINE_SEGURIDAD.md` (SEC-005/007/009/011/013).
- Fase en el roadmap: `docs/ROADMAP_COMERCIALIZACION.md` → F1.
- Deuda técnica cerrada por F1 Bloque A: TD-30, TD-34, TD-37, TD-39 en `TECH_DEBT.md`.
