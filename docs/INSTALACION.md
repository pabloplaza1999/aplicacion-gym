# Guía de Instalación — Rhinopower

Esta guía permite instalar Rhinopower en la PC del gimnasio en menos de 30 minutos.

---

## Requisitos previos

- PC con **Windows 10** u **11** (64 bits)
- Acceso a internet durante la instalación _(ver sección al final si no hay internet)_
- Al menos **4 GB de RAM** y **10 GB de espacio libre en disco**

---

## Paso 1 — Instalar Docker Desktop

Docker Desktop es el programa que ejecuta Rhinopower. Solo se instala una vez.

1. Ve a **https://www.docker.com/products/docker-desktop/** y descarga la versión para Windows
2. Ejecuta el instalador y sigue los pasos (acepta todas las opciones por defecto)
3. Cuando termine, **reinicia la PC**
4. Después del reinicio, Docker Desktop se abre automáticamente
5. Espera a que el icono de Docker en la barra de tareas deje de animarse (1–2 minutos la primera vez)

> Si Docker Desktop pide instalar **WSL 2**, acepta y sigue las instrucciones en pantalla, luego reinicia nuevamente.

---

## Paso 2 — Descomprimir el kit de Rhinopower

1. Copia el archivo `rhinopower-local-v1.0.zip` a la carpeta donde instalarás el sistema
   - Recomendado: `C:\Rhinopower`
2. Haz clic derecho sobre el archivo → **Extraer todo** → elige la carpeta → **Extraer**
3. Verifica que dentro de la carpeta estén los archivos `start.bat`, `stop.bat` y `docker-compose.yml`

---

## Paso 3 — Configurar el sistema

Antes del primer inicio debes configurar el archivo `.env`:

1. Abre la carpeta del kit y busca el archivo `.env`
2. Haz clic derecho sobre él → **Abrir con** → **Bloc de notas**
3. Completa los tres valores obligatorios:

```
SECRET_KEY=<pega aquí la clave generada — ver instrucción abajo>
JWT_SECRET_KEY=<pega aquí una segunda clave generada>
ADMIN_INITIAL_PASSWORD=<elige una contraseña para el primer acceso>
```

### Cómo generar las claves de seguridad

Abre el **Símbolo del sistema** (busca "cmd" en el menú inicio) y ejecuta este comando:

```
docker run --rm python:3.11-slim python -c "import secrets; print(secrets.token_hex(32))"
```

Copia el resultado y pégalo como valor de `SECRET_KEY`.  
Ejecuta el comando **una segunda vez** para obtener un valor diferente para `JWT_SECRET_KEY`.

> Cada instalación debe tener claves únicas. Nunca uses las mismas claves en dos gimnasios distintos.

4. Guarda el archivo `.env` (Ctrl+S)

---

## Paso 4 — Primer inicio

1. Haz doble clic en **`start.bat`**
2. La primera vez descarga las imágenes del sistema (~5 minutos según la velocidad de internet)
3. Cuando aparezca `[OK] Sistema iniciado`, el navegador se abre automáticamente

---

## Paso 5 — Primer acceso

1. Inicia sesión con:
   - **Usuario:** `admin`
   - **Contraseña:** la que configuraste en `ADMIN_INITIAL_PASSWORD`
2. El sistema te pedirá cambiar la contraseña inmediatamente — elige una nueva contraseña segura (mínimo 8 caracteres)
3. ¡Rhinopower está listo para usar!

---

## Verificación de la instalación

La instalación fue exitosa cuando:

- `start.bat` termina sin errores y muestra `[OK] Sistema iniciado`
- `http://localhost` carga la pantalla de inicio de sesión de Rhinopower
- Puedes iniciar sesión y cambiar la contraseña

---

## Instalación sin conexión a internet

Si la PC del gimnasio no tiene acceso a internet, el kit incluye una carpeta `images/` con las imágenes pre-descargadas:

1. Ejecuta `load-images.bat` para cargarlas en Docker
2. Continúa desde el **Paso 4**
