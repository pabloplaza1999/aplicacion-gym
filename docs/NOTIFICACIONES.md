# Notificaciones por correo — Guía de configuración y operación

Sistema de alertas automáticas de vencimiento de membresías.  
Implementado en **Notificaciones Fase 2**.

---

## Cómo funciona

El scheduler ejecuta un ciclo de evaluación diariamente a las **08:00 AM** (America/Bogota).

El ciclo evalúa todas las membresías activas y envía un correo al cliente cuando su membresía vence en exactamente **7, 3, 1 o 0 días**. Cada par `(membresía, umbral)` se envía **una sola vez** — si el correo ya fue enviado, el ciclo lo omite en ejecuciones posteriores. Los envíos fallidos se reintentan en cada ciclo hasta que sean exitosos.

**Exclusiones automáticas:**
- Membresías congeladas.
- Planes de tipo "Valera" (las valeras se notifican por consumo, no por fecha).
- Clientes sin email registrado (aparecen en el contador "Sin email" del Dashboard).

---

## Requisito previo — SECRET_KEY

La contraseña SMTP se almacena **cifrada** en la base de datos. La clave de cifrado vive exclusivamente en el archivo `.env` — nunca en el código ni en la base de datos. Debe generarse **una sola vez por instalación**, antes de configurar el SMTP.

### Paso 1 — El sistema debe estar levantado

```powershell
docker compose up -d
```

### Paso 2 — Generar la clave

```powershell
docker compose exec backend python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

El resultado es una cadena de ~44 caracteres terminada en `=`, por ejemplo:
```
xK8mN2vQabcdefghijklmnopqrstuvwxyz012345=
```

### Paso 3 — Agregarla al archivo `.env`

Abrir el archivo `.env` (está en la carpeta raíz del proyecto) y agregar al final:

```env
# ── Notificaciones ────────────────────────────
SECRET_KEY=pegar-aqui-la-cadena-completa-sin-comillas
```

> **Importante:** pegar la cadena **sin comillas** y **completa** (incluyendo el `=` del final). Un valor incompleto o con espacios genera el error `Fernet key must be 32 url-safe base64-encoded bytes`.

### Paso 4 — Reconstruir los contenedores

En PowerShell ejecutar **un comando por vez** (`&&` no funciona en PowerShell):

```powershell
docker compose build
```

Esperar que termine, luego:

```powershell
docker compose up -d
```

### Paso 5 — Verificar

Abrir `http://localhost` → **Configuración**. Si el proceso fue correcto, el error rojo de `SECRET_KEY` ya no aparece y el botón **"Guardar configuración"** funciona.

> **Advertencia:** Si se pierde la `SECRET_KEY`, las contraseñas SMTP almacenadas en la BD quedan ilegibles. Generar una nueva clave, agregarla al `.env`, reconstruir, y reconfigurar el SMTP desde la UI. Los datos de clientes y membresías **no se ven afectados**.

---

## Configuración SMTP

Navegar a `http://localhost` → **Configuración** (engranaje en el menú lateral izquierdo).

### Qué datos necesitas

Solo necesitas el **correo del gimnasio** y su contraseña de aplicación. Los demás campos (servidor, puerto) son fijos según el proveedor y no cambian.

---

### Gmail — cuenta del gimnasio

Gmail **no permite** usar la contraseña normal. Requiere una **contraseña de aplicación** generada desde la cuenta.

**Generar la contraseña de aplicación (hacerlo desde el celular o PC con la cuenta del gimnasio):**

1. Ir a `myaccount.google.com` con la cuenta del gimnasio.
2. **Seguridad** → activar **Verificación en dos pasos** si no está activa.
3. Volver a **Seguridad** → **Contraseñas de aplicación**.
4. Crear una contraseña para "Correo / Windows".
5. Google muestra una contraseña de **16 caracteres** (ej: `dqqo qeue bqrw uljl`).
6. Copiarla **sin espacios**: `dqqoqeuebqrwuljl`.

**Llenar el formulario:**

| Campo | Valor |
|-------|-------|
| Servidor SMTP | `smtp.gmail.com` |
| Puerto | `587` |
| Usuario | `correo-del-gimnasio@gmail.com` |
| Contraseña | Los 16 caracteres **sin espacios** |
| Nombre remitente | `RHINO Power` |
| Correo remitente | `correo-del-gimnasio@gmail.com` |

> El **Usuario** y el **Correo remitente** son siempre el mismo correo del gimnasio. El **Servidor** y el **Puerto** nunca cambian para Gmail.

---

### Outlook / Microsoft 365

| Campo | Valor |
|-------|-------|
| Servidor SMTP | `smtp.office365.com` |
| Puerto | `587` |
| Usuario | `correo-del-gimnasio@outlook.com` |
| Contraseña | Contraseña normal de la cuenta Outlook |
| Nombre remitente | `RHINO Power` |
| Correo remitente | `correo-del-gimnasio@outlook.com` |

> Microsoft 365 empresarial puede requerir que el administrador habilite **SMTP AUTH** en el portal de administración.

> Microsoft 365 empresarial puede requerir que el administrador habilite **SMTP AUTH** en el portal de administración de Microsoft 365 (`admin.microsoft.com → Usuarios → tucuenta → Correo → Administrar configuración de correo → Envío de correo autenticado`).

---

## Prueba de conexión SMTP

Después de guardar la configuración, hacer clic en **"Probar conexión"**.

El sistema realiza una conexión SMTP real (no una validación de campos): se conecta al servidor, se autentica y envía un correo de prueba **al mismo correo remitente configurado**.

Si la prueba falla, la UI muestra el mensaje de error exacto del servidor SMTP — ver sección Troubleshooting.

---

## Ejecución manual del ciclo

### Desde la UI

Dashboard → panel **Notificaciones** → botón **"Ejecutar ahora"**.

El resultado aparece inmediatamente en el panel: `X enviados, Y omitidos, Z fallidos`.

### Desde la API

```powershell
curl -X POST http://localhost:8000/api/notifications/run
```

Respuesta esperada:

```json
{
  "sent": 2,
  "skipped": 1,
  "failed": 0,
  "message": "2 enviados, 1 omitidos (ya notificados), 0 fallidos."
}
```

---

## Verificación del scheduler

```powershell
# Ver los últimos logs del scheduler
docker compose logs scheduler --tail 30
```

**Al arrancar el sistema**, el scheduler debe mostrar:

```
[scheduler] Scheduler iniciado — backup 02:00 AM · notificaciones 08:00 AM (America/Bogota)
```

**Al ejecutarse el ciclo** (08:00 AM o manualmente):

```
[scheduler] Notificaciones: 3 enviados, 1 omitidos (ya notificados), 0 fallidos.
```

**Si el scheduler no aparece en `docker compose ps`:**

```powershell
docker compose up -d scheduler
docker compose logs scheduler
```

---

## Troubleshooting

### "Probar conexión" falla: "Authentication failed"

| Proveedor | Causa probable | Solución |
|-----------|---------------|----------|
| Gmail | Se usó la contraseña normal de la cuenta | Crear una **contraseña de aplicación** en Configuración de Google |
| Gmail | La verificación en dos pasos no está activada | Activarla antes de crear la contraseña de aplicación |
| Outlook empresarial | SMTP AUTH deshabilitado | El administrador debe habilitarlo en el portal de Microsoft 365 |
| Cualquier proveedor | Contraseña incorrecta | Verificar y regenerar la contraseña de aplicación |

### "Probar conexión" falla: "Connection refused" o "timed out"

- El servidor SMTP o el puerto son incorrectos.
  - Gmail: `smtp.gmail.com:587`
  - Outlook: `smtp.office365.com:587`
- Un firewall corporativo bloquea la salida al puerto 587 desde el servidor.
- Verificar conectividad: `docker compose exec backend python -c "import socket; socket.create_connection(('smtp.gmail.com', 587), timeout=5); print('OK')"`

### El ciclo devuelve `sent=0 skipped=0 failed=0`

El ciclo no encontró membresías elegibles. Verificar:

1. **¿Hay membresías con vencimiento en 0, 1, 3 o 7 días?** — en Clientes, revisar fechas de fin de membresías.
2. **¿Los clientes elegibles tienen email?** — el contador "Sin email" en el panel del Dashboard muestra cuántos clientes activos no tienen email registrado.
3. **¿Las notificaciones están activadas?** — en Configuración, verificar que el toggle "Activo" está encendido.
4. **¿La SMTP está configurada?** — el panel del Dashboard muestra una advertencia naranja si la SMTP no está configurada.

### Un cliente no recibe correo pese a tener membresía por vencer

1. Verificar que el cliente tiene email registrado: Clientes → ficha del cliente → pestaña Info.
2. Verificar que la membresía no está **congelada**.
3. Verificar que el plan **no es de tipo Valera** (las valeras están excluidas del sistema de notificaciones).
4. Revisar el historial: Dashboard → "Ver historial" — buscar el nombre del cliente para ver si hay un log `failed` con el detalle del error SMTP.
5. Verificar el umbral: la membresía debe vencer exactamente en 7, 3, 1 o 0 días desde hoy (hora Colombia). Si vence en 5 días, el próximo correo se envía cuando falten 3 días.

### El historial muestra logs `failed` repetidos para el mismo cliente

**Este es el comportamiento esperado.** Los envíos fallidos se reintentan en cada ciclo. Indica un problema de SMTP persistente (credenciales vencidas, servidor temporalmente no disponible). Resolver el problema SMTP y el próximo ciclo enviará exitosamente.

---

## Flujo de recuperación ante fallo SMTP

Situación: el sistema ha intentado notificar a clientes pero los correos fallan (SMTP caído, contraseña expirada, etc.).

1. **Identificar el error:** Dashboard → "Ver historial" → revisar `error_message` en los logs `failed`.
2. **Corregir la causa:** actualizar credenciales o servidor en Configuración.
3. **Verificar la corrección:** usar "Probar conexión" — debe devolver éxito.
4. **Recuperación:** los logs `failed` se reintentarán automáticamente en el ciclo de mañana a las 08:00 AM. Para recuperación inmediata: Dashboard → "Ejecutar ahora".
5. **Confirmar:** el historial debe mostrar nuevos registros con `status=sent` para los mismos clientes.

> Los clientes con membresía ya vencida (0 días) y correo fallido **no** recibirán notificación retroactiva una vez resuelta la SMTP — el umbral 0d solo aplica el día exacto del vencimiento. Para esos casos se recomienda contacto manual.

---

## Seguridad de credenciales

| Aspecto | Implementación |
|---------|---------------|
| Contraseña SMTP en BD | Cifrada con Fernet (AES-128-CBC + HMAC) |
| `smtp_password` en API | No se devuelve en ningún GET — solo se acepta en PUT |
| `SECRET_KEY` | Solo en `.env` — nunca en código ni en la BD |
| Tránsito frontend → backend | HTTP local (red local). Usar HTTPS si se expone a internet |

---

## Preparación para Fase 3 — WhatsApp / SMS

La arquitectura fue diseñada para extenderse sin cambios de esquema:

- **Campo `channel`** en `notification_logs` — actualmente `"email"`. Para WhatsApp/SMS, crear un nuevo `ChannelProvider` y registrar los logs con `channel="whatsapp"` o `channel="sms"`. El historial y las estadísticas funcionarán automáticamente.
- **Campo `thresholds`** en `notification_settings` — compartido entre canales. Se puede extender a un JSON por canal si los umbrales difieren.
- **Plantillas** — actualmente embebidas en `_build_email()` en `notification_service.py`. Para plantillas configurables por el operador, se recomienda una tabla `notification_templates` con campos `channel`, `threshold_days`, `subject`, `body` y renderizado con `str.format_map()`.
- **Deduplicación** — el par `(membership_id, threshold_days)` en `notification_logs` es independiente del canal. Para multi-canal, agregar `channel` a la clave de deduplicación en `get_sent_threshold_pairs`.
