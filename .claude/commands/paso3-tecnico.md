Paso 3 — Diseño técnico (sin implementar)
Guardia de paso

Verifica que el usuario haya aprobado explícitamente el Paso 2.

Si no existe aprobación registrada, responde:

Completa y aprueba /paso2-funcional primero.

y detente.

Objetivo

Definir el diseño técnico de la funcionalidad propuesta utilizando la arquitectura existente del proyecto.

Este paso busca identificar el impacto técnico, los componentes afectados y la estrategia de implementación antes de escribir código.

Instrucciones
NO implementar código.
NO modificar archivos.
NO generar documentación final.
NO diseñar detalles de implementación.
Basarse únicamente en el estado actual del proyecto.
Enfocarse en arquitectura, impacto técnico y estrategia de ejecución.
Inspección previa obligatoria

Antes de generar el diseño:

Leer documentación relevante.
Inspeccionar archivos relacionados.
Identificar la arquitectura existente.
Identificar patrones ya utilizados.
Verificar convenciones actuales.
No asumir comportamientos ni estructuras.
Optimización obligatoria de contexto

Antes de generar el análisis:

Revisar resultados aprobados de:
Paso 1 — Valor
Paso 2 — Diseño funcional
Reutilizar decisiones ya aprobadas.
No repetir:
análisis de negocio,
análisis funcional,
casos de uso,
justificaciones ya documentadas.
Referenciar brevemente decisiones previas cuando sea suficiente.
Analizar únicamente el impacto técnico necesario para tomar decisiones de implementación.

Objetivo: minimizar consumo de tokens evitando análisis duplicados.

Genera el diseño técnico
1. Componentes afectados

Para cada elemento afectado indicar:

Ruta exacta.
Tipo:
Modelo
Servicio
API
Página
Componente
Script
Configuración
Otro
Motivo del cambio.
2. Arquitectura impactada

Identificar:

Capas involucradas.
Flujo actual.
Flujo propuesto.
Componentes reutilizables.
Dependencias relevantes.
3. Impacto sobre estructuras existentes

Indicar únicamente:

Estructuras nuevas requeridas.
Estructuras existentes afectadas.
Compatibilidad con la solución actual.

No diseñar modelos detallados ni estructuras completas.

4. Backend

Describir:

APIs afectadas.
Servicios afectados.
Repositorios afectados.
Procesos afectados.
Reglas de negocio impactadas.

Si no aplica, indicarlo explícitamente.

5. Frontend

Describir:

Pantallas afectadas.
Componentes afectados.
Formularios afectados.
Navegación afectada.
Visualización de información impactada.

Si no aplica, indicarlo explícitamente.

6. Documentación

Indicar qué documentos requieren actualización.

Ejemplos:

FEATURE_SUMMARY.md
TECH_DEBT.md
REQUERIMIENTOS.md
ARQUITECTURA.md
ADRs
Otros
7. Riesgos técnicos

Para cada riesgo indicar:

Descripción.
Probabilidad:
Alta
Media
Baja
Impacto.
Mitigación propuesta.

Registrar únicamente riesgos relevantes.

8. Estrategia de implementación

Definir:

Orden recomendado de ejecución.
Dependencias entre tareas.
Posibles fases.
Estrategia de validación por fase.

Mantener el nivel de detalle necesario para planificar el trabajo.

9. Blast Radius

Indicar:

Funcionalidades potencialmente afectadas.
Validaciones necesarias.
Estrategia para minimizar regresiones.
Estimación

Indicar:

Complejidad:
Baja
Media
Alta
Cantidad aproximada de archivos a modificar.
Cantidad aproximada de archivos nuevos.

Las estimaciones deben ser aproximadas y orientativas.

Regla de validación estructural

Si la funcionalidad implica alguno de los siguientes escenarios:

Nuevos módulos.
Nuevos componentes principales.
Nuevas estructuras de información.
Integraciones externas.
Procesos complejos.
Cambios arquitectónicos relevantes.
Impacto transversal sobre múltiples áreas del sistema.

Debe ejecutarse el Paso 3.5 — Validación estructural antes del Paso 4.

No avanzar a implementación hasta completar y aprobar el Paso 3.5 cuando aplique.

Cierre

Finalizar con:

Diseño técnico completo. ¿Apruebas continuar al siguiente paso requerido?

Si aplica Paso 3.5, solicitar aprobación para continuar a Paso 3.5.

Si no aplica Paso 3.5, solicitar aprobación para continuar a Paso 4 — Implementación.

No avanzar sin aprobación explícita