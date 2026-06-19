# Guía de Operación Diaria — Rhinopower

---

## Iniciar el sistema

**Cada mañana, antes de usar el sistema:**

1. Haz doble clic en **`start.bat`**
2. Espera el mensaje `[OK] Sistema iniciado` (30–60 segundos)
3. El navegador se abre automáticamente en `http://localhost`

> Si el navegador no se abre solo, ábrelo manualmente y ve a `http://localhost`

---

## Cerrar el sistema

**Al final del día:**

1. Haz doble clic en **`stop.bat`**
2. Espera el mensaje `[OK] Sistema detenido`

> Los datos se guardan automáticamente en todo momento. No es necesario hacer ninguna acción antes de cerrar.

---

## Acceder a la aplicación

Una vez iniciado, el sistema está disponible en:

```
http://localhost
```

Puedes marcar esta dirección en favoritos en Chrome o Edge para acceder más rápido.

---

## Cerrar sesión

Haz clic en el ícono de salida **(→)** en la esquina inferior izquierda del menú lateral.

---

## Respaldo de datos

Rhinopower hace un respaldo automático **cada día a las 2:00 AM** mientras el sistema está corriendo.

Para crear un respaldo manual antes de un evento importante, consulta [BACKUP.md](BACKUP.md).

---

## Reiniciar el sistema si algo no responde

1. Ejecuta `stop.bat`
2. Espera 10 segundos
3. Ejecuta `start.bat`

Esto resuelve la mayoría de los problemas de conectividad o pantalla en blanco.

---

## Resumen de scripts

| Script | Cuándo usarlo |
|--------|--------------|
| `start.bat` | Cada mañana para iniciar el sistema |
| `stop.bat` | Al final del día para apagarlo |
| `backup-manual.bat` | Antes de eventos importantes o actualizaciones |
| `reset-password.bat` | Si el operador olvida su contraseña |
