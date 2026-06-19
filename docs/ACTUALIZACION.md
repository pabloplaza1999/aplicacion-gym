# Actualización del Sistema — Rhinopower

---

## Cuándo usar este documento

Utiliza esta guía cuando recibes una **actualización del sistema** (nuevo `docker-compose.yml`, nuevas imágenes o scripts actualizados) y ya tienes una instalación de Rhinopower funcionando con datos reales.

Para una **primera instalación** desde cero, consulta [INSTALACION.md](INSTALACION.md).

---

## Antes de actualizar

> **Regla de oro:** nunca actualices sin un respaldo previo.

1. Verifica que el sistema está corriendo (`start.bat`).
2. Crea un respaldo manual:
   - Haz doble clic en **`backup-manual.bat`**, o
   - Abre Rhinopower → Dashboard → Respaldos → Crear respaldo.
3. Copia los respaldos a un USB o carpeta externa (recomendado):
   ```
   docker run --rm -v rhinopower_db-data:/data -v C:\RespaldoPreUpgrade:/backup alpine cp -r /data/backups /backup/
   ```
   *(Si tu instalación aún usa el volumen anterior, reemplaza `rhinopower_db-data` por `aplicacion-gym_db-data`.)*

---

## Procedimiento de actualización (flujo principal)

### Paso 1 — Reemplazar los archivos del kit

Copia los archivos recibidos (nuevos `docker-compose.yml`, `.bat` y `docs/`) sobre la carpeta de instalación existente. Responde **"Sí a todo"** cuando Windows pregunte si deseas reemplazar archivos.

No borres el archivo `.env` — contiene tus claves de configuración.

### Paso 2 — Cargar nuevas imágenes (si se proporcionaron archivos `.tar`)

Si recibes archivos en la carpeta `images/`:

Haz doble clic en **`load-images.bat`**.

Espera el mensaje `[OK] Imágenes cargadas correctamente`.

### Paso 3 — Ejecutar la actualización

Haz doble clic en **`upgrade.bat`**.

El script ejecuta automáticamente:

| Acción | Descripción |
|---|---|
| Detiene el sistema | De forma segura antes de cualquier cambio |
| Detecta datos anteriores | Busca el volumen `aplicacion-gym_db-data` |
| Migra los datos | Crea `rhinopower_db-data` y copia todo el contenido |
| Valida la copia | Verifica que la base de datos quedó íntegra |
| Inicia el nuevo sistema | Solo si la validación fue exitosa |

> **Garantía de seguridad:** el volumen original (`aplicacion-gym_db-data`) **nunca se modifica ni elimina**. Si algo falla durante la migración, el sistema no arranca y tus datos originales permanecen intactos.

### Paso 4 — Validar después de la actualización

1. Verifica que la pantalla de login abre en `http://localhost`.
2. Inicia sesión — usa tu contraseña habitual.
3. Confirma que los miembros, membresías y datos históricos están visibles.
4. Verifica que el Dashboard muestra los datos esperados.
5. Crea un respaldo manual post-actualización (`backup-manual.bat`).

---

## Si la actualización falla

`upgrade.bat` muestra un mensaje de error claro y **no inicia el sistema**.

Tus datos originales permanecen en `aplicacion-gym_db-data` sin ninguna modificación.

**Pasos a seguir:**

1. Anota el mensaje de error que aparece en pantalla.
2. Contacta a soporte: **pabloplaza1999@gmail.com**
3. Mientras esperas respuesta, puedes seguir usando el sistema con el kit anterior.

---

## Procedimiento manual de migración (contingencia)

Si necesitas ejecutar la migración manualmente, sigue estos pasos desde el **Símbolo del sistema** (busca "cmd" en el menú inicio) dentro de la carpeta del kit:

**1. Detener el sistema:**
```
docker compose down
```

**2. Crear el nuevo volumen:**
```
docker volume create rhinopower_db-data
```

**3. Copiar los datos (aditivo — NO modifica el volumen original):**
```
docker run --rm -v aplicacion-gym_db-data:/src -v rhinopower_db-data:/dst alpine sh -c "cp -a /src/. /dst/"
```

**4. Verificar que la base de datos existe en el destino:**
```
docker run --rm -v rhinopower_db-data:/data alpine ls /data/gym.db
```
Debe mostrar `/data/gym.db`. Si no aparece, **no continúes** — contacta a soporte.

**5. Iniciar el nuevo sistema:**
```
docker compose up -d
```

---

## Preguntas frecuentes

**¿Se borran mis datos al actualizar?**
No. La actualización es estrictamente aditiva: el volumen original nunca se elimina ni se modifica.

**¿Puedo volver a la versión anterior si algo sale mal?**
Sí. Tus datos originales permanecen en `aplicacion-gym_db-data`. Para usar la versión anterior, restaura el kit antiguo y ejecuta `start.bat`.

**¿Por qué `upgrade.bat` en lugar de `start.bat`?**
`upgrade.bat` detecta automáticamente si hay datos de una versión anterior y los migra antes de iniciar. Después de una actualización exitosa, el uso diario vuelve a ser `start.bat` y `stop.bat`.

**¿Cuánto tiempo tarda la actualización?**
Entre 2 y 5 minutos dependiendo del tamaño de la base de datos y la velocidad del equipo.
