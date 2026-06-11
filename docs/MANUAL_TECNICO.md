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

## Arranques posteriores

Una vez instalado, el sistema se levanta con:

```powershell
cd aplicacion-gym
docker compose up -d
```

Para que Docker arranque automáticamente con Windows: abrir Docker Desktop → Settings → **Start Docker Desktop when you log in** → activar.

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

Para mover el sistema a otro PC:

1. Crear backup de la base de datos (ver sección Backup).
2. Instalar el sistema en el nuevo PC siguiendo esta guía desde el Paso 1.
3. Copiar el archivo `gym_backup.db` al nuevo PC y restaurarlo.

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
