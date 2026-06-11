# Manual del Operador — Sistema de Gestión Gym

Guía de uso diario para el personal del gimnasio.

---

## Rutina diaria de operación

### Al encender el PC

1. Encender el PC normalmente.
2. Esperar a que Docker Desktop arranque solo — el ícono de la ballena aparece en la barra de tareas (esquina inferior derecha). Cuando deja de estar animado, está listo.
3. Abrir **Chrome o Edge** e ingresar a:

```
http://localhost
```

No se requiere usuario ni contraseña. El sistema está listo para usar.

> Si la página no carga, esperar 30 segundos y recargar. Docker puede tardar un momento en levantar los servicios.

### Si el sistema no carga

1. Verificar que el ícono de Docker está en la barra de tareas. Si no aparece, abrir **Docker Desktop** desde el menú de inicio y esperar.
2. Recargar `http://localhost` en el navegador.
3. Si sigue sin cargar, contactar al técnico.

### Al cerrar el día

No es necesario apagar el sistema manualmente. Al apagar el PC, Docker se detiene solo. Los datos quedan guardados automáticamente.

---

## Módulos disponibles

| Módulo | Descripción |
|--------|-------------|
| Dashboard | Resumen general del negocio |
| Clientes | Registro y gestión de socios |
| Pagos | Registro y consulta de pagos |
| Asistencia | Check-in de valeras |
| Tienda | Ventas, productos e inventario |
| Configuración | SMTP para notificaciones y umbrales de alerta |

---

## Dashboard

Pantalla principal con indicadores del negocio:

- **Membresías activas / por vencer / vencidas / congeladas / valeras agotadas** — conteo actual de clientes por estado.
- **Ingresos del mes** — total membresías + total tienda + total general.
- **Cartera pendiente** — saldo de ventas a crédito sin cobrar.
- **Membresías por plan** — tabla con activos, agotados, vencidos y congelados por tipo de plan.
- **Alertas operativas** — lista de clientes que requieren atención:
  - *Vencidas*: membresías ya vencidas (con filtro por antigüedad).
  - *Hoy / 3 días / 7 días*: membresías próximas a vencer.
  - *Cartera*: clientes con mayor deuda pendiente.
  - *Bajo stock*: productos con inventario bajo el mínimo.

---

## Clientes

### Registrar un cliente nuevo

1. Ir a **Clientes**.
2. Clic en **Nuevo cliente**.
3. Completar nombre, cédula, teléfono y correo (opcional).
4. Guardar.

### Crear una membresía

1. Abrir el cliente desde la lista.
2. En la sección **Membresía**, seleccionar el plan y la fecha de inicio.
3. Clic en **Crear membresía**.

> Si el cliente tiene una valera activa y se intenta cambiar a plan mensual, el sistema muestra una advertencia con los ingresos restantes. Confirmar si se desea proceder.

### Renovar una membresía

1. Abrir el cliente.
2. Clic en **Renovar membresía**.
3. Seleccionar el nuevo plan y confirmar.

### Congelar / reactivar una membresía

- **Congelar**: pausa el conteo de días. Útil cuando el cliente no puede asistir por un período. Máximo 3 congelaciones por membresía.
- **Reactivar**: reanuda la membresía desde donde se pausó.

Los botones aparecen en el detalle del cliente según el estado actual.

### Registrar un pago

1. Abrir el cliente.
2. En la sección **Pagos**, clic en **Registrar pago**.
3. Ingresar monto, método de pago y concepto.
4. Guardar.

### Medidas corporales

En la pestaña **Info** del cliente se pueden registrar y consultar las medidas corporales.

### Eliminar un cliente

El botón **Eliminar** en el detalle del cliente realiza una eliminación permanente. Esta acción no se puede deshacer.

---

## Pagos

- Ver todos los pagos registrados con nombre del cliente, monto, método y fecha.
- Eliminar un pago individual si fue registrado por error.
- Estadísticas de pagos por mes disponibles en la sección superior.

---

## Asistencia (Valeras)

Las valeras son planes de ingreso limitado (ej. Valera 7 = 7 ingresos en 30 días).

### Registrar un ingreso

1. Ir a **Asistencia**.
2. Ingresar la cédula del cliente.
3. Clic en **Registrar ingreso**.
4. El sistema confirma el ingreso y muestra los ingresos restantes.

> Solo se permite un ingreso por día por valera.

### Consultar estado de una valera

1. Ir a **Asistencia**.
2. Ingresar la cédula del cliente.
3. Clic en **Consultar valera**.
4. Se muestra: total de ingresos, consumidos, restantes, fecha de vencimiento y estado.

**Estados posibles de una valera:**

| Estado | Significado |
|--------|-------------|
| Vigente | Tiene ingresos disponibles y no ha vencido |
| Agotada | Se usaron todos los ingresos |
| Vencida | Expiró por fecha aunque queden ingresos |

---

## Tienda

### Registrar una venta

1. Ir a **Tienda** → pestaña **Ventas**.
2. Buscar y agregar productos al carrito.
3. Seleccionar cliente (opcional) y método de pago (contado o crédito).
4. Confirmar la venta.

> Una venta a crédito queda registrada en **Cartera** hasta que se abone o pague en su totalidad.

### Registrar un abono a cartera

1. Ir a **Tienda** → pestaña **Cartera**.
2. Buscar la venta pendiente.
3. Clic en **Abonar** e ingresar el monto recibido.

### Anular una venta

1. Ir a **Tienda** → pestaña **Ventas**.
2. Abrir la venta.
3. Clic en **Anular**.

> La anulación repone automáticamente el stock de los productos.

### Gestionar productos

- **Productos**: agregar, editar, activar/desactivar y eliminar productos.
- **Categorías**: organizar productos por categoría.
- **Inventario**: registrar entradas de mercancía y ajustes de stock.

### Reportes de tienda

Pestaña **Reportes** — muestra KPIs de ventas, estado de cartera e inventario bajo stock para el período seleccionado (hoy, semana, mes o rango personalizado).

---

## Notificaciones de vencimiento

El sistema envía correos automáticos a los clientes cuando su membresía está próxima a vencer (7, 3, 1 y 0 días antes). Los correos se envían a las **08:00 AM** todos los días.

> Para que funcione, el SMTP debe estar configurado. Ver sección **Configuración** más abajo.

### Panel de notificaciones en el Dashboard

| Indicador | Significado |
|-----------|-------------|
| Punto verde | SMTP configurado y notificaciones activas |
| Punto amarillo | Notificaciones desactivadas (toggle en Configuración) |
| Advertencia naranja | SMTP no configurado |
| "Sin email" | Clientes con membresía próxima a vencer sin correo — contactar manualmente |

### Ejecutar el ciclo manualmente

Dashboard → panel **Notificaciones** → **"Ejecutar ahora"**.

Útil para la primera prueba después de configurar el SMTP, o para recuperación ante un fallo.

### Ver historial de correos enviados

Dashboard → "Ver historial" → tabla con cliente, plan, umbral (7d/3d/1d/0d), estado y fecha.

### Qué hacer si hay correos fallidos

Los correos fallidos se reintentan automáticamente cada día. Si los fallos persisten, contactar al técnico para revisar la configuración SMTP.

---

## Configuración

La página **Configuración** (engranaje en el menú lateral) gestiona el sistema de notificaciones:

- **SMTP**: servidor, puerto, usuario y contraseña del correo que envía las alertas.
- **Remitente**: nombre y correo que ve el cliente al recibir la notificación.
- **Umbrales**: días de anticipación con los que se envía el aviso (por defecto: 7, 3, 1 y 0 días).
- **Toggle Activo**: activa o pausa el envío automático sin borrar la configuración.
- **"Probar conexión"**: verifica las credenciales enviando un correo de prueba al remitente.

Para la configuración inicial del SMTP (Gmail, Outlook) ver [`docs/NOTIFICACIONES.md`](NOTIFICACIONES.md).

---

## Recomendaciones operativas

- Registrar el pago de membresía **el mismo día** que se crea o renueva.
- Verificar semanalmente el **Dashboard → Alertas → Vencidas** para contactar clientes.
- Registrar el **correo electrónico** de cada cliente para recibir notificaciones automáticas.
- Revisar **Bajo stock** antes de hacer pedidos de mercancía.
- **No ejecutar** comandos en la terminal del PC sin indicación del técnico responsable.
