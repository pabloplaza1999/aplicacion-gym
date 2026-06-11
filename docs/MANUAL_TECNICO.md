# Manual Técnico — Instalación y Operación del Sistema

Guía para instalar, configurar y mantener el sistema en un PC nuevo.

---

## Requisitos del equipo

| Componente | Mínimo |
|------------|--------|
| Sistema operativo | Windows 10/11 (64 bits) |
| RAM | 4 GB |
| Almacenamiento libre | 5 GB |
| Conexión a internet | Requerida solo para la instalación inicial |

---

## Instalación desde cero

### Paso 1 — Instalar Docker Desktop

Abrir **PowerShell como administrador** y ejecutar:

```powershell
winget install Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
```

### Paso 2 — Instalar Git

```powershell
winget install Git.Git
```

### Paso 3 — Reiniciar el PC

Obligatorio para que los cambios tomen efecto.

### Paso 4 — Verificar Docker

Abrir Docker Desktop desde el menú de inicio. Debe mostrar el estado **"Engine running"**.

Si aparece un error de virtualización al arrancar Docker:

```powershell
# Abrir PowerShell como administrador:
wsl --install
# Reiniciar el PC nuevamente
```

### Paso 5 — Clonar el proyecto

```powershell
git clone https://github.com/pabloplaza1999/aplicacion-gym.git
cd aplicacion-gym
```

### Paso 6 — Configurar el entorno

```powershell
cp .env.example .env
```

El archivo `.env` generado por defecto es correcto para uso local. No requiere cambios.

```env
DATABASE_URL=sqlite:////app/data/gym.db
CORS_ORIGINS=["http://localhost", "http://localhost:80"]
VITE_API_URL=http://localhost:8000
```

### Paso 7 — Levantar el sistema

```powershell
docker compose up -d
```

La primera ejecución descarga las imágenes (~600 MB). Puede tardar varios minutos según la velocidad de internet.

### Paso 8 — Verificar que funciona

Abrir el navegador e ingresar a `http://localhost`.

Verificaciones adicionales:

| URL | Resultado esperado |
|-----|--------------------|
| `http://localhost` | Interfaz del sistema |
| `http://localhost:8000/api/health` | `{"status": "ok"}` |
| `http://localhost:8000/docs` | Documentación de la API |

---

## Operación diaria del PC del gimnasio

### Flujo normal cada día

1. **Encender el PC** normalmente.
2. **Docker Desktop arranca solo** si está configurado (ver abajo). Esperar a que el ícono de la ballena en la barra de tareas esté estático (no animado).
3. **Abrir el navegador** (Chrome o Edge) e ingresar a `http://localhost`.
4. El sistema está listo para usar.

> El operador no necesita abrir ninguna terminal ni ejecutar comandos. Si Docker está configurado para arrancar con Windows, el sistema queda disponible automáticamente al encender el PC.

### Configurar Docker para arranque automático con Windows

Hacer esto una sola vez después de instalar:

1. Abrir **Docker Desktop** desde el menú de inicio.
2. Hacer clic en el ícono de engranaje (Settings) arriba a la derecha.
3. En **General**, activar **"Start Docker Desktop when you log in"**.
4. Clic en **Apply & Restart**.

Desde ese momento Docker arranca solo con Windows y los contenedores del sistema se levantan automáticamente.

### Verificar que el sistema está corriendo

Si la app no carga en el navegador, abrir **PowerShell** y ejecutar:

```powershell
docker compose ps
```

Resultado esperado — los tres contenedores deben estar en estado `Up` o `healthy`:

```
NAME                      STATUS
appparagym-backend-1      Up (healthy)
appparagym-frontend-1     Up
appparagym-scheduler-1    Up
```

Si alguno aparece en `Exit` o no aparece, ver la sección **Recuperación ante fallo de Docker** más abajo.

### Reinicio manual del sistema

Si el sistema se comporta de forma inesperada (pantalla en blanco, datos no cargan, errores en la app), el primer paso es reiniciarlo. Abrir PowerShell en la carpeta del proyecto y ejecutar **un comando por vez**:

```powershell
docker compose down
```

Esperar que termine, luego:

```powershell
docker compose up -d
```

Volver a abrir `http://localhost` en el navegador.

### Recuperación ante fallo de Docker

**Caso 1 — Docker Desktop no arranca:**

1. Buscar "Docker Desktop" en el menú de inicio y abrirlo manualmente.
2. Si muestra error de virtualización, abrir PowerShell como administrador y ejecutar:
```powershell
wsl --install
```
Reiniciar el PC.

**Caso 2 — Contenedores caídos (aparecen en `Exit`):**

```powershell
docker compose down
docker compose up -d
```

**Caso 3 — El sistema no responde aunque los contenedores están `Up`:**

```powershell
docker compose logs backend --tail 30
```

Revisar los últimos logs en busca de errores. Si hay un error desconocido, contactar al técnico.

**Caso 4 — Puerto ocupado (error "port is already allocated"):**

```powershell
netstat -ano | findstr :80
```

Identificar el proceso que usa el puerto 80 y cerrarlo, o reiniciar el PC.

---

## Arranques posteriores

Una vez instalado, el sistema se levanta con:

```powershell
cd aplicacion-gym
docker compose up -d
```

Si Docker está configurado para arrancar con Windows (ver sección anterior), esto ocurre automáticamente y no es necesario ejecutar ningún comando.

---

## Comandos de operación

```powershell
# Levantar el sistema en background
docker compose up -d

# Ver logs en tiempo real (útil para diagnosticar errores)
docker compose logs -f

# Ver logs solo del backend
docker compose logs -f backend

# Ver logs solo del frontend
docker compose logs -f frontend

# Estado de los contenedores
docker compose ps

# Detener el sistema (datos preservados)
docker compose down
```

> ⚠️ **ADVERTENCIA CRÍTICA**
> `docker compose down -v` elimina la base de datos de forma **permanente e irreversible**.
> Nunca ejecutar este comando salvo para un reset total del sistema y solo después de hacer backup.

---

## Backup y restauración de datos

El sistema genera respaldos automáticos diariamente a las **02:00 AM** mediante el servicio `scheduler` incluido en Docker Compose. No requiere configuración adicional.

### Ubicación de los respaldos

Los archivos se guardan dentro del volumen Docker, accesibles desde el Explorador de Windows en la carpeta del proyecto:

```
aplicacion-gym/
└── (volumen db-data montado en /app/data/)
    ├── gym.db                    ← base de datos activa
    └── backups/
        ├── automatic/            ← respaldos automáticos (máx. 30)
        └── manual/               ← respaldos manuales (máx. 10)
```

> Los archivos en `backups/` son accesibles directamente desde el Explorador de Windows — no requieren comandos Docker.

### Nomenclatura

`gym_YYYY-MM-DD_HH-MM.db` — incluye fecha y hora para identificación exacta.

### Crear un backup manual desde la aplicación

1. Abrir el Dashboard en `http://localhost`.
2. Ir al panel **Respaldos** al final de la página.
3. Clic en **"Ver respaldos"**.
4. Clic en **"Crear respaldo ahora"**.
5. El sistema confirma el nombre del archivo creado.

### Restaurar desde un backup

```powershell
# 1. Detener el sistema
docker compose down

# 2. Copiar el archivo de backup sobre gym.db en el volumen
docker run --rm `
  -v appparagym_db-data:/data `
  -v "${PWD}:/host" `
  alpine sh -c "cp /host/backups/automatic/gym_YYYY-MM-DD_HH-MM.db /data/gym.db"

# 3. Levantar el sistema
docker compose up -d
```

Reemplazar `gym_YYYY-MM-DD_HH-MM.db` con el nombre del archivo a restaurar.

### Política de retención automática

| Tipo | Límite | Eliminación |
|------|--------|-------------|
| Automático | 30 archivos | El más antiguo al superar el límite |
| Manual | 10 archivos | El más antiguo al superar el límite |

Los pools son independientes: los respaldos manuales nunca eliminan respaldos automáticos.

---

## Actualizar el sistema

Cuando haya una nueva versión disponible:

```powershell
# 1. Hacer backup primero (ver sección anterior)

# 2. Descargar cambios
git pull

# 3. Reconstruir imágenes
docker compose build

# 4. Levantar el sistema actualizado
docker compose up -d
```

---

## Cambio de equipo o migración

Para mover el sistema al PC del gimnasio o a un equipo nuevo:

### En el PC origen (el que tiene los datos)

1. Crear un backup manual desde el Dashboard → panel **Respaldos** → "Crear respaldo ahora".
2. Copiar el archivo de backup (está en `aplicacion-gym/backups/manual/`) a una memoria USB.
3. Anotar o copiar también el valor de `SECRET_KEY` del archivo `.env` — lo necesitarás en el nuevo PC para que el SMTP funcione.

### En el PC destino (el nuevo)

1. Seguir esta guía desde el **Paso 1 — Instalación desde cero**.
2. En el **Paso 6**, además de copiar `.env.example` a `.env`, agregar la `SECRET_KEY` del PC origen:
```env
SECRET_KEY=la-misma-clave-del-pc-origen
```
3. Levantar el sistema:
```powershell
docker compose up -d
```
4. Restaurar la base de datos desde la USB:
```powershell
docker compose down
docker run --rm -v appparagym_db-data:/data -v "${PWD}:/host" alpine sh -c "cp /host/backups/manual/gym_YYYY-MM-DD_HH-MM.db /data/gym.db"
docker compose up -d
```
5. Abrir `http://localhost` — todos los datos del gimnasio deben aparecer.
6. Ir a **Configuración** y verificar que el SMTP sigue funcionando con "Probar conexión".

> Si se usa la misma `SECRET_KEY`, la contraseña SMTP queda descifrada correctamente y no es necesario reconfigurar el correo.

---

## Configuración para red local (varios equipos)

Si se quiere acceder al sistema desde otros equipos en la misma red:

1. Obtener la IP local del PC servidor:

```powershell
ipconfig
# Buscar "Dirección IPv4", ej: 192.168.1.100
```

2. Editar el archivo `.env`:

```env
VITE_API_URL=http://192.168.1.100:8000
CORS_ORIGINS=["http://192.168.1.100"]
```

3. Reconstruir y levantar:

```powershell
docker compose build
docker compose up -d
```

4. En los otros equipos, acceder a `http://192.168.1.100` desde el navegador.

> `VITE_API_URL` se embebe en el build del frontend. Cualquier cambio requiere reconstruir las imágenes con `docker compose build`.

---

## Configuración de notificaciones por correo

Ver guía completa: [`docs/NOTIFICACIONES.md`](NOTIFICACIONES.md)

Pasos resumidos:

1. Generar `SECRET_KEY` con `docker compose exec backend python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` y agregarla a `.env`.
2. Reconstruir contenedores: `docker compose build && docker compose up -d`.
3. Navegar a **Configuración** en la app y completar el formulario SMTP.
4. Usar **"Probar conexión"** para verificar las credenciales.
5. El scheduler envía los correos automáticamente a las 08:00 AM. También disponible el botón **"Ejecutar ahora"** en el Dashboard.

---

## Diagnóstico de problemas comunes

### El sistema no carga en el navegador

1. Verificar que Docker Desktop está corriendo (ícono en la barra de tareas).
2. Ejecutar `docker compose ps` — ambos contenedores deben estar en estado `Up`.
3. Si alguno está en `Exit`, revisar logs: `docker compose logs -f`.

### Error "port is already allocated"

El puerto 80 o 8000 está siendo usado por otro programa.

```powershell
# Ver qué usa el puerto 80
netstat -ano | findstr :80
```

Cerrar el programa que ocupa el puerto o cambiar los puertos en `docker-compose.yml`.

### Docker no arranca (error de virtualización)

```powershell
# Abrir PowerShell como administrador
wsl --install
# Reiniciar el PC
```

Si el problema persiste, verificar en BIOS que la virtualización (Intel VT-x / AMD-V) esté habilitada.

### La base de datos no tiene datos al levantar

Verificar que no se haya ejecutado `docker compose down -v` por error. Si se perdieron los datos, restaurar desde backup.

---

## Estructura del proyecto

```
aplicacion-gym/
├── backend/          # API FastAPI (Python)
├── frontend/         # Interfaz React (TypeScript)
├── docker-compose.yml
├── .env              # Configuración de entorno (no subir a Git)
├── .env.example      # Plantilla de configuración
└── docs/
    ├── MANUAL_OPERADOR.md
    ├── MANUAL_TECNICO.md
    └── NOTIFICACIONES.md
```

### Servicios y puertos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Frontend (Nginx) | 80 | Interfaz web |
| Backend (FastAPI) | 8000 | API REST |
| Base de datos | — | SQLite en volumen Docker |
