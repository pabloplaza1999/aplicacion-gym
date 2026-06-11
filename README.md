# Gym Management System

Sistema de gestión para gimnasio local (~100 clientes).

**Stack:** React 18 + TypeScript + TailwindCSS · FastAPI + SQLAlchemy 2 · SQLite · Docker

---

## Arranque rápido

### Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo

### Primera ejecución

```bash
git clone <url-del-repo>
cd "APP para Gym"
cp .env.example .env
docker compose up
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

## Desarrollo local sin Docker

Para desarrollo sin contenedores:

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
