# PRODUCT_VISION.md — Gym Platform

> Documento fundacional de producto. Fuente oficial de verdad para la evolución de la plataforma.
> Versión: 1.0 — aprobada por producto. Fecha: junio 2026.

---

## Declaración de Visión

Gym Platform es una **plataforma integral de gestión, operación, comercialización y fidelización para gimnasios independientes**. Diseñada para el mercado latinoamericano, permite a cualquier gimnasio digitalizar completamente su operación desde una instalación local simple, y crecer hacia canales digitales avanzados sin cambiar de plataforma ni de proveedor.

---

## Misión

Democratizar el acceso a tecnología de gestión empresarial para gimnasios independientes, ofreciendo una plataforma modular que crece con el negocio: desde el control básico de membresías hasta la fidelización digital de clientes y la analítica predictiva de comportamiento.

---

## Mercado Objetivo

### Segmento primario
Gimnasios independientes en Colombia y América Latina con entre 30 y 500 miembros activos:

- Micro-gyms y boxes funcionales (CrossFit, calistenia, funcional, HIIT)
- Studios especializados (yoga, pilates, artes marciales, baile, spinning)
- Gimnasios tradicionales establecidos con operación diaria y staff permanente
- Nuevos emprendimientos fitness en proceso de formalización

### Segmento secundario (F5+)
Gimnasios de alto volumen (500+ miembros) y cadenas locales con múltiples sedes en una misma ciudad que buscan una solución unificada sin la complejidad de un ERP.

### Fuera del alcance actual
Cadenas nacionales o franquicias con sistemas propios, gimnasios corporativos integrados a ERPs empresariales, o mercados fuera de América Latina con regulaciones contables distintas.

---

## Propuesta de Valor

| Para quién | El problema | Nuestra solución |
|---|---|---|
| Dueño de gimnasio | Opera con Excel, WhatsApp y papel | Core digital completo desde el día 1 |
| Administrador | No sabe cuántos clientes vencen hoy | Dashboard con alertas en tiempo real |
| Recepcionista | Cobros manuales, errores, olvidos | Membresías + pagos + recordatorios automáticos |
| Cliente del gimnasio | No tiene canal directo con su gym | App móvil, cobros online, comunicación proactiva |
| Propietario en crecimiento | No puede medir retención ni churn | Analítica avanzada e inteligencia predictiva |

---

## Posicionamiento

Gym Platform **no es un POS para gimnasios**. Es la infraestructura digital completa del gimnasio: el sistema que gestiona la operación diaria, automatiza la comunicación, habilita los cobros online, digitaliza el acceso físico, pone la marca del gimnasio en el celular de sus clientes y predice qué miembros están a punto de cancelar antes de que lo hagan.

El diferenciador no es el precio ni una funcionalidad aislada. Es la **progresión coherente**: un gimnasio puede empezar con el módulo mínimo viable y adoptar nuevas capacidades a medida que su operación lo justifica, sin migrar de plataforma ni perder el historial.

---

## Principios Estratégicos

**1. Modularidad progresiva.**
Cada gimnasio comienza con lo que necesita y agrega módulos cuando su operación lo justifica. No hay funcionalidades forzadas, no hay bloatware. El plan más básico es completamente funcional desde el primer día.

**2. Instalación local primero.**
La plataforma opera sobre la infraestructura del cliente (PC local + Docker) sin dependencia de conectividad permanente para la operación Core. Los datos del gimnasio son propiedad del gimnasio, no del proveedor.

**3. Un sistema, múltiples clientes.**
El código fuente es único y no contiene referencias a clientes específicos. La diferenciación entre instalaciones vive exclusivamente en la configuración (`.env`) y los datos (`gym.db`), nunca en el código.

**4. Crecimiento guiado por valor percibido.**
El modelo comercial está diseñado para que el cliente adopte nuevos módulos cuando experimenta el dolor que resuelven, no por presión de ventas. El upsell correcto llega en el momento correcto del journey del cliente.

**5. Plataforma, no aplicación.**
El objetivo no es vender una herramienta de registro. Es construir la infraestructura digital del gimnasio de forma que cada módulo agregado aumente el valor del conjunto y el costo de cambiar de proveedor.

**6. Arquitectura que no obliga a reescribir.**
Cada decisión de arquitectura actual (repo único, feature flags, Docker, SQLite) debe ser compatible con la evolución futura hacia cloud. No se construye para el estado final: se construye para que el camino hacia ese estado no requiera tirar lo que ya funciona.

---

## Rhinopower — Primer Cliente de Referencia

Rhinopower Gym es el gimnasio que validó la versión inicial de la plataforma (Local Edition v1.1, F3 — cerrada). Opera con el Core Platform completo en producción desde 2025 y sirve como referencia de implementación para nuevos clientes.

Todas las funcionalidades del Core Platform fueron validadas en producción real en Rhinopower antes de su comercialización. El nombre "Rhinopower" no aparece en el código fuente de la plataforma. Rhinopower es un cliente, no el producto.

---

## Visión a 5 Años

Una plataforma operando en 100+ gimnasios en Colombia y al menos 3 países de América Latina, con módulos Premium maduros (App Móvil, Control de Acceso, IA Predictiva) y un modelo de licenciamiento que genera ARR sostenible para financiar la evolución continua del producto.

La transición a modelo SaaS cloud (F8+) se evaluará cuando la base de clientes ISV supere los 20 gimnasios activos y exista demanda validada de acceso multi-dispositivo sin instalación local. Ese movimiento no se anticipa en el diseño actual; se adopta cuando las condiciones lo justifiquen.
