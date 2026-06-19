# Respaldo y Restauración — Rhinopower

---

## ¿Qué se respalda?

La base de datos completa del sistema: todos los clientes, membresías, pagos, asistencia, ventas y configuración.

---

## Respaldos automáticos

El sistema crea un respaldo automático **cada día a las 2:00 AM** mientras está corriendo.

- Se conservan los últimos **30 respaldos automáticos**
- Los respaldos más antiguos se eliminan automáticamente
- El estado de los respaldos es visible en el **Dashboard → sección "Respaldos"**

---

## Crear un respaldo manual

Hazlo antes de eventos importantes (actualización del sistema, mantenimiento de la PC):

1. Verifica que el sistema está corriendo (ejecuta `start.bat` si no lo está)
2. Haz doble clic en **`backup-manual.bat`**
3. Espera el mensaje `[OK] Respaldo creado`

Se conservan los últimos **10 respaldos manuales**.

También puedes crear un respaldo manual desde el Dashboard → panel "Respaldos" → botón "Crear respaldo".

---

## Ver el historial de respaldos

Abre Rhinopower → Dashboard → panel "Respaldos" → botón **"Ver respaldos"**.

---

## Copia de seguridad externa (recomendado)

Para proteger los datos ante falla de disco o pérdida del equipo, copia periódicamente los respaldos a un USB o servicio en la nube.

Desde el **Símbolo del sistema**, en la carpeta del kit:

```
docker run --rm -v rhinopower_db-data:/data -v C:\RespaldosGym:/backup alpine cp -r /data/backups /backup/
```

Esto copia todos los respaldos a la carpeta `C:\RespaldosGym` en tu PC.

---

## Restaurar un respaldo

> **Advertencia:** la restauración reemplaza todos los datos actuales. Esta acción no se puede deshacer.
> Crea un respaldo manual antes de restaurar si tienes datos recientes que conservar.

1. Detén el sistema: doble clic en `stop.bat`
2. Abre el **Símbolo del sistema** en la carpeta del kit
3. Lista los respaldos disponibles:
   ```
   docker run --rm -v rhinopower_db-data:/data alpine ls /data/backups/manual/
   ```
4. Identifica el archivo a restaurar (ej. `backup_manual_20260619_143000.db`)
5. Reemplaza la base de datos activa:
   ```
   docker run --rm -v rhinopower_db-data:/data alpine sh -c "cp /data/backups/manual/backup_manual_20260619_143000.db /data/gym.db"
   ```
6. Inicia el sistema: doble clic en `start.bat`
