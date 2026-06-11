# Gym Management System

Sistema de gestión para gimnasio local (~100 clientes).

**Stack:** React 18 + TypeScript + TailwindCSS · FastAPI + SQLAlchemy 2 · SQLite · Docker

---

## Instalación en PC nuevo (gimnasio u otro equipo)

Pasos completos para instalar el sistema desde cero en Windows:

```powershell
# 1. Instalar Docker Desktop
winget install Docker.DockerDesktop --accept-package-agreements --accept-source-agreements

# 2. Instalar Git
winget install Git.Git

# 3. Reiniciar el PC
```

Si Docker Desktop no arranca al reiniciar (error de virtualización):

```powershell
# Abrir PowerShell como administrador y ejecutar:
wsl --install
# Reiniciar el PC nuevamente
```

```powershell
# 4. Clonar el proyecto
git clone https://github.com/pabloplaza1999/aplicacion-gym.git
cd aplicacion-gym

# 5. Configurar entorno
cp .env.example .env

# 6. Levantar el sistema (primera vez descarga ~600 MB)
docker compose up -d
```

Abrir **http://localhost** en el navegador — el sistema está listo.

**Arranques posteriores:** `docker compose up -d` (segundos, sin descarga).

---

## Arranque rápido

### Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo
- [Git](https://git-scm.com/) instalado

### Primera ejecución

```bash
git clone https://github.com/pabloplaza1999/aplicacion-gym.git
cd aplicacion-gym
cp .env.example .env
docker compose up -d
```

El sistema queda disponible en:

| Servicio  | URL                        |
|-----------|----------------------------|
| Frontend  | http://localhost            |
| Backend   | http://localhost:8000       |
| API docs  | http://localhost:8000/docs  |
| Health    | http://localhost:8000/api/health |

La base de datos se inicializa automáticamente con los planes de membresía al primer arranque.

---

## Comandos de operación

```bash
# Arrancar en background
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f backend
docker compose logs -f frontend

# Detener (datos preservados)
docker compose down

# Ver estado de contenedores
docker compose ps
```

> ⚠️ **ADVERTENCIA — Pérdida de datos:**
> `docker compose down -v` elimina el volumen de base de datos de forma permanente e irreversible.
> Usar únicamente para reset total del sistema. Hacer backup antes.

---

## Configuración de entorno (.env)

Copiar `.env.example` a `.env` y ajustar según el entorno:

```env
# Base de datos (no cambiar en Docker)
DATABASE_URL=sqlite:////app/data/gym.db

# Orígenes permitidos para CORS
CORS_ORIGINS=["http://localhost", "http://localhost:80"]

# Origen del servidor backend — solo host y puerto, SIN /api al final
VITE_API_URL=http://localhost:8000
```

### Despliegue en servidor externo

`VITE_API_URL` se embebe en el build estático del frontend al ejecutar `docker compose up`.
**Debe configurarse antes de levantar el sistema**, no tiene efecto en caliente.

> ⚠️ `VITE_API_URL` debe contener únicamente el origen del servidor (`http://host:puerto`).
> **No incluir `/api` al final** — el sistema lo agrega automáticamente.

```env
# En servidor con IP pública o dominio:
VITE_API_URL=http://192.168.1.100:8000
# o
VITE_API_URL=http://mi-dominio.com:8000

# Ajustar también CORS para permitir el origen del frontend:
CORS_ORIGINS=["http://mi-dominio.com"]
```

Después de cambiar `VITE_API_URL` reconstruir las imágenes:

```bash
docker compose build
docker compose up -d
```

---

## Actualización de la aplicación

Cuando hay cambios de código:

```bash
# 1. Obtener cambios
git pull

# 2. Reconstruir imágenes
docker compose build

# 3. Reiniciar con las nuevas imágenes (datos preservados)
docker compose up -d
```

Las migraciones de base de datos se aplican automáticamente en el arranque del backend.

---

## Respaldo y restauración de datos

La base de datos vive en el volumen Docker `appparagym_db-data`.

### Hacer backup

```bash
# Copiar gym.db desde el volumen al directorio actual
docker run --rm \
  -v appparagym_db-data:/data \
  -v "$(pwd)":/backup \
  alpine cp /data/gym.db /backup/gym_backup_$(date +%Y%m%d).db
```

En Windows (PowerShell):

```powershell
$date = Get-Date -Format "yyyyMMdd"
docker run --rm `
  -v appparagym_db-data:/data `
  -v "${PWD}:/backup" `
  alpine cp /data/gym.db /backup/gym_backup_$date.db
```

### Restaurar backup

```bash
# 1. Detener el sistema
docker compose down

# 2. Restaurar el archivo al volumen
docker run --rm \
  -v appparagym_db-data:/data \
  -v "$(pwd)":/backup \
  alpine cp /backup/gym_backup_YYYYMMDD.db /data/gym.db

# 3. Volver a levantar
docker compose up -d
```

### Backup automático recomendado

Agregar al cron del host (Linux/Mac):

```cron
0 3 * * * docker run --rm -v appparagym_db-data:/data -v /ruta/backups:/backup alpine cp /data/gym.db /backup/gym_$(date +\%Y\%m\%d).db
```

---

## Modos de ejecución

El proyecto tiene dos formas de correr. Usa la que corresponda según el contexto:

| | `INICIAR.bat` | `docker compose up -d` |
|---|---|---|
| **Cuándo usarlo** | Desarrollo — editar código | Uso diario en el gimnasio |
| **Requiere** | Python + Node instalados | Solo Docker Desktop |
| **Frontend** | `http://localhost:5173` | `http://localhost` |
| **Backend** | `http://localhost:8000` | `http://localhost:8000` |
| **Base de datos** | `backend/gym.db` (archivo local) | Volumen Docker (aislado) |
| **Recarga automática** | Sí (`--reload`) | No (requiere rebuild) |

### INICIAR.bat — desarrollo local

Doble clic en `INICIAR.bat`. Abre dos ventanas de consola (backend y frontend) y lanza el navegador en `http://localhost:5173`.

Útil cuando estás modificando código: el backend recarga solo al guardar cambios en Python, y Vite recarga el frontend en tiempo real.

> Los datos de esta modalidad se guardan en `backend/gym.db` (archivo local), **separado** del volumen Docker.

### docker compose up — producción / uso diario

```powershell
docker compose up -d
```

Recomendado para el PC del gimnasio y cualquier despliegue fuera del entorno de desarrollo.

---

## Desarrollo local sin Docker

Si no tienes Docker y necesitas correr el proyecto manualmente:

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

El frontend en dev usa el proxy de Vite (`:5173 → :8000`) automáticamente.
No es necesario definir `VITE_API_URL` para desarrollo local.

---

## Estructura del proyecto

```
APP para Gym/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # Endpoints FastAPI
│   │   ├── services/        # Lógica de negocio
│   │   ├── repositories/    # Acceso a datos
│   │   ├── models/          # Modelos SQLAlchemy
│   │   ├── schemas/         # Schemas Pydantic
│   │   ├── database/        # init_db, session
│   │   └── core/config.py   # Configuración (env vars)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # Vistas principales
│   │   ├── components/      # Componentes reutilizables
│   │   ├── services/api.ts  # Cliente HTTP
│   │   └── types/index.ts   # Tipos TypeScript
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
└── .env                     # Local — nunca en git
```
