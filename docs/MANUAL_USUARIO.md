# MANUAL DE USUARIO
## Sistema de Gestión de Gimnasio

---

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           SISTEMA DE GESTIÓN DE GIMNASIO                        ║
║                                                                  ║
║                  Manual de Usuario                               ║
║                                                                  ║
║           Guía completa para recepcionistas,                     ║
║           administradores y propietarios                         ║
║                                                                  ║
║                  Versión 1.0                                     ║
║               Junio 2026                                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## CONTROL DE VERSIONES

| Versión | Fecha | Descripción de cambios | Autor |
|---------|-------|------------------------|-------|
| 1.0 | Junio 2026 | Versión inicial del manual de usuario | Equipo de desarrollo |

---

## TABLA DE CONTENIDO

1. [Introducción](#1-introducción)
2. [Requisitos de uso](#2-requisitos-de-uso)
3. [Inicio de la aplicación](#3-inicio-de-la-aplicación)
4. [Dashboard — Panel principal](#4-dashboard--panel-principal)
5. [Clientes](#5-clientes)
6. [Membresías](#6-membresías)
7. [Pagos](#7-pagos)
8. [Asistencia — Valeras](#8-asistencia--valeras)
9. [Tienda — Ventas](#9-tienda--ventas)
10. [Inventario](#10-inventario)
11. [Notificaciones de vencimiento](#11-notificaciones-de-vencimiento)
12. [Configuración del sistema](#12-configuración-del-sistema)
13. [Tareas más frecuentes](#13-tareas-más-frecuentes)
14. [Problemas frecuentes](#14-problemas-frecuentes)
15. [Buenas prácticas operativas](#15-buenas-prácticas-operativas)
16. [Contacto de soporte](#16-contacto-de-soporte)

---

## 1. INTRODUCCIÓN

### ¿Qué es este sistema?

El Sistema de Gestión de Gimnasio es una herramienta diseñada específicamente para el manejo diario de su establecimiento. Desde este sistema usted puede:

- Registrar y administrar todos sus clientes
- Crear, renovar y controlar membresías de forma sencilla
- Registrar pagos y llevar el control financiero del mes
- Controlar el acceso de clientes con valeras de ingreso limitado
- Manejar la tienda interna con inventario, ventas y créditos
- Recibir alertas automáticas de membresías próximas a vencer
- Enviar correos de aviso a sus clientes de forma automática
- Consultar reportes de ventas, cartera e inventario

### ¿Para quién es este manual?

Este manual está escrito para **cualquier persona que trabaje en el gimnasio**, sin importar si tiene experiencia con computadores o sistemas de administración. No se requiere ningún conocimiento técnico previo.

Si en alguna sección encuentra una instrucción que no entiende, no dude en contactar al soporte técnico indicado al final de este documento.

### ¿Cómo usar este manual?

- Si necesita aprender a usar el sistema desde cero, lea las secciones en orden.
- Si ya conoce el sistema y necesita recordar cómo hacer algo específico, busque el procedimiento en la sección **13. Tareas más frecuentes**.
- Si el sistema está presentando un error, consulte directamente la sección **14. Problemas frecuentes**.

---

## 2. REQUISITOS DE USO

### ¿Qué necesito para usar el sistema?

El sistema ya viene instalado en el computador del gimnasio. No necesita instalar nada adicional. Solo necesita:

**Computador:**
- El computador donde está instalado el sistema (ya configurado)
- Que el computador esté encendido y funcionando normalmente

**Navegador de internet:**
- Google Chrome (recomendado) o Microsoft Edge
- No necesita internet — el sistema funciona en la red interna del establecimiento

**Pantalla:**
- El sistema funciona mejor en una pantalla con resolución mínima de 1280 x 720 píxeles (la mayoría de monitores modernos ya la tienen)

### ¿Necesito usuario y contraseña?

No. El sistema no requiere inicio de sesión. Al abrir la dirección del sistema en el navegador, entra directamente al panel principal.

> **Importante:** Dado que el sistema no tiene contraseñas, evite dejar el computador sin supervisión con el sistema abierto cuando haya personas ajenas al gimnasio.

### ¿Funciona en el celular o tableta?

El sistema está optimizado para computadores. Puede usarse en tabletas, pero la experiencia es más cómoda en un monitor de escritorio o portátil.

---

## 3. INICIO DE LA APLICACIÓN

### Objetivo
Abrir el sistema cada día para comenzar la operación del gimnasio.

### Descripción
El sistema funciona de forma automática en el computador. Al encender el PC, un programa llamado Docker (que usted no necesita conocer ni configurar) arranca solo en segundo plano y pone el sistema en funcionamiento.

### Cuándo usarlo
Cada vez que encienda el computador al comenzar el día.

---

### Procedimiento de inicio

**Paso 1 — Encender el computador**
Encienda el PC normalmente, como lo hace todos los días.

**Paso 2 — Esperar a que el sistema arranque**
En la esquina inferior derecha de la pantalla, en la barra de tareas, aparecerá el ícono de Docker Desktop (una figura que parece una ballena azul). Cuando este ícono deja de moverse o parpadear, el sistema está listo.

> Esto puede tardar entre 30 y 60 segundos dependiendo del computador.

[CAPTURA-001]
**Descripción:** Barra de tareas de Windows con el ícono de Docker Desktop visible en la esquina inferior derecha.
**Qué debe verse:** El ícono de la ballena azul en la bandeja del sistema, en estado estático (sin animación).
**Qué debe resaltarse:** El ícono de Docker y su estado "estático = listo".
**Por qué es importante:** Es la señal visual que indica que el sistema está listo para usarse. Si el ícono sigue moviéndose, hay que esperar.

---

**Paso 3 — Abrir el navegador**
Abra Google Chrome o Microsoft Edge (cualquiera de los dos funciona).

**Paso 4 — Ingresar la dirección del sistema**
En la barra de dirección del navegador (donde normalmente escribe una página web), escriba exactamente:

```
http://localhost
```

Presione Enter.

[CAPTURA-002]
**Descripción:** Navegador Chrome con la barra de dirección mostrando "http://localhost".
**Qué debe verse:** La barra de dirección con el texto escrito correctamente y el panel principal del sistema cargándose.
**Qué debe resaltarse:** La barra de dirección y el texto exacto a escribir.
**Por qué es importante:** Esta es la única dirección que necesita saber para acceder al sistema. No se escribe ninguna otra cosa.

---

**Paso 5 — Verificar que el sistema cargó**
El sistema mostrará la pantalla principal (Dashboard) con los indicadores del negocio. Si carga correctamente, ya puede comenzar a trabajar.

### Resultado esperado
La pantalla principal del sistema se muestra con los datos actualizados del gimnasio.

[CAPTURA-003]
**Descripción:** Pantalla completa del Dashboard del sistema recién cargado.
**Qué debe verse:** El menú lateral izquierdo con todos los módulos, y en el área central las tarjetas de resumen con los indicadores del negocio (membresías activas, ingresos del mes, etc.).
**Qué debe resaltarse:** El menú lateral y las tarjetas de indicadores principales.
**Por qué es importante:** Confirma que el sistema está completamente operativo y listo para registrar la actividad del día.

---

### Advertencias

> **Si la página no carga después de escribir la dirección:** Espere 30 segundos adicionales y vuelva a cargar la página presionando la tecla F5. Docker puede tardar un momento en terminar de arrancar.

> **Si después de 2 minutos el sistema sigue sin cargar:** Consulte la sección **14. Problemas frecuentes** de este manual.

### Al cerrar el día
No es necesario hacer ninguna acción especial al terminar. Al apagar el computador normalmente, el sistema se detiene solo. Todos los datos quedan guardados automáticamente.

---

## 4. DASHBOARD — PANEL PRINCIPAL

### Objetivo
Tener una visión inmediata del estado general del negocio sin necesidad de entrar a cada módulo.

### Descripción
El Dashboard es la primera pantalla que ve al abrir el sistema. Muestra de forma resumida los indicadores más importantes del gimnasio: cuántos clientes están activos, cuánto se ha recaudado en el mes, qué clientes tienen la membresía por vencer y qué productos están por agotarse en la tienda.

### Cuándo usarlo
- Al comenzar el día, para revisar el estado general del negocio.
- Durante el día, para detectar alertas que requieran atención inmediata.
- Al final del día, para verificar los ingresos registrados.

---

### 4.1 Tarjetas de resumen (indicadores principales)

En la parte superior del Dashboard encontrará una fila de tarjetas de colores con los conteos principales:

[CAPTURA-004]
**Descripción:** Fila de tarjetas de indicadores en la parte superior del Dashboard.
**Qué debe verse:** Tarjetas individuales para: Membresías Activas, Por Vencer, Vencidas, Congeladas, Valeras Agotadas.
**Qué debe resaltarse:** Los números en grande dentro de cada tarjeta y el color diferenciado por estado.
**Por qué es importante:** Son los indicadores más rápidos para saber el estado del negocio en un vistazo.

| Tarjeta | Qué significa |
|---------|---------------|
| **Membresías activas** | Cantidad de clientes con membresía vigente en este momento |
| **Por vencer** | Clientes cuya membresía vence en los próximos 7 días |
| **Vencidas** | Clientes cuya membresía ya expiró y no han renovado |
| **Congeladas** | Clientes que pausaron su membresía temporalmente |
| **Valeras agotadas** | Clientes con valera que usaron todos sus ingresos disponibles |

---

### 4.2 Ingresos del mes

Debajo de las tarjetas encontrará la sección de **Ingresos del mes**, que muestra:

- **Membresías:** total recaudado por cobros de planes de membresía en el mes actual
- **Tienda:** total de ventas realizadas en la tienda durante el mes actual
- **Total general:** suma de membresías más tienda

[CAPTURA-005]
**Descripción:** Sección "Ingresos del mes" con las tres cifras de recaudo.
**Qué debe verse:** Tres valores monetarios: ingresos por membresías, ingresos por tienda y total general del mes.
**Qué debe resaltarse:** El total general como cifra más prominente.
**Por qué es importante:** Permite al propietario o administrador ver de un vistazo cuánto se ha recaudado en el mes en curso.

---

### 4.3 Cartera pendiente

Muestra el **saldo total de ventas a crédito** que los clientes de la tienda aún no han pagado completamente. Si no hay ventas a crédito, este valor es cero.

---

### 4.4 Membresías por plan

Tabla que muestra cuántas membresías hay activas, agotadas, vencidas y congeladas **por cada tipo de plan** que ofrece el gimnasio.

[CAPTURA-006]
**Descripción:** Tabla "Membresías por plan" con filas para cada tipo de plan.
**Qué debe verse:** Una fila por cada plan (ej. Mensual, Plan Día, Valera 7, Valera 15) con columnas: Activos, Agotados, Vencidos, Congelados, Total.
**Qué debe resaltarse:** La columna "Total" y la fila del plan más popular.
**Por qué es importante:** Permite al administrador saber cuántos clientes están en cada plan sin necesidad de contar manualmente.

---

### 4.5 Alertas operativas

Es la sección más importante del Dashboard para la gestión diaria. Muestra una lista de situaciones que requieren atención.

[CAPTURA-007]
**Descripción:** Panel "Alertas operativas" con sus pestañas.
**Qué debe verse:** Pestañas con etiquetas: Vencidas, Hoy, 3 días, 7 días, Cartera, Bajo stock.
**Qué debe resaltarse:** El número de alertas en cada pestaña y la lista de clientes afectados.
**Por qué es importante:** Permite identificar de inmediato qué clientes necesitan ser contactados o qué situaciones requieren acción antes de que se conviertan en un problema mayor.

**Pestañas disponibles:**

| Pestaña | Contenido |
|---------|-----------|
| **Vencidas** | Clientes con membresía ya vencida. Incluye filtros por antigüedad (1-7 días, 8-30 días, más de 30 días). |
| **Hoy** | Clientes cuya membresía vence exactamente hoy |
| **3 días** | Clientes cuya membresía vence en los próximos 3 días |
| **7 días** | Clientes cuya membresía vence en los próximos 7 días |
| **Cartera** | Los 5 clientes con mayor deuda pendiente en la tienda |
| **Bajo stock** | Productos de la tienda con stock por debajo del mínimo definido |

**Búsqueda en alertas:**
En las pestañas de membresías (Vencidas, Hoy, 3 días, 7 días) hay un campo de búsqueda para encontrar un cliente específico por nombre o cédula.

---

### 4.6 Panel de Notificaciones

Muestra el estado del sistema automático de correos a clientes. Consulte la sección **11. Notificaciones de vencimiento** para entender todos sus indicadores.

---

### 4.7 Panel de Respaldos

Muestra información sobre el último respaldo automático de los datos del sistema. Consulte la sección **15. Buenas prácticas operativas** para más detalles.

---

## 5. CLIENTES

### Objetivo
Registrar, consultar, editar y administrar la información de todos los socios del gimnasio.

### Descripción
El módulo de Clientes es el núcleo del sistema. Aquí se registran todos los datos personales de cada socio y desde aquí se gestionan sus membresías, pagos y medidas corporales.

### Cuándo usarlo
- Cuando ingresa un cliente nuevo al gimnasio
- Cuando necesita actualizar los datos de un cliente existente
- Cuando necesita consultar el estado de la membresía de alguien
- Cuando necesita registrar medidas corporales de un cliente

---

### 5.1 Ver la lista de clientes

**Paso 1:** En el menú lateral izquierdo, haga clic en **"Clientes"**.

**Paso 2:** Se muestra la lista completa de todos los clientes registrados.

[CAPTURA-008]
**Descripción:** Pantalla principal del módulo Clientes con la lista de socios.
**Qué debe verse:** Una tabla o listado con los nombres de los clientes, su número de documento, estado de membresía y botones de acción.
**Qué debe resaltarse:** La barra de búsqueda en la parte superior y el botón "Nuevo cliente".
**Por qué es importante:** Muestra el directorio completo de socios y es el punto de partida para cualquier gestión de clientes.

**Búsqueda de un cliente:**
Use la barra de búsqueda en la parte superior para encontrar un cliente por nombre o número de cédula. El listado se filtra automáticamente mientras escribe.

---

### 5.2 Registrar un cliente nuevo

**Cuándo:** Cuando un cliente se inscribe por primera vez en el gimnasio.

**Paso 1:** Haga clic en el botón **"Nuevo cliente"** (esquina superior derecha de la pantalla de Clientes).

**Paso 2:** Se abre un formulario. Complete los campos:

| Campo | Descripción | ¿Obligatorio? |
|-------|-------------|---------------|
| **Nombre completo** | Nombre y apellido del cliente | Sí |
| **Número de cédula** | Documento de identidad (sin puntos ni espacios) | Recomendado |
| **Teléfono** | Número de contacto | No |
| **Correo electrónico** | Email para recibir notificaciones de vencimiento | No |
| **Notas** | Cualquier observación relevante sobre el cliente | No |

[CAPTURA-009]
**Descripción:** Formulario de registro de nuevo cliente.
**Qué debe verse:** Los campos del formulario: nombre, cédula, teléfono, correo y notas, con el botón "Guardar" al final.
**Qué debe resaltarse:** El campo de correo electrónico como campo importante para las notificaciones automáticas.
**Por qué es importante:** La información registrada aquí es la que usará el sistema para identificar al cliente en todas las operaciones y para enviarle correos de aviso.

**Paso 3:** Revise que los datos estén correctos y haga clic en **"Guardar"**.

**Resultado esperado:** El cliente queda registrado y aparece en la lista. El sistema muestra un mensaje de confirmación.

> **Importante sobre la cédula:** El número de cédula es el identificador principal para el registro de asistencia con valeras. Si el cliente va a adquirir una valera, la cédula es indispensable.

> **Importante sobre el correo electrónico:** Si ingresa el correo electrónico del cliente, el sistema le enviará automáticamente avisos cuando su membresía esté próxima a vencer.

> **Advertencia:** Si intenta registrar un cliente con un número de cédula que ya existe en el sistema, aparecerá un mensaje de error indicando que ese documento ya está registrado.

---

### 5.3 Ver y editar los datos de un cliente

**Paso 1:** Desde la lista de clientes, haga clic sobre el nombre del cliente que desea consultar.

**Paso 2:** Se abre la ficha completa del cliente con varias secciones.

[CAPTURA-010]
**Descripción:** Ficha completa de un cliente con todas sus secciones.
**Qué debe verse:** Pestañas o secciones con: datos personales, estado de membresía actual, historial de membresías, historial de pagos.
**Qué debe resaltarse:** El estado actual de la membresía (activa, vencida, congelada, etc.) con su color correspondiente.
**Por qué es importante:** Es la vista central desde donde se gestiona toda la relación con el cliente.

**Para editar los datos personales:**
- Haga clic en el botón **"Editar"** dentro de la ficha del cliente.
- Modifique los campos que necesite actualizar.
- Haga clic en **"Guardar"**.

---

### 5.4 Medidas corporales

**Cuándo:** Cuando el cliente solicita el registro de sus medidas de progreso físico.

**Paso 1:** Abra la ficha del cliente.

**Paso 2:** Haga clic en la pestaña **"Info"**.

**Paso 3:** En la sección de medidas corporales, ingrese los valores disponibles (peso, talla, medidas de circunferencia, etc.).

**Paso 4:** Haga clic en **"Guardar medidas"**.

[CAPTURA-011]
**Descripción:** Pestaña "Info" dentro de la ficha del cliente con el formulario de medidas corporales.
**Qué debe verse:** Campos para ingresar peso, talla y otras medidas corporales, con fechas de registro.
**Qué debe resaltarse:** Los campos de medidas y el botón para guardar.
**Por qué es importante:** Permite llevar un seguimiento del progreso físico del cliente a lo largo del tiempo.

---

### 5.5 Eliminar un cliente

**Cuándo:** Solo cuando sea completamente necesario. Esta acción no tiene reversa.

**Paso 1:** Abra la ficha del cliente.

**Paso 2:** Haga clic en el botón **"Eliminar cliente"**.

**Paso 3:** El sistema le pedirá confirmación. Lea el mensaje y confirme solo si está seguro.

> **ADVERTENCIA:** La eliminación de un cliente es permanente. Se borran todos sus datos, historial de membresías y pagos. Esta acción no se puede deshacer. Úsela solo cuando sea estrictamente necesario.

---

## 6. MEMBRESÍAS

### Objetivo
Crear, renovar, congelar y controlar el estado de las membresías de cada cliente.

### Descripción
Las membresías son los planes que contrata cada cliente para acceder al gimnasio. El sistema maneja varios tipos de plan (mensual, por días, valeras) y lleva el control automático de las fechas de vigencia.

### Cuándo usarlo
- Cuando un cliente se inscribe y necesita su primer plan
- Cuando un cliente renueva su membresía vencida o próxima a vencer
- Cuando un cliente necesita pausar temporalmente su membresía (congelar)
- Cuando un cliente regresa de una pausa (reactivar)

---

### 6.1 Crear una membresía nueva

**Cuándo:** Cuando un cliente se inscribe por primera vez o cuando no tiene ninguna membresía activa.

**Paso 1:** Abra la ficha del cliente (ver sección 5.3).

**Paso 2:** En la sección **"Membresía"**, haga clic en **"Crear membresía"**.

**Paso 3:** Seleccione el **plan** de la lista desplegable (Mensual, Plan Día, Valera 7, Valera 15, u otros planes disponibles).

**Paso 4:** Seleccione la **fecha de inicio**. Por defecto, el sistema sugiere el día de hoy.

**Paso 5:** Haga clic en **"Confirmar"**.

[CAPTURA-012]
**Descripción:** Modal o formulario de creación de membresía.
**Qué debe verse:** Un selector de plan, un campo de fecha de inicio y los botones de confirmar y cancelar.
**Qué debe resaltarse:** El selector de plan y la fecha de inicio.
**Por qué es importante:** Define el tipo de servicio que tendrá el cliente y desde cuándo empieza a correr su tiempo.

**Resultado esperado:** La membresía queda creada y se muestra el estado "Activa" en la ficha del cliente, con la fecha de vencimiento calculada automáticamente.

> **Aviso sobre cambio de valera a mensual:** Si el cliente tiene una valera activa con ingresos disponibles y usted intenta crear una membresía mensual, el sistema mostrará una advertencia con los ingresos que quedarían sin usar. Puede cancelar y esperar a que la valera se agote, o confirmar el cambio y la valera quedará desactivada.

---

### 6.2 Renovar una membresía

**Cuándo:** Cuando la membresía de un cliente está vencida o próxima a vencer y desea continuar.

**Paso 1:** Abra la ficha del cliente.

**Paso 2:** Haga clic en el botón **"Renovar membresía"**.

**Paso 3:** Seleccione el plan para la renovación (puede ser el mismo u otro diferente).

**Paso 4:** Confirme la renovación.

[CAPTURA-013]
**Descripción:** Modal de renovación de membresía sobre la ficha del cliente.
**Qué debe verses:** El selector de plan con la opción de elegir el mismo u otro plan, y los botones confirmar/cancelar.
**Qué debe resaltarse:** La opción de cambiar de plan durante la renovación.
**Por qué es importante:** La renovación registra automáticamente la nueva membresía y desactiva la anterior, manteniendo el historial limpio.

**Resultado esperado:** La nueva membresía queda activa desde hoy. La membresía anterior queda registrada en el historial del cliente.

---

### 6.3 Congelar una membresía

**Cuándo:** Cuando un cliente va a ausentarse por un período (viaje, lesión, etc.) y desea que los días no corran durante ese tiempo.

**Paso 1:** Abra la ficha del cliente.

**Paso 2:** Haga clic en el botón **"Congelar"** que aparece en la sección de membresía activa.

**Paso 3:** Confirme la acción.

[CAPTURA-014]
**Descripción:** Sección de membresía activa en la ficha del cliente con el botón "Congelar" visible.
**Qué debe verse:** El estado actual de la membresía y el botón "Congelar" disponible.
**Qué debe resaltarse:** El botón "Congelar" y el estado actual de la membresía.
**Por qué es importante:** El congelamiento detiene el conteo de días. El cliente no pierde los días pagados durante su ausencia.

**Resultado esperado:** La membresía pasa al estado **"Congelada"**. El sistema registra el día en que se congeló. Los días dejarán de contarse.

> **Límite de congelaciones:** Cada membresía puede congelarse un máximo de **3 veces**. Si ya se usaron los 3 congelamientos, el botón no estará disponible.

> **Nota:** Las membresías congeladas no aparecen en las alertas de vencimiento. El sistema reconoce que el cliente está en pausa autorizada.

---

### 6.4 Reactivar una membresía congelada

**Cuándo:** Cuando el cliente regresa y desea que su membresía vuelva a correr.

**Paso 1:** Abra la ficha del cliente.

**Paso 2:** Haga clic en el botón **"Reactivar"** que aparece cuando la membresía está congelada.

**Paso 3:** Confirme la acción.

**Resultado esperado:** La membresía vuelve al estado **"Activa"**. El sistema recalcula automáticamente la nueva fecha de vencimiento sumando los días que estuvo congelada.

[CAPTURA-015]
**Descripción:** Membresía en estado congelado con el botón "Reactivar" visible.
**Qué debe verse:** El estado "Congelada" de la membresía, la fecha de congelación y el botón "Reactivar".
**Qué debe resaltarse:** El botón "Reactivar" y el indicador de estado "Congelada".
**Por qué es importante:** La reactivación suma los días de pausa al vencimiento, garantizando que el cliente reciba todos los días que pagó.

---

### 6.5 Activar / desactivar una membresía manualmente

En casos excepcionales, es posible activar o desactivar una membresía de forma manual (independiente del estado del cliente). Este control aparece como un interruptor en la ficha del cliente.

> **Use esta opción con precaución.** Es para situaciones especiales acordadas con el cliente. El uso incorrecto puede generar inconsistencias en el historial.

---

### 6.6 Estados de una membresía

| Estado | Significado | Color en pantalla |
|--------|-------------|-------------------|
| **Activa** | Vigente, el cliente puede ingresar | Verde |
| **Por vencer** | Vence en los próximos 7 días | Naranja |
| **Vencida** | Expiró por fecha | Rojo |
| **Congelada** | Pausada temporalmente | Gris/Azul |
| **Agotada** | Solo para valeras: todos los ingresos usados | Amarillo |

---

## 7. PAGOS

### Objetivo
Registrar los pagos realizados por los clientes, consultar el historial de cobros y mantener el control financiero del gimnasio.

### Descripción
El módulo de Pagos registra cada cobro asociado a un cliente: mensualidades, inscripciones, pagos de planes especiales, etc. Los pagos de la tienda (ventas y abonos de cartera) se registran en el módulo de Tienda.

### Cuándo usarlo
- Cada vez que un cliente paga una membresía o cuota
- Cuando necesita consultar el historial de pagos de un cliente
- Cuando necesita revisar el total recaudado en un período

---

### 7.1 Registrar un pago

**Cuándo:** Cada vez que un cliente cancela el valor de su membresía u otro cobro del gimnasio.

**Paso 1:** Abra la ficha del cliente (módulo Clientes → seleccionar cliente).

**Paso 2:** En la sección **"Pagos"**, haga clic en **"Registrar pago"**.

**Paso 3:** Complete el formulario:

| Campo | Descripción |
|-------|-------------|
| **Monto** | Valor pagado en pesos |
| **Método de pago** | Efectivo, transferencia, tarjeta u otro |
| **Concepto** | Descripción del pago (ej. "Mensualidad julio", "Inscripción") |

**Paso 4:** Haga clic en **"Guardar"**.

[CAPTURA-016]
**Descripción:** Modal o formulario de registro de pago dentro de la ficha del cliente.
**Qué debe verse:** Los campos: monto, método de pago y concepto, con el botón "Guardar".
**Qué debe resaltarse:** El campo de monto y el selector de método de pago.
**Por qué es importante:** Cada pago registrado queda asociado al cliente y contribuye al total de ingresos del mes visible en el Dashboard.

**Resultado esperado:** El pago queda registrado y aparece en el historial de pagos del cliente. El total del mes en el Dashboard se actualiza automáticamente.

---

### 7.2 Consultar todos los pagos

**Paso 1:** En el menú lateral, haga clic en **"Pagos"**.

**Paso 2:** Se muestra una tabla con todos los pagos registrados en el sistema, ordenados del más reciente al más antiguo.

La tabla incluye: nombre del cliente, monto, método de pago, concepto y fecha.

[CAPTURA-017]
**Descripción:** Pantalla principal del módulo Pagos con la lista de todos los cobros.
**Qué debe verse:** Una tabla con columnas de cliente, monto, método, concepto y fecha.
**Qué debe resaltarse:** Las estadísticas de resumen en la parte superior (total del mes, total por método de pago).
**Por qué es importante:** Permite al administrador revisar todos los ingresos sin necesidad de entrar a la ficha de cada cliente.

---

### 7.3 Eliminar un pago registrado por error

**Cuándo:** Solo si el pago fue registrado por error (monto incorrecto, cliente equivocado, etc.).

**Paso 1:** En el módulo Pagos, ubique el pago que desea eliminar.

**Paso 2:** Haga clic en el ícono o botón de eliminar junto al pago.

**Paso 3:** Confirme la eliminación.

> **Advertencia:** La eliminación de un pago es permanente y no se puede deshacer. Verifique bien antes de confirmar.

---

## 8. ASISTENCIA — VALERAS

### Objetivo
Registrar el ingreso diario de clientes que tienen planes de asistencia por cantidad de visitas (valeras).

### Descripción
Las valeras son planes que otorgan al cliente un número determinado de ingresos al gimnasio durante un período de tiempo. Por ejemplo:
- **Valera 7:** 7 ingresos en 30 días
- **Valera 15:** 15 ingresos en 30 días

Cada vez que un cliente con valera llega al gimnasio, se registra su ingreso en este módulo. El sistema descuenta automáticamente un ingreso de su saldo disponible.

### Cuándo usarlo
- Cada vez que un cliente con valera ingresa al gimnasio
- Cuando el cliente o el recepcionista quieren saber cuántos ingresos quedan disponibles

---

### 8.1 Registrar un ingreso

**Paso 1:** En el menú lateral, haga clic en **"Asistencia"**.

**Paso 2:** En el campo **"Número de cédula"**, escriba el número de documento del cliente que está ingresando.

**Paso 3:** Haga clic en el botón **"Registrar ingreso"**.

[CAPTURA-018]
**Descripción:** Pantalla del módulo Asistencia con el campo de cédula y el botón de registrar ingreso.
**Qué debe verse:** Un campo de texto para ingresar la cédula y el botón "Registrar ingreso" claramente visible.
**Qué debe resaltarse:** El campo de cédula como único dato necesario para registrar la entrada.
**Por qué es importante:** Este es el proceso que se realiza cada vez que un cliente con valera llega al gimnasio. Debe ser rápido y sencillo.

**Resultado esperado:** El sistema muestra un mensaje de confirmación verde con:
- Nombre del cliente
- Ingresos totales del plan
- Ingresos usados (consumidos)
- Ingresos restantes
- Fecha de vencimiento de la valera

[CAPTURA-019]
**Descripción:** Mensaje de confirmación de ingreso exitoso en el módulo Asistencia.
**Qué debe verse:** Un banner verde con el nombre del cliente y el resumen de ingresos: total, consumidos y restantes.
**Qué debe resaltarse:** El número de ingresos restantes para comunicárselo al cliente.
**Por qué es importante:** Permite al recepcionista informar al cliente cuántos ingresos le quedan sin necesidad de buscar en otro módulo.

---

### 8.2 Posibles mensajes de error al registrar ingreso

| Mensaje | Significado | Qué hacer |
|---------|-------------|-----------|
| "Cliente no encontrado" | La cédula ingresada no existe en el sistema | Verifique el número de cédula. Si es un cliente nuevo, regístrelo primero en el módulo Clientes |
| "El cliente no tiene una valera activa" | El cliente no tiene valera o su valera venció o se agotó | Verifique con el cliente si necesita comprar una nueva valera |
| "Ya se registró un ingreso hoy" | El cliente ya entró hoy y no puede registrar dos veces en el mismo día | Informar al cliente que solo se permite un ingreso por día |
| "Valera vencida" | La valera expiró por fecha aunque queden ingresos | El cliente necesita renovar o adquirir una nueva valera |

---

### 8.3 Consultar el estado de una valera

**Cuándo:** Cuando el cliente o recepcionista quiere saber cuántos ingresos quedan sin necesidad de registrar una entrada.

**Paso 1:** En el módulo Asistencia, escriba la cédula del cliente.

**Paso 2:** Haga clic en el botón **"Consultar valera"**.

**Resultado esperado:** El sistema muestra el detalle completo de la valera:

| Dato | Descripción |
|------|-------------|
| **Total de ingresos** | Cuántos ingresos tiene el plan completo |
| **Consumidos** | Cuántos ingresos ya se usaron |
| **Restantes** | Cuántos ingresos quedan disponibles |
| **Vencimiento** | Fecha límite para usar los ingresos |
| **Estado** | Vigente, Agotada o Vencida |

[CAPTURA-020]
**Descripción:** Panel de consulta de estado de valera después de buscar por cédula.
**Qué debe verse:** Una tarjeta con los datos de la valera: total, consumidos, restantes, fecha de vencimiento y estado con badge de color.
**Qué debe resaltarse:** Los ingresos restantes y la fecha de vencimiento.
**Por qué es importante:** Permite al recepcionista comunicar proactivamente al cliente su saldo de ingresos.

---

### 8.4 Estados posibles de una valera

| Estado | Descripción | Puede ingresar |
|--------|-------------|----------------|
| **Vigente** | Tiene ingresos disponibles y no ha vencido | Sí |
| **Agotada** | Se usaron todos los ingresos disponibles | No |
| **Vencida** | Expiró la fecha de vencimiento, aunque queden ingresos | No |

---

## 9. TIENDA — VENTAS

### Objetivo
Gestionar la venta de productos al detal dentro del gimnasio, tanto al contado como a crédito.

### Descripción
El módulo de Tienda permite registrar ventas de productos (suplementos, ropa deportiva, accesorios, bebidas, etc.), llevar el inventario y controlar las ventas a crédito (cartera).

### Cuándo usarlo
- Cuando un cliente compra un producto de la tienda
- Cuando un cliente realiza un abono a su deuda pendiente
- Cuando necesita consultar el estado de la cartera
- Cuando necesita revisar ventas y reportes de tienda

---

### 9.1 Registrar una venta al contado

**Cuándo:** Cuando un cliente paga la compra en el momento.

**Paso 1:** En el menú lateral, haga clic en **"Tienda"**.

**Paso 2:** Haga clic en la pestaña **"Ventas"**.

**Paso 3:** En la sección del carrito de compra, busque el producto que desea vender (puede escribir el nombre para filtrar).

**Paso 4:** Haga clic en el producto para agregarlo al carrito. Ajuste la cantidad si es necesario.

[CAPTURA-021]
**Descripción:** Pantalla de ventas de la tienda con el catálogo de productos y el carrito.
**Qué debe verse:** A la izquierda o en la parte superior, la lista de productos disponibles. A la derecha o abajo, el carrito con los productos seleccionados y el total.
**Qué debe resaltarse:** El buscador de productos, el carrito y el botón de confirmar venta.
**Por qué es importante:** El proceso de venta debe ser rápido y claro para evitar errores al momento de cobrar.

**Paso 5:** Si desea asociar la venta a un cliente registrado (opcional), búsquelo en el campo "Cliente".

**Paso 6:** En el campo **"Método de pago"**, seleccione **"Contado"**.

**Paso 7:** Haga clic en **"Confirmar venta"**.

**Resultado esperado:** La venta queda registrada, el inventario se descuenta automáticamente y aparece el comprobante de la venta.

---

### 9.2 Registrar una venta a crédito

**Cuándo:** Cuando el cliente se lleva el producto pero pagará después (total o parcialmente).

Los pasos son idénticos a la venta al contado, con una diferencia:

**En el Paso 6:** Seleccione **"Crédito"** como método de pago.

**Resultado esperado:** La venta queda registrada con estado **"Pendiente"** y aparece en la sección **Cartera** hasta que sea pagada completamente.

> **Importante:** Para hacer ventas a crédito se recomienda vincular la venta a un cliente registrado, así podrá hacer seguimiento en la cartera.

---

### 9.3 Registrar un abono a cartera

**Cuándo:** Cuando un cliente viene a abonar parte o la totalidad de una deuda de tienda.

**Paso 1:** En el módulo Tienda, haga clic en la pestaña **"Cartera"**.

**Paso 2:** Busque la venta pendiente del cliente (por nombre o número de documento).

**Paso 3:** Haga clic en **"Abonar"** sobre la venta correspondiente.

**Paso 4:** Ingrese el monto del abono recibido.

**Paso 5:** Confirme el abono.

[CAPTURA-022]
**Descripción:** Pestaña "Cartera" en el módulo Tienda con la lista de deudas pendientes.
**Qué debe verse:** Una tabla con el nombre del cliente, el total de la venta, lo pagado hasta el momento, el saldo pendiente y el botón "Abonar".
**Qué debe resaltarse:** La columna "Saldo pendiente" y el botón "Abonar".
**Por qué es importante:** Permite controlar de forma precisa quién debe y cuánto, evitando confusiones al momento de cobrar abonos.

**Resultado esperado:** El abono queda registrado. Si el pago cubre el total de la deuda, la venta pasa automáticamente al estado **"Pagada"**.

---

### 9.4 Anular una venta

**Cuándo:** Cuando una venta fue registrada por error o el cliente devuelve el producto.

**Paso 1:** En la pestaña **"Ventas"**, busque y abra la venta que desea anular.

**Paso 2:** Haga clic en **"Anular venta"**.

**Paso 3:** Confirme la anulación.

**Resultado esperado:** La venta queda marcada como **"Anulada"**. El stock de los productos involucrados se repone automáticamente.

> **Nota:** Una venta anulada no puede reactivarse. Si fue un error, registre una nueva venta.

---

### 9.5 Gestionar clientes de tienda

La tienda maneja su propio registro de clientes, que puede incluir personas que compran en la tienda sin ser socios del gimnasio. También pueden vincularse clientes existentes del gimnasio.

**Pestaña "Clientes"** (dentro del módulo Tienda):
- Ver lista de clientes de tienda
- Agregar un cliente nuevo de tienda
- Vincular un cliente de tienda con un socio del gimnasio

---

### 9.6 Reportes de tienda

**Cuándo:** Cuando necesita ver el resumen de ventas, estado de cartera e inventario bajo stock para un período.

**Paso 1:** En el módulo Tienda, haga clic en la pestaña **"Reportes"**.

**Paso 2:** Seleccione el período de tiempo que desea analizar:
- Hoy
- Esta semana
- Este mes
- Rango personalizado (seleccione fecha inicio y fecha fin)

[CAPTURA-023]
**Descripción:** Pestaña "Reportes" del módulo Tienda con el selector de período.
**Qué debe verse:** Selector de período (Hoy/Semana/Mes/Personalizado) y debajo los KPIs de ventas: total de ventas, ingresos, ticket promedio, abonos cobrados.
**Qué debe resaltarse:** El selector de período y los KPIs principales.
**Por qué es importante:** Permite tomar decisiones informadas sobre el negocio sin necesidad de hacer cálculos manuales.

**Información disponible en los reportes:**

| Bloque | Datos que muestra |
|--------|-------------------|
| **Ventas** | Total de ventas, ingresos, ticket promedio, ventas al contado vs. crédito |
| **Top productos** | Los 5 productos más vendidos en el período |
| **Cartera** | Saldo total de deudas, clientes con deuda, deuda más antigua |
| **Inventario** | Productos con stock bajo el mínimo definido |

---

## 10. INVENTARIO

### Objetivo
Controlar el stock de productos de la tienda, registrar entradas de mercancía y ajustar cantidades cuando sea necesario.

### Descripción
El inventario lleva el conteo automático de cuántas unidades hay disponibles de cada producto. Cada venta descuenta unidades automáticamente. Cuando llega nueva mercancía, usted la ingresa manualmente.

### Cuándo usarlo
- Cuando llega mercancía nueva y necesita sumarla al inventario
- Cuando necesita corregir el stock de un producto (por ejemplo, después de un conteo físico)
- Cuando quiere ver el historial de movimientos de un producto

---

### 10.1 Ver el inventario actual

**Paso 1:** En el módulo Tienda, haga clic en la pestaña **"Productos"**.

**Paso 2:** La lista de productos muestra el stock actual de cada uno.

[CAPTURA-024]
**Descripción:** Pestaña "Productos" en el módulo Tienda con la lista de productos y su stock actual.
**Qué debe verse:** Una tabla de productos con nombre, categoría, precio, stock actual y stock mínimo.
**Qué debe resaltarse:** La columna "Stock" y cualquier producto con el stock en rojo o naranja (por debajo del mínimo).
**Por qué es importante:** Permite identificar de inmediato qué productos necesitan reabastecimiento.

Los productos cuyo stock está **por debajo del mínimo definido** aparecen marcados en naranja o rojo como alerta visual.

---

### 10.2 Registrar entrada de mercancía

**Cuándo:** Cuando llega un pedido de productos y necesita aumentar el stock disponible.

**Paso 1:** En la lista de Productos, haga clic en el producto al que va a ingresar mercancía.

**Paso 2:** Seleccione la opción **"Registrar entrada"** o **"Inventario"** (ícono de inventario).

**Paso 3:** En el formulario que aparece, ingrese:
- **Cantidad:** número de unidades que ingresaron
- **Notas:** descripción del movimiento (ej. "Pedido proveedor XYZ, factura #123")

**Paso 4:** Haga clic en **"Registrar entrada"**.

[CAPTURA-025]
**Descripción:** Modal o formulario de registro de entrada de inventario para un producto.
**Qué debe verse:** Campo de cantidad (positivo para entradas), campo de notas y botones de confirmar/cancelar.
**Qué debe resaltarse:** El campo de cantidad y el campo de notas como registro del origen de la mercancía.
**Por qué es importante:** Mantener el inventario actualizado evita vender productos que no hay en stock y permite detectar pérdidas o robos.

**Resultado esperado:** El stock del producto aumenta en la cantidad ingresada. El movimiento queda registrado en el historial.

---

### 10.3 Registrar un ajuste de stock

**Cuándo:** Cuando necesita corregir el stock por una diferencia entre el sistema y el conteo físico (por productos dañados, robos, errores de registro, etc.).

El proceso es similar al de entrada de mercancía, pero puede ingresar valores negativos para reducir el stock.

> **Recomendación:** Siempre ingrese una nota explicando el motivo del ajuste. Esto facilita las auditorías posteriores.

---

### 10.4 Gestionar productos y categorías

**Agregar un producto nuevo:**
1. En la pestaña "Productos", haga clic en **"Nuevo producto"**.
2. Complete: nombre, categoría, precio de venta y stock mínimo de alerta.
3. Guarde.

**Editar un producto:**
1. Haga clic en el producto de la lista.
2. Seleccione "Editar".
3. Modifique los campos necesarios y guarde.

**Activar / desactivar un producto:**
Un producto desactivado no aparece en el carrito de ventas, pero conserva su historial.

**Categorías:**
En la pestaña "Categorías" puede crear y gestionar las categorías para organizar los productos (ej. Suplementos, Ropa, Accesorios, Bebidas).

---

## 11. NOTIFICACIONES DE VENCIMIENTO

### Objetivo
Mantener informados a los clientes sobre el próximo vencimiento de su membresía mediante correos electrónicos automáticos.

### Descripción
El sistema envía automáticamente un correo electrónico a los clientes cuando su membresía está a punto de vencer. Los correos se envían a las **8:00 AM** cada día, para los clientes que vencen en exactamente **7, 3, 1 o 0 días**.

Para que esto funcione se necesita:
1. Que el cliente tenga registrado su correo electrónico en su ficha.
2. Que la configuración SMTP esté completada (ver sección 12).
3. Que el sistema de notificaciones esté activado.

### Cuándo usarlo
- Revisar el panel de notificaciones al inicio del día
- Ejecutar manualmente el ciclo de notificaciones si es necesario
- Consultar el historial de correos enviados

---

### 11.1 Panel de notificaciones en el Dashboard

El Dashboard incluye un panel resumen del estado de las notificaciones:

[CAPTURA-026]
**Descripción:** Panel de Notificaciones en el Dashboard del sistema.
**Qué debe verse:** Un indicador de estado (punto verde/amarillo/naranja), los contadores de correos enviados/fallidos/sin-email del día, y el botón "Ejecutar ahora".
**Qué debe resaltarse:** El indicador de estado y el contador "Sin email" que muestra clientes sin correo registrado.
**Por qué es importante:** Permite verificar de un vistazo si el sistema de notificaciones está funcionando correctamente.

**Indicadores de estado:**

| Indicador | Significado | Qué hacer |
|-----------|-------------|-----------|
| Punto **verde** | SMTP configurado y notificaciones activas | Todo en orden |
| Punto **amarillo** | Las notificaciones están desactivadas | Ir a Configuración y activar el toggle |
| Advertencia **naranja** | El SMTP no está configurado | Ir a Configuración y completar los datos SMTP |

**Contador "Sin email":** muestra cuántos clientes con membresía próxima a vencer no tienen correo electrónico registrado. Estos clientes no recibirán notificación automática — debe contactarlos manualmente.

---

### 11.2 Ejecutar el ciclo de notificaciones manualmente

**Cuándo:** Si necesita enviar las notificaciones en un momento específico sin esperar las 8:00 AM del día siguiente, o para verificar que el sistema funciona después de configurarlo.

**Paso 1:** En el Dashboard, ubique el panel de Notificaciones.

**Paso 2:** Haga clic en el botón **"Ejecutar ahora"**.

**Paso 3:** Espere unos segundos. El panel muestra el resultado: cuántos correos se enviaron, cuántos se omitieron (ya notificados anteriormente) y cuántos fallaron.

[CAPTURA-027]
**Descripción:** Panel de Notificaciones después de ejecutar el ciclo manualmente.
**Qué debe verse:** El resultado de la ejecución: "X enviados, Y omitidos, Z fallidos".
**Qué debe resaltarse:** Los tres números del resultado para evaluar si el ciclo funcionó correctamente.
**Por qué es importante:** Confirma que el sistema está enviando correos correctamente o permite identificar si hay un problema con la configuración.

---

### 11.3 Ver el historial de correos enviados

**Paso 1:** En el Dashboard, en el panel de Notificaciones, haga clic en **"Ver historial"**.

**Paso 2:** Se abre una ventana con la lista de todos los correos enviados, con:
- Nombre del cliente
- Plan de membresía
- Cuántos días antes del vencimiento se envió el correo
- Estado del envío (Enviado / Fallido)
- Fecha y hora del envío

[CAPTURA-028]
**Descripción:** Modal del historial de notificaciones enviadas.
**Qué debe verse:** Una tabla paginada con los correos enviados ordenados del más reciente al más antiguo. Columnas: cliente, plan, umbral (7d/3d/1d/0d), estado y fecha.
**Qué debe resaltarse:** Los correos con estado "Fallido" en rojo para identificar problemas.
**Por qué es importante:** Permite verificar que los clientes sí recibieron las notificaciones, y detectar si hay correos que no llegaron correctamente.

---

### 11.4 Qué hacer si hay correos fallidos

Si en el historial aparecen correos con estado **"Fallido"**:

1. Los correos fallidos se **reintentarán automáticamente** al día siguiente a las 8:00 AM. No requiere ninguna acción si el problema fue temporal (internet caído, servidor de correo no disponible momentáneamente).

2. Si los fallos **persisten por varios días**, puede indicar un problema con las credenciales del correo. Vaya a **Configuración → "Probar conexión"** para verificar.

3. Si "Probar conexión" falla, revise y corrija los datos del servidor SMTP en la sección de Configuración.

---

### 11.5 Qué pasa si un cliente no recibe el correo

Antes de concluir que hay un problema técnico, verifique:

1. **¿El cliente tiene correo registrado?**
   - Vaya a Clientes → ficha del cliente → pestaña Info. Si el campo de correo está vacío, regístrelo.

2. **¿La membresía del cliente es una valera?**
   - Las valeras no reciben notificaciones de vencimiento por correo (se gestionan por ingresos, no por fecha).

3. **¿La membresía está congelada?**
   - Las membresías congeladas tampoco generan notificaciones.

4. **¿En qué día vence la membresía?**
   - Las notificaciones se envían cuando faltan exactamente 7, 3, 1 o 0 días. Si la membresía vence en 5 días, el próximo correo saldrá cuando falten 3 días.

5. **Revise el historial** buscando el nombre del cliente para ver si hay registros de intentos fallidos.

---

## 12. CONFIGURACIÓN DEL SISTEMA

### Objetivo
Configurar el sistema de notificaciones por correo electrónico para que los clientes reciban avisos automáticos de vencimiento.

### Descripción
La página de Configuración permite al administrador ingresar los datos del correo electrónico del gimnasio que se usará para enviar notificaciones a los clientes.

### Cuándo usarlo
- La primera vez que se pone en marcha el sistema (configuración inicial del SMTP)
- Cuando cambia la contraseña del correo del gimnasio
- Cuando necesita pausar el envío automático de correos temporalmente

---

### 12.1 Acceder a Configuración

**Paso 1:** En el menú lateral izquierdo, haga clic en el ícono de **engranaje** o en la opción **"Configuración"**.

[CAPTURA-029]
**Descripción:** Pantalla principal de Configuración con el formulario SMTP.
**Qué debe verse:** Secciones: datos del servidor SMTP, datos del remitente, umbrales de notificación, toggle de activación y botones de guardar y probar conexión.
**Qué debe resaltarse:** El toggle "Activo" para activar/pausar notificaciones y el botón "Probar conexión".
**Por qué es importante:** Esta es la única pantalla del sistema donde se configura el envío de correos. Si no está configurada, los clientes no recibirán notificaciones automáticas.

---

### 12.2 Configurar el correo con Gmail

Si el gimnasio usa Gmail para enviar notificaciones:

> **Nota importante:** Gmail no permite usar la contraseña normal de la cuenta. Requiere una contraseña especial generada para aplicaciones. Siga estos pasos:

**Paso previo — Crear una contraseña de aplicación en Gmail:**

1. Abra un navegador e ingrese a: `myaccount.google.com` con la cuenta de Gmail del gimnasio.
2. Vaya a la sección **"Seguridad"**.
3. Active la **"Verificación en dos pasos"** si no está activada (es un requisito de Google).
4. Una vez activada, regrese a **"Seguridad"** y busque la opción **"Contraseñas de aplicación"**.
5. Cree una contraseña nueva para "Correo / Windows".
6. Google le mostrará una contraseña de **16 caracteres** con espacios (ej: `dqqo qeue bqrw uljl`). Cópiela **sin los espacios**: `dqqoqeuebqrwuljl`.

**Datos para ingresar en el formulario de Configuración:**

| Campo | Valor a ingresar |
|-------|-----------------|
| Servidor SMTP | `smtp.gmail.com` |
| Puerto | `587` |
| Usuario | El correo del gimnasio (ej: `migimnasio@gmail.com`) |
| Contraseña | Los 16 caracteres sin espacios |
| Nombre del remitente | El nombre del gimnasio (ej: `GYM Power`) |
| Correo remitente | El mismo correo del gimnasio |

---

### 12.3 Configurar el correo con Outlook

Si el gimnasio usa Outlook o Hotmail:

| Campo | Valor a ingresar |
|-------|-----------------|
| Servidor SMTP | `smtp.office365.com` |
| Puerto | `587` |
| Usuario | El correo del gimnasio (ej: `migimnasio@outlook.com`) |
| Contraseña | La contraseña normal de la cuenta Outlook |
| Nombre del remitente | El nombre del gimnasio |
| Correo remitente | El mismo correo del gimnasio |

---

### 12.4 Guardar y probar la configuración

**Paso 1:** Ingrese todos los datos del servidor SMTP.

**Paso 2:** Haga clic en **"Guardar configuración"**.

**Paso 3:** Haga clic en **"Probar conexión"**.

El sistema intentará conectarse al servidor de correo y enviará un mensaje de prueba **al mismo correo configurado como remitente**. Si funciona, verá un mensaje verde de éxito. Si falla, verá el mensaje de error.

[CAPTURA-030]
**Descripción:** Resultado del botón "Probar conexión" en la pantalla de Configuración.
**Qué debe verse:** Un mensaje en verde ("Conexión exitosa") o en rojo con el detalle del error.
**Qué debe resaltarse:** El color del mensaje de resultado.
**Por qué es importante:** Es la única manera de verificar que los datos del correo son correctos antes de depender de las notificaciones automáticas.

---

### 12.5 Umbrales de notificación

Los umbrales definen con cuántos días de anticipación se envía el aviso de vencimiento. Por defecto son: **7, 3, 1 y 0 días** antes del vencimiento.

- **7 días:** aviso con una semana de anticipación
- **3 días:** segundo aviso a 3 días del vencimiento
- **1 día:** recordatorio urgente
- **0 días:** aviso el mismo día del vencimiento

Puede modificar estos valores desde la sección de Configuración si desea cambiar los días de anticipación.

---

### 12.6 Activar o pausar las notificaciones

El toggle **"Activo"** en la página de Configuración permite activar o pausar el envío automático de correos sin borrar los datos de configuración.

- **Toggle encendido (azul):** el sistema envía correos automáticamente cada día a las 8:00 AM.
- **Toggle apagado (gris):** el sistema no envía correos hasta que se vuelva a activar.

---

## 13. TAREAS MÁS FRECUENTES

Esta sección reúne los procedimientos completos para las operaciones del día a día, en el orden en que se realizan con más frecuencia.

---

### 13.1 Registrar un cliente nuevo

**Cuándo:** Un nuevo socio se inscribe en el gimnasio.

1. Ir al módulo **Clientes** (menú lateral izquierdo).
2. Clic en **"Nuevo cliente"** (botón esquina superior derecha).
3. Ingresar **nombre completo** del cliente.
4. Ingresar **número de cédula** (sin puntos ni guiones).
5. Ingresar **teléfono** de contacto.
6. Ingresar **correo electrónico** (para notificaciones automáticas de vencimiento).
7. Clic en **"Guardar"**.
8. El sistema confirma con un mensaje verde. El cliente ya puede recibir membresías y pagos.

**Tiempo estimado:** 1-2 minutos.

---

### 13.2 Crear una membresía

**Cuándo:** Un cliente adquiere un plan por primera vez.

1. Buscar el cliente en el módulo **Clientes** (usar la barra de búsqueda).
2. Hacer clic sobre el nombre del cliente para abrir su ficha.
3. En la sección **"Membresía"**, hacer clic en **"Crear membresía"**.
4. Seleccionar el **plan** (ej. Mensual, Plan Día, Valera 7, Valera 15).
5. Verificar o ajustar la **fecha de inicio** (por defecto es hoy).
6. Clic en **"Confirmar"**.
7. Registrar el pago correspondiente (ver tarea 13.4).

**Tiempo estimado:** 2 minutos.

---

### 13.3 Renovar una membresía

**Cuándo:** Un cliente ya inscrito desea continuar con su membresía vencida o próxima a vencer.

1. Buscar el cliente en el módulo **Clientes**.
2. Abrir su ficha haciendo clic en el nombre.
3. En la sección de membresía, hacer clic en **"Renovar membresía"**.
4. Seleccionar el plan (puede ser el mismo u otro diferente).
5. Clic en **"Confirmar"**.
6. Registrar el pago de la renovación (ver tarea 13.4).

**Tiempo estimado:** 1-2 minutos.

---

### 13.4 Registrar un pago

**Cuándo:** Un cliente cancela el valor de su membresía u otro servicio.

1. Abrir la ficha del cliente (módulo Clientes → clic en el nombre).
2. En la sección **"Pagos"**, hacer clic en **"Registrar pago"**.
3. Ingresar el **monto** exacto recibido.
4. Seleccionar el **método de pago**: Efectivo / Transferencia / Tarjeta / Otro.
5. Ingresar el **concepto** del pago (ej. "Mensualidad julio 2026", "Valera 7 entradas").
6. Clic en **"Guardar"**.
7. El pago queda registrado y contribuye al total de ingresos del mes en el Dashboard.

**Tiempo estimado:** 1 minuto.

---

### 13.5 Registrar ingreso con valera

**Cuándo:** Un cliente con valera llega al gimnasio y debe registrarse.

1. Ir al módulo **Asistencia** (menú lateral izquierdo).
2. En el campo de cédula, escribir el **número de documento** del cliente.
3. Hacer clic en **"Registrar ingreso"**.
4. El sistema muestra el nombre del cliente y los ingresos restantes.
5. Informar al cliente cuántos ingresos le quedan disponibles.

**Si el sistema muestra un error:** revisar el mensaje (ver sección 8.2 de este manual).

**Tiempo estimado:** 30 segundos.

---

### 13.6 Registrar una venta en la tienda

**Cuándo:** Un cliente compra un producto de la tienda.

1. Ir al módulo **Tienda** → pestaña **"Ventas"**.
2. Buscar el producto en el catálogo (puede escribir el nombre para filtrar).
3. Hacer clic en el producto para agregarlo al carrito. Ajustar cantidad si el cliente lleva más de uno.
4. Repetir para cada producto adicional.
5. Si la venta es para un cliente registrado, seleccionarlo en el campo "Cliente" (opcional).
6. Seleccionar el **método de pago**: Contado o Crédito.
7. Hacer clic en **"Confirmar venta"**.
8. El stock se descuenta automáticamente.

**Tiempo estimado:** 1-2 minutos.

---

### 13.7 Registrar un abono a cartera

**Cuándo:** Un cliente que compró a crédito viene a abonar o cancelar su deuda.

1. Ir al módulo **Tienda** → pestaña **"Cartera"**.
2. Buscar al cliente (por nombre o documento) en la lista de deudas.
3. Identificar la venta pendiente del cliente.
4. Hacer clic en **"Abonar"**.
5. Ingresar el **monto recibido**.
6. Confirmar el abono.
7. Si el abono cubre el total, la venta pasa automáticamente a estado "Pagada".

**Tiempo estimado:** 1 minuto.

---

### 13.8 Congelar una membresía

**Cuándo:** Un cliente solicita pausar su membresía porque no puede asistir por un período.

1. Buscar el cliente en el módulo **Clientes**.
2. Abrir su ficha.
3. En la sección de membresía, hacer clic en **"Congelar"**.
4. Confirmar la acción.
5. El estado de la membresía cambia a **"Congelada"**.
6. Los días no correrán hasta que el cliente regrese.

**Límite:** máximo 3 congelaciones por membresía.

**Tiempo estimado:** 1 minuto.

---

### 13.9 Reactivar una membresía congelada

**Cuándo:** El cliente regresa después de una pausa y desea retomar su membresía.

1. Buscar el cliente en el módulo **Clientes**.
2. Abrir su ficha.
3. Verificar que la membresía aparece como **"Congelada"**.
4. Hacer clic en **"Reactivar"**.
5. Confirmar.
6. El sistema calcula automáticamente la nueva fecha de vencimiento sumando los días de pausa.

**Tiempo estimado:** 1 minuto.

---

### 13.10 Consultar la cartera de la tienda

**Cuándo:** El administrador quiere revisar quién debe y cuánto.

**Opción rápida — desde el Dashboard:**
- En el Dashboard, revisar la sección "Alertas operativas" → pestaña **"Cartera"**.
- Muestra los 5 clientes con mayor deuda pendiente.

**Vista completa — desde el módulo Tienda:**
1. Ir al módulo **Tienda** → pestaña **"Cartera"**.
2. Se muestra la lista completa de ventas pendientes con saldos por cliente.
3. También puede consultar los reportes en la pestaña **"Reportes"** → bloque Cartera.

---

### 13.11 Consultar vencimientos de membresías

**Cuándo:** El administrador quiere ver qué clientes vencen próximamente para contactarlos.

**Desde el Dashboard:**
1. En la sección **"Alertas operativas"**, revisar las pestañas:
   - **"Hoy"**: vencen hoy
   - **"3 días"**: vencen en los próximos 3 días
   - **"7 días"**: vencen en la próxima semana
   - **"Vencidas"**: ya vencidas (con filtro por antigüedad)

2. En cada pestaña puede buscar un cliente específico por nombre o cédula.

**Tiempo estimado:** 2-3 minutos para revisar todas las pestañas.

---

### 13.12 Revisar alertas operativas del negocio

**Cuándo:** Al inicio del día o cuando el administrador quiere tener una visión general de situaciones que requieren atención.

1. Ir al **Dashboard** (módulo principal).
2. Revisar las tarjetas de resumen superiores para ver los conteos de membresías activas, por vencer, vencidas, congeladas y valeras agotadas.
3. Desplazarse hasta la sección **"Alertas operativas"**.
4. Revisar cada pestaña:
   - **Vencidas:** contactar a esos clientes para renovar
   - **Hoy / 3 días / 7 días:** prepararse para renovaciones próximas
   - **Cartera:** hacer seguimiento a clientes con deuda
   - **Bajo stock:** programar pedidos de mercancía
5. Revisar el panel **"Notificaciones"**: verificar el estado del envío automático de correos.

**Tiempo estimado:** 5-10 minutos de revisión matutina.

---

## 14. PROBLEMAS FRECUENTES

Esta sección describe los problemas más comunes que pueden presentarse y cómo resolverlos sin necesidad de llamar al soporte técnico.

---

### 14.1 El sistema no abre en el navegador

**Síntoma:** Al escribir `http://localhost` en el navegador, aparece una página de error ("No se puede acceder a este sitio", "ERR_CONNECTION_REFUSED" u otro mensaje de error).

**Posible causa:** El sistema aún no ha terminado de arrancar, o Docker Desktop no está corriendo.

**Solución paso a paso:**

1. Mire la barra de tareas en la esquina inferior derecha de la pantalla (junto al reloj).
2. Busque el ícono de Docker Desktop (figura de ballena azul).
3. **Si el ícono no aparece:** Abra Docker Desktop desde el menú Inicio de Windows. Espere 1-2 minutos mientras arranca.
4. **Si el ícono aparece pero está animado (moviéndose):** Espere hasta que deje de moverse, luego recargue la página (F5).
5. **Si el ícono aparece estático y la página sigue sin cargar:** Espere 1 minuto adicional y vuelva a intentar. El sistema puede tardar un momento en terminar de inicializar.
6. Si después de 3 minutos sigue sin cargar, contacte al soporte técnico.

**Cuándo contactar soporte:** Si después de reiniciar Docker Desktop y esperar 3 minutos el sistema sigue sin cargar.

---

### 14.2 Docker Desktop no está iniciado o no aparece

**Síntoma:** El ícono de Docker no aparece en la barra de tareas y el sistema no carga.

**Posible causa:** Docker Desktop no arrancó automáticamente al encender el PC.

**Solución paso a paso:**

1. Haga clic en el botón de **Inicio de Windows** (esquina inferior izquierda).
2. Escriba **"Docker Desktop"** en el buscador.
3. Haga clic en el resultado para abrir Docker Desktop.
4. Espere a que aparezca la pantalla de Docker y el estado cambie a "Engine running" (motor en ejecución). Esto puede tardar 1-2 minutos.
5. Una vez listo, intente abrir el sistema en `http://localhost`.

**Cuándo contactar soporte:** Si Docker Desktop muestra un error al arrancar o si el estado nunca llega a "Engine running".

---

### 14.3 No aparecen clientes en la lista

**Síntoma:** La pantalla del módulo Clientes aparece vacía o no muestra ningún cliente.

**Posibles causas y soluciones:**

**Causa 1 — Filtro de búsqueda activo:**
- Revise si hay texto escrito en la barra de búsqueda de clientes.
- Si hay texto, bórrelo y la lista completa volverá a aparecer.

**Causa 2 — El sistema aún está cargando:**
- Espere unos segundos y vuelva a hacer clic en "Clientes".
- Recargue la página con F5.

**Causa 3 — El sistema recién fue instalado o los datos se borraron:**
- Si el sistema es nuevo, es normal que no haya clientes. Empiece registrando el primero.
- Si había clientes antes y ahora no aparecen, contacte soporte de inmediato (puede indicar un problema con los datos).

**Cuándo contactar soporte:** Si borró el texto de búsqueda, recargó la página, y la lista sigue vacía pese a que antes había clientes registrados.

---

### 14.4 No se puede registrar un pago

**Síntoma:** Al intentar registrar un pago, el formulario no guarda o aparece un mensaje de error.

**Posibles causas y soluciones:**

**Causa 1 — Campos incompletos:**
- Verifique que el monto esté ingresado (no puede estar en blanco o en cero).
- Verifique que se seleccionó un método de pago.

**Causa 2 — El monto tiene formato incorrecto:**
- No use puntos como separador de miles. Si el valor es cien mil pesos, escriba `100000`, no `100.000`.
- No use caracteres especiales (signos de pesos, letras, etc.).

**Causa 3 — Problema de conectividad interna:**
- Recargue la página con F5 e intente nuevamente.

**Cuándo contactar soporte:** Si después de corregir el formato sigue sin guardar y aparece un mensaje de error en rojo.

---

### 14.5 No se puede registrar la asistencia de un cliente con valera

**Síntoma:** Al ingresar la cédula en el módulo Asistencia, el sistema muestra un error o no permite registrar el ingreso.

**Posibles causas y soluciones:**

**Causa 1 — Cédula no registrada:**
- Mensaje: "Cliente no encontrado".
- El cliente no está registrado en el sistema o se ingresó la cédula incorrecta.
- Verifique el número de documento y, si es necesario, registre primero al cliente en el módulo Clientes.

**Causa 2 — El cliente no tiene valera activa:**
- Mensaje: "El cliente no tiene una valera activa".
- El cliente venció su valera o no tiene ninguna. Necesita adquirir una nueva.

**Causa 3 — Ya se registró la asistencia del día:**
- Mensaje: "Ya se registró un ingreso hoy".
- Solo se permite un ingreso por día por valera. Si el cliente ya entró, no puede volver a registrarse ese mismo día.

**Causa 4 — La valera está agotada o vencida:**
- El cliente usó todos sus ingresos o la valera expiró por fecha.
- Necesita una nueva valera.

**Cuándo contactar soporte:** Si el mensaje de error no corresponde a ninguno de los anteriores o si el sistema se comporta de manera extraña (no responde, se congela).

---

### 14.6 No se envían correos de notificación a los clientes

**Síntoma:** Los clientes no están recibiendo correos de aviso aunque su membresía está próxima a vencer.

**Verificación paso a paso:**

**Paso 1 — Revisar el estado en el Dashboard:**
- Vaya al Dashboard y busque el panel de **"Notificaciones"**.
- Si hay un punto **naranja** o un mensaje de advertencia, el SMTP no está configurado o hay un error de conexión.

**Paso 2 — Verificar que el cliente tiene correo registrado:**
- Vaya a Clientes → ficha del cliente → pestaña "Info".
- Si el campo de correo está vacío, agrégalo.

**Paso 3 — Verificar el tipo de membresía:**
- Las valeras no reciben notificaciones. Solo los planes mensuales y similares.

**Paso 4 — Verificar que el sistema está activo:**
- Vaya a **Configuración** y revise que el toggle "Activo" está encendido (azul).

**Paso 5 — Probar la conexión:**
- En Configuración, haga clic en **"Probar conexión"**.
- Si falla, el error indicado le dará la pista del problema (contraseña incorrecta, servidor equivocado, etc.).

**Paso 6 — Ejecutar manualmente:**
- En el Dashboard, haga clic en **"Ejecutar ahora"** para forzar el envío.

**Cuándo contactar soporte:** Si "Probar conexión" falla con un mensaje que no entiende, o si solucionó el problema pero los correos siguen sin enviarse.

---

### 14.7 Problemas con el inventario de la tienda

**Síntoma:** El stock de un producto no coincide con la cantidad real en el establecimiento.

**Posibles causas y soluciones:**

**Causa 1 — Una venta fue registrada con cantidad incorrecta:**
- Verifique en el historial de movimientos del producto (Tienda → Productos → producto → Inventario) cuál fue el último movimiento.
- Si fue una venta incorrecta, considere anularla y volverla a registrar correctamente.

**Causa 2 — Se perdió o dañó mercancía sin registrar el ajuste:**
- Registre un ajuste de inventario con la cantidad negativa correspondiente.
- Use la nota del ajuste para documentar el motivo (ej. "Producto dañado 2026-06-17").

**Causa 3 — Ingresó mercancía nueva sin registrarla:**
- Use la función de **"Registrar entrada"** en el producto para actualizar el stock.

**Cuándo contactar soporte:** Si el historial de movimientos muestra datos incoherentes que no corresponden a las operaciones realizadas.

---

## 15. BUENAS PRÁCTICAS OPERATIVAS

Esta sección recoge las recomendaciones de uso del sistema para que el gimnasio funcione sin contratiempos.

---

### 15.1 Hábitos diarios recomendados

**Al comenzar el día:**
- Abrir el sistema y revisar el Dashboard antes de atender el primer cliente.
- Revisar las pestañas "Hoy" y "3 días" en Alertas operativas para identificar membresías que vencen.
- Contactar proactivamente a los clientes cuya membresía vence hoy o mañana.
- Revisar el indicador de "Bajo stock" para detectar productos que necesitan reposición.

**Durante el día:**
- Registrar cada pago en el momento en que se recibe — no acumular pagos para registrarlos al final.
- Registrar el ingreso de cada cliente con valera en el momento en que llega — nunca omitir este paso.
- Al vender en la tienda, confirmar siempre el método de pago (contado o crédito) con el cliente.

**Al finalizar el día:**
- Verificar en el Dashboard que los ingresos del día estén reflejados correctamente.
- No es necesario apagar el sistema manualmente. Al apagar el computador, todo queda guardado automáticamente.

---

### 15.2 Registro de pagos

- Registre el pago el **mismo día** en que se crea o renueva la membresía. No deje pagos pendientes de registrar.
- Use siempre el campo "Concepto" para describir qué se está pagando. Esto facilita revisar el historial en el futuro.
- Si un cliente paga en cuotas, registre cada cuota por separado con el monto exacto recibido.

---

### 15.3 Registro de clientes

- Siempre solicite y registre la **cédula** del cliente al inscribirlo. La cédula es indispensable para el registro de asistencia con valeras.
- Solicite el **correo electrónico** del cliente al inscribirlo. Esto permite que el sistema envíe notificaciones automáticas de vencimiento.
- Si el cliente no quiere dar su correo, no es obligatorio — pero no recibirá avisos automáticos.
- Actualice el teléfono de contacto si el cliente reporta que cambió de número.

---

### 15.4 Gestión de la tienda

- Antes de registrar una entrada de mercancía, cuente físicamente los productos recibidos y verifique que coincidan con el pedido.
- Configure un stock mínimo razonable para cada producto. Esto permite que el sistema le avise automáticamente antes de que se quede sin stock.
- Realice un conteo físico del inventario al menos **una vez al mes** y compárelo con el sistema. Si hay diferencias, registre ajustes con el motivo correspondiente.
- Para ventas a crédito, asegúrese de vincular la venta a un cliente registrado para facilitar el seguimiento de la cartera.

---

### 15.5 Notificaciones y correos

- Configure el SMTP desde el inicio para que el sistema comience a enviar avisos de vencimiento desde el primer día.
- Registre el correo electrónico de todos los clientes para maximizar el alcance de las notificaciones automáticas.
- Revise semanalmente el contador "Sin email" en el Dashboard y contacte a esos clientes para actualizar su información.
- Si un cliente solicita no recibir correos, puede dejar el campo de email vacío en su ficha.

---

### 15.6 Respaldos de los datos

El sistema realiza respaldos automáticos de todos los datos **todos los días a las 2:00 AM**. Estos respaldos son automáticos y no requieren ninguna acción de su parte.

Sin embargo, recomendamos:

**Respaldo manual mensual:**
- En el Dashboard, busque el panel de **"Respaldos"**.
- Haga clic en **"Crear respaldo manual"** al menos una vez por mes.

[CAPTURA-031]
**Descripción:** Panel de Respaldos en el Dashboard con el indicador de estado y el botón de respaldo manual.
**Qué debe verse:** La fecha del último respaldo automático, el indicador de estado (verde si es reciente, naranja si lleva más de 24 horas) y el botón "Crear respaldo manual".
**Qué debe resaltarse:** La fecha del último respaldo y el botón de respaldo manual.
**Por qué es importante:** Los respaldos son la garantía de que los datos del negocio están seguros. Un respaldo reciente permite recuperar toda la información en caso de un problema grave.

> **Advertencia crítica:** Nunca realice operaciones de mantenimiento del computador (formateo, reinstalación de Windows, eliminación de carpetas del sistema) sin confirmar primero con el soporte técnico que los datos están respaldados. La pérdida de datos es irreversible si no hay respaldo.

---

### 15.7 Seguridad del sistema

- No comparta el acceso al computador del sistema con personas que no sean personal del gimnasio.
- Bloquee o apague el computador cuando no esté en uso y haya personas ajenas al establecimiento.
- No instale programas o aplicaciones en el computador del sistema sin consultar con el soporte técnico.
- No ejecute comandos en la terminal del computador a menos que el soporte técnico se lo indique expresamente.
- Si detecta comportamientos extraños en el sistema (datos que cambian solos, errores inesperados, lentitud inusual), notifique al soporte técnico.

---

## 16. CONTACTO DE SOPORTE

Si encuentra un problema que no está cubierto en la sección **14. Problemas frecuentes**, o si el sistema presenta un comportamiento que no puede resolver siguiendo las instrucciones de este manual, contacte al equipo de soporte técnico.

---

### Información de contacto

| Canal | Datos |
|-------|-------|
| **Responsable técnico** | *(completar con nombre del técnico responsable)* |
| **Teléfono / WhatsApp** | *(completar con número de contacto)* |
| **Correo electrónico** | *(completar con correo de soporte)* |
| **Horario de atención** | *(completar con horario disponible)* |

---

### Antes de contactar soporte, tenga listos los siguientes datos:

1. **Descripción del problema:** ¿Qué estaba haciendo cuando ocurrió el error?
2. **Mensaje de error:** Si el sistema muestra un mensaje de error, anótelo o tome una foto a la pantalla.
3. **Módulo afectado:** ¿En qué sección del sistema ocurrió? (Clientes, Membresías, Pagos, Tienda, etc.)
4. **Frecuencia:** ¿El error ocurrió una vez o se repite siempre?
5. **Tiempo:** ¿Desde cuándo está ocurriendo este problema?

Tener esta información lista permite al soporte técnico resolver el problema de manera más rápida y eficiente.

---

### Capturas de pantalla

Cuando contacte soporte, es muy útil enviar una captura de pantalla del error. Para tomar una captura en Windows:

1. Presione la tecla **Windows + Mayúscula + S** simultáneamente.
2. Seleccione el área de la pantalla que desea capturar.
3. La imagen se guarda en el portapapeles y puede pegarla directamente en WhatsApp o correo electrónico.

---

*Este manual es propiedad del Sistema de Gestión de Gimnasio. Versión 1.0 — Junio 2026.*
*Para solicitar actualizaciones de este documento, contacte al soporte técnico.*

---

## ÍNDICE DE CAPTURAS DE IMAGEN

| Captura | Sección | Descripción |
|---------|---------|-------------|
| CAPTURA-001 | 3. Inicio | Docker Desktop en la barra de tareas |
| CAPTURA-002 | 3. Inicio | Navegador con la dirección del sistema |
| CAPTURA-003 | 3. Inicio | Dashboard recién cargado |
| CAPTURA-004 | 4. Dashboard | Tarjetas de indicadores principales |
| CAPTURA-005 | 4. Dashboard | Sección Ingresos del mes |
| CAPTURA-006 | 4. Dashboard | Tabla Membresías por plan |
| CAPTURA-007 | 4. Dashboard | Panel de Alertas operativas con pestañas |
| CAPTURA-008 | 5. Clientes | Lista de clientes |
| CAPTURA-009 | 5. Clientes | Formulario de nuevo cliente |
| CAPTURA-010 | 5. Clientes | Ficha completa del cliente |
| CAPTURA-011 | 5. Clientes | Pestaña Info con medidas corporales |
| CAPTURA-012 | 6. Membresías | Formulario de creación de membresía |
| CAPTURA-013 | 6. Membresías | Modal de renovación de membresía |
| CAPTURA-014 | 6. Membresías | Botón Congelar en membresía activa |
| CAPTURA-015 | 6. Membresías | Membresía congelada con botón Reactivar |
| CAPTURA-016 | 7. Pagos | Formulario de registro de pago |
| CAPTURA-017 | 7. Pagos | Lista de todos los pagos |
| CAPTURA-018 | 8. Asistencia | Campo de cédula y botón Registrar ingreso |
| CAPTURA-019 | 8. Asistencia | Confirmación de ingreso exitoso |
| CAPTURA-020 | 8. Asistencia | Consulta de estado de valera |
| CAPTURA-021 | 9. Tienda | Pantalla de ventas con carrito |
| CAPTURA-022 | 9. Tienda | Pestaña Cartera con botón Abonar |
| CAPTURA-023 | 9. Tienda | Pestaña Reportes con selector de período |
| CAPTURA-024 | 10. Inventario | Lista de productos con stock actual |
| CAPTURA-025 | 10. Inventario | Formulario de entrada de inventario |
| CAPTURA-026 | 11. Notificaciones | Panel de notificaciones en Dashboard |
| CAPTURA-027 | 11. Notificaciones | Resultado de ejecutar el ciclo manualmente |
| CAPTURA-028 | 11. Notificaciones | Historial de correos enviados |
| CAPTURA-029 | 12. Configuración | Formulario SMTP en Configuración |
| CAPTURA-030 | 12. Configuración | Resultado del botón Probar conexión |
| CAPTURA-031 | 15. Buenas prácticas | Panel de Respaldos en Dashboard |
