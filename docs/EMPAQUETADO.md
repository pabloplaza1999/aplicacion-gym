# Empaquetado del Kit — Rhinopower

> **Uso interno del publicador.** Este documento no forma parte del kit del cliente.

---

## Estructura del kit de entrega

```
rhinopower-kit-v1.0/
├── docker-compose.yml
├── .env.example
├── start.bat
├── stop.bat
├── upgrade.bat
├── backup-manual.bat
├── reset-password.bat
├── load-images.bat
├── images/
│   ├── rhinopower-backend.tar
│   └── rhinopower-frontend.tar
└── docs/
    ├── INSTALACION.md
    ├── OPERACION.md
    ├── BACKUP.md
    ├── SOPORTE.md
    └── ACTUALIZACION.md
```

**No incluir:** código fuente (`backend/`, `frontend/`), archivos `.env` con claves reales, directorio `.git`, `INICIAR.bat` (script de desarrollo interno), `docs/EMPAQUETADO.md` (este archivo).

---

## Proceso de empaquetado

### 1. Construir y etiquetar las imágenes

```bash
docker compose build
```

Las imágenes quedan etiquetadas como `rhinopower/backend:1.0` y `rhinopower/frontend:1.0` gracias a las directivas `image:` en `docker-compose.yml`.

Verificar:
```bash
docker images | grep rhinopower
```

Debe mostrar ambas imágenes con el tag correcto.

### 2. Exportar las imágenes a archivos .tar

```bash
mkdir images

docker save rhinopower/backend:1.0 -o images/rhinopower-backend.tar
docker save rhinopower/frontend:1.0 -o images/rhinopower-frontend.tar
```

Verificar tamaños (referencia v1.0: backend ~335 MB, frontend ~102 MB):
```bash
dir images\
```

### 3. Preparar el directorio del kit

Copiar en una carpeta limpia los archivos listados en la estructura de arriba. Usar `.env.example` — nunca incluir `.env` con claves reales.

### 4. Comprimir para entrega

```powershell
Compress-Archive -Path rhinopower-kit-v1.0\* -DestinationPath rhinopower-v1.0.zip
```

Verificar que el `.zip` abre correctamente y contiene todos los archivos esperados.

---

## Checklist pre-entrega

- [ ] Imágenes tagueadas (`docker images | grep rhinopower`)
- [ ] `.tar` generados con tamaño esperado
- [ ] `docker-compose.yml` sin rutas de desarrollo hardcodeadas
- [ ] `.env.example` presente — sin `.env` con claves reales
- [ ] `INICIAR.bat` **no** incluido
- [ ] `docs/EMPAQUETADO.md` **no** incluido
- [ ] Carpeta `docs/` con los cinco archivos del cliente
- [ ] Carpeta `images/` con los dos `.tar`

---

## Actualización de versión (v1.0 → vX.X)

1. Actualizar el tag en `docker-compose.yml`: `image: rhinopower/backend:X.X` y `image: rhinopower/frontend:X.X`.
2. Actualizar la etiqueta en `frontend/src/App.tsx`: `v1.0 · Local` → `vX.X · Local`.
3. Reconstruir: `docker compose build`.
4. Exportar nuevos `.tar` con el tag actualizado.
5. Empaquetar el kit incluyendo `upgrade.bat` para instalaciones existentes.
6. Documentar los cambios en `FEATURE_SUMMARY.md`.
