# DEPLOYMENT_PLAYBOOK.md — Gym Platform

> Template reutilizable para despliegues en instalaciones de clientes.
> Aplica a cualquier cliente y cualquier release. No es específico de F1 ni de Rhinopower.
> Para el runbook del release F1 Bloque A (ya ejecutado): `docs/RELEASE_F1_BLOQUE_A.md`.

---

## Principio canary

Siempre desplegar primero en el cliente de menor riesgo operativo. Validar completamente. Solo entonces continuar con los demás clientes. Nunca desplegar en todos simultáneamente.

---

## §1 — Registro de instalaciones activas

Mantener actualizado manualmente tras cada despliegue.

| Cliente | Tag en producción | BIND_ADDR | Topología | Plan | Módulos activos (via panel) |
|---|---|---|---|---|---|
| Rhinopower | commit `5f4567f` (F4-C + auth fixes) | `127.0.0.1` | PC única | `professional` | Store, Body Tracking, Analytics (BD), Access Control (addon) |

---

## §2 — Variables obligatorias por despliegue

Cada instalación tiene su propio `.env`. Nunca compartir variables entre clientes.

| Variable | Obligatoria | Regla |
|---|---|---|
| `SECRET_KEY` | Sí (producción) | Única por cliente. Conservar si existe — cambiarla rompe el descifrado de `smtp_password`. Si no existe, generar: `docker run --rm python:3.11-slim python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `DEBUG` | Sí | `false` en producción siempre. El backend no arranca sin `SECRET_KEY` cuando `DEBUG=false`. |
| `BIND_ADDR` | Sí | `127.0.0.1` (PC única) o IP LAN (multi-dispositivo). |
| `DATABASE_URL` | Sí | `sqlite:////app/data/gym.db` (invariante — no modificar). |
| `CORS_ORIGINS` | Sí | Acorde a `BIND_ADDR`. |
| `VITE_API_URL` | Solo multi-dispositivo | Requiere rebuild del frontend si cambia. Ej: `http://192.168.1.10:8000`. |
| Feature flags `MODULE_*` | Según plan | `MODULE_NOTIFICATIONS`, `MODULE_BODY_TRACKING`, `MODULE_STORE`. Usados como semilla inicial en el arranque; a partir de F4-C la gestión en caliente se realiza desde el panel `/superadmin/licencia`. |
| `SUPER_ADMIN_PASSWORD` | Sí (F4-C+) | Contraseña inicial del ISV (`super_admin`). Distinta a `ADMIN_INITIAL_PASSWORD`. No vacía en producción. Solo actúa en seed y en `reset_super_admin.py`. |
| `GYM_NAME` | Sí (F4-C+) | Nombre del gimnasio — seed inicial de `gyms`. Sin efecto si el registro ya existe en BD. |
| `GYM_PLAN` | Sí (F4-C+) | Plan inicial: `starter`, `professional` o `premium`. Sin efecto si `gym_licenses` ya existe. |

---

## §3 — Checklist de pre-deploy (por cliente)

Completar antes de ejecutar cualquier paso de despliegue.

- [ ] **Topología confirmada:** ¿PC única o LAN multi-dispositivo? Determina `BIND_ADDR` y si hace falta rebuild del frontend.
- [ ] **`SECRET_KEY`:**
  - [ ] ¿Existe ya en el `.env`? → **conservar**.
  - [ ] ¿No existe? → generar una **única** para este cliente (comando en §2).
  - [ ] Confirmar que **no se reutiliza** la misma clave entre clientes.
- [ ] **`.env` completo y coherente:** `DEBUG=false`, `DATABASE_URL`, `CORS_ORIGINS`, `VITE_API_URL` acorde a la topología, feature flags según plan contratado.
- [ ] **Respaldo previo realizado** (§4.1) y verificado (archivo existe y pesa > 0).
- [ ] **Ventana de mantenimiento** acordada con el cliente (downtime breve durante recreate).
- [ ] **Acceso a la PC** del cliente y Docker operativo.
- [ ] **`docker compose ps`** muestra los servicios en estado sano (estado de partida conocido).
- [ ] **`git status`** limpio en la copia del cliente (sin cambios locales que se perderían).
- [ ] **Espacio en disco** suficiente para la nueva imagen.

---

## §4 — Procedimiento estándar

Ejecutar en la PC del cliente, desde la carpeta del proyecto.

### §4.1 — Backup previo (obligatorio)

```bash
docker run --rm -v appparagym_db-data:/data -v "%CD%\backups_host":/backup alpine \
  sh -c "cp /data/gym.db /backup/gym_PRE_<TAG>_$(date +%Y-%m-%d_%H-%M).db"
```

- [ ] Verificar que el archivo existe en `backups_host\` y pesa > 0.

### §4.2 — Actualización del código

```bash
git fetch origin
git checkout <tag-objetivo>
```

- [ ] Confirmar que `HEAD` apunta al tag esperado.

### §4.3 — Retag de imágenes para rollback

```bash
docker tag appparagym-backend   appparagym-backend:pre-<tag>
docker tag appparagym-frontend  appparagym-frontend:pre-<tag>
docker tag appparagym-scheduler appparagym-scheduler:pre-<tag>
```

### §4.4 — Build

```bash
docker compose build
```

- [ ] Build termina sin error.
- Si se modificó `VITE_API_URL` (multi-dispositivo): el build rehornea el frontend.

### §4.5 — Recreate

```bash
docker compose up -d
```

### §4.6 — Verificación inmediata

```bash
docker compose ps                     # servicios "Up"; backend "healthy"
docker compose logs backend   --tail 20
docker compose logs scheduler --tail 20
```

- [ ] Backend sano (sin error de `SECRET_KEY` faltante).
- [ ] Scheduler muestra los jobs programados.
- Continuar a §5 (validación completa).

---

## §5 — Checklist de validación post-deploy

Declarar éxito solo si **todos** pasan. Reemplazar `<BIND>` por `127.0.0.1` o la IP LAN.

- [ ] **Backend:** `curl http://<BIND>:8000/api/health` → `{"status":"ok"}`.
- [ ] **Frontend:** `http://<BIND>/` carga el Dashboard; datos visibles.
- [ ] **Scheduler:** `docker compose logs scheduler` muestra arranque y jobs.
- [ ] **Backup manual:** botón en Dashboard → 200, aparece archivo nuevo en `manual/`.
- [ ] **Operación mínima:** crear cliente de prueba, registrar pago, eliminarlos (sin errores).
- [ ] **Datos intactos:** conteos de clientes/membresías/pagos iguales a los previos al deploy.
- [ ] **Feature flags:** `GET /api/config/features` devuelve el estado correcto para el plan del cliente.

---

## §6 — Plan de rollback

Disparadores: backend en crash-loop, frontend no carga, o cualquier ítem de §5 falla.

### Rollback rápido (checkout a tag anterior)

```bash
git checkout <tag-anterior>
docker compose up -d --build
```

Las variables nuevas del `.env` son inertes para el código viejo: no estorban.

### Rollback con imágenes retaggeadas (si el build falló)

```bash
docker tag appparagym-backend:pre-<tag>   appparagym-backend
docker tag appparagym-frontend:pre-<tag>  appparagym-frontend
docker tag appparagym-scheduler:pre-<tag> appparagym-scheduler
docker compose up -d
```

### Restauración de datos (solo si la BD se corrompiera — improbable)

```bash
docker compose down
docker run --rm -v appparagym_db-data:/data -v "%CD%\backups_host":/backup alpine \
  sh -c "cp /backup/gym_PRE_<TAG>_<FECHA>.db /data/gym.db"
docker compose up -d
```

Validar rollback: backend healthy, frontend carga, conteos de datos coinciden.

---

## §7 — Alta de cliente nuevo

Procedimiento para instalar en un primer cliente o en un cliente adicional.

1. Generar `SECRET_KEY` única (comando en §2). **No reutilizar** la de ningún cliente existente.
2. Crear `.env` desde `.env.example`. Configurar todas las variables de §2 incluyendo las F4-C: `SUPER_ADMIN_PASSWORD`, `GYM_NAME`, `GYM_PLAN`.
3. Configurar `GYM_PLAN` según el plan contratado. Los feature flags `MODULE_*` solo influyen en el seed inicial; la gestión en caliente se realiza desde el panel de licenciamiento.
4. Ejecutar §3 (pre-deploy) + §4 completo + §5 (validación).
5. Iniciar sesión como `super_admin` y cambiar la contraseña temporal. Verificar que el panel `/superadmin/licencia` muestre el gimnasio, la licencia y los módulos correctos.
6. Añadir entrada a la tabla §1 con tag, topología, plan y módulos activos.
7. Registrar en `docs/EMPAQUETADO.md` si el cliente recibe kit físico.

### Nota F4-C — Upgrade sobre instalación existente con super_admin previo

Si la BD ya contiene un usuario `super_admin` (por ejemplo, de una sesión de pruebas o de un deploy anterior), el seed lo omite y la contraseña puede no coincidir con `SUPER_ADMIN_PASSWORD`. Ejecutar antes del primer acceso:

```powershell
docker exec -it rhinopower-backend-1 python scripts/reset_super_admin.py
```

---

## Referencias

- Runbook específico de F1 Bloque A (ya ejecutado): `docs/RELEASE_F1_BLOQUE_A.md`
- Catálogo de módulos y feature flags: `PRODUCT_MODULES.md`
- Arquitectura ISV y separación core/modules: `PLATFORM_ARCHITECTURE.md`
- Estado de instalaciones: §1 de este documento
