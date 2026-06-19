# Soporte y Solución de Problemas — Rhinopower

---

## El sistema no inicia (`start.bat` da error)

**Causa más común:** Docker Desktop no está corriendo.

**Solución:**
1. Busca "Docker Desktop" en el menú inicio y ábrelo
2. Espera a que el ícono en la barra de tareas deje de animarse (1–2 minutos)
3. Ejecuta `start.bat` nuevamente

Si Docker Desktop no está instalado, sigue el Paso 1 de [INSTALACION.md](INSTALACION.md).

---

## La página no carga (`http://localhost` no abre)

**Verifica:**
1. ¿Ejecutaste `start.bat`? Debe haberse mostrado `[OK] Sistema iniciado`
2. Espera 60 segundos después de iniciar y recarga la página (F5)
3. Prueba con otro navegador (Chrome, Edge, Firefox)

**Si sigue sin cargar:**
1. Ejecuta `stop.bat`
2. Espera 10 segundos
3. Ejecuta `start.bat`

---

## Olvidé la contraseña del administrador

1. Asegúrate de que el sistema está corriendo (`start.bat`)
2. Haz doble clic en **`reset-password.bat`**
3. Confirma la acción cuando se te pida
4. Inicia sesión en `http://localhost` con:
   - **Usuario:** `admin`
   - **Contraseña:** la configurada en `ADMIN_INITIAL_PASSWORD` dentro del archivo `.env`
5. El sistema pedirá establecer una nueva contraseña

---

## El respaldo manual no funciona

**Causa:** el sistema no está corriendo.

**Solución:** ejecuta `start.bat` primero, luego `backup-manual.bat`.

---

## Docker Desktop pide actualizar WSL

Acepta la actualización. WSL es requerido por Docker en Windows. Sigue las instrucciones en pantalla y reinicia si se solicita.

---

## Docker dice "Hardware assisted virtualization must be enabled"

La virtualización no está habilitada en la BIOS de la PC.

1. Reinicia la PC y entra a la BIOS (generalmente con F2, F10, F12 o Supr al iniciar)
2. Busca "Virtualization Technology", "Intel VT-x" o "AMD-V"
3. Habilítala y guarda los cambios
4. Reinstala Docker Desktop si es necesario

---

## El sistema estaba funcionando y dejó de responder

Puede ocurrir tras actualizaciones de Windows o Docker Desktop.

1. Clic derecho en el ícono de Docker en la barra de tareas → **Restart**
2. Espera 2 minutos
3. Ejecuta `start.bat`

---

## ADVERTENCIA — Comando que destruye los datos permanentemente

**Nunca ejecutes el siguiente comando:**

```
docker compose down -v
```

La opción `-v` elimina el volumen donde están guardados todos los datos del gimnasio (clientes, membresías, pagos y respaldos). Esta acción **no se puede deshacer**.

El script `stop.bat` **no** incluye esta opción — es seguro para uso diario.

Si ejecutaste este comando por error, contacta a soporte **antes** de iniciar el sistema nuevamente.

---

## Contacto con soporte Rhinopower

Describe el problema, el mensaje de error que aparece y los pasos que ya intentaste.

- **Correo:** pabloplaza1999@gmail.com
