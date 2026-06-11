Paso 3.5 — Validación estructural y optimización (sin implementar)

Guardia de paso



Verifica que:



El Paso 3 haya sido completado.

El usuario haya aprobado explícitamente el Paso 3.



Si no existe aprobación registrada, responde:



Completa y aprueba /paso3-tecnico primero.



y detente.



Objetivo



Validar que la solución técnica propuesta sea:



Coherente con la arquitectura existente.

Suficientemente simple para el problema.

Escalable cuando sea necesario.

Consistente con las convenciones actuales.

Optimizada para minimizar complejidad, deuda técnica y consumo innecesario de recursos.



Este paso NO diseña nuevamente la solución.



Su propósito es validar y optimizar el diseño técnico antes de implementar.



Instrucciones

NO implementar código.

NO modificar archivos.

NO redefinir requerimientos.

NO repetir análisis funcionales.

NO repetir análisis técnicos ya realizados en el Paso 3.

Reutilizar toda la información ya aprobada.

Analizar únicamente aspectos estructurales y de optimización.

Optimización obligatoria de contexto



Antes de ejecutar:



Revisar conclusiones aprobadas del Paso 1.

Revisar conclusiones aprobadas del Paso 2.

Revisar conclusiones aprobadas del Paso 3.



No volver a generar:



Casos de uso.

Beneficios de negocio.

Diseño funcional.

Diseño técnico completo.



Referenciar brevemente análisis previos cuando sea suficiente.



Objetivo: minimizar consumo de tokens evitando análisis duplicados.



Validación estructural

1\. Coherencia arquitectónica



Validar:



Compatibilidad con la arquitectura actual.

Cumplimiento de patrones existentes.

Consistencia con convenciones del proyecto.

Alineación con módulos ya implementados.



Identificar desviaciones relevantes.



2\. Reutilización



Evaluar:



Componentes reutilizables.

Servicios reutilizables.

APIs reutilizables.

Modelos reutilizables.

Procesos reutilizables.



Indicar explícitamente:



Qué puede reutilizarse.

Qué realmente requiere crearse.



Evitar duplicar funcionalidades existentes.



3\. Simplificación



Evaluar si existe una alternativa más simple.



Comparar:



Solución propuesta.

Solución más simple viable.



Indicar:



Beneficios.

Limitaciones.

Recomendación.



No rediseñar completamente la solución salvo que exista una mejora significativa.



4\. Escalabilidad



Evaluar:



Capacidad de crecimiento.

Mantenibilidad.

Facilidad de extensión futura.



Indicar posibles limitaciones conocidas.



5\. Impacto sobre datos y estructuras



Validar:



Compatibilidad con estructuras existentes.

Impacto sobre datos actuales.

Riesgos de migración.

Riesgos de integridad.



Solo a nivel conceptual.



No diseñar modelos detallados.



6\. Impacto transversal



Identificar:



Módulos afectados.

Dependencias ocultas.

Integraciones relacionadas.

Posibles efectos colaterales.



Registrar únicamente impactos relevantes.



7\. Riesgos estructurales



Para cada riesgo indicar:



Descripción.

Probabilidad:

Alta

Media

Baja

Impacto.

Mitigación propuesta.



Excluir riesgos menores o irrelevantes.



Optimización de implementación

1\. Complejidad



Evaluar si la solución está:



Subdimensionada

Adecuada

Sobredimensionada



Justificar brevemente.



2\. Consumo de recursos



Evaluar si la solución podría generar:



Consultas innecesarias.

Procesamiento redundante.

Duplicación de datos.

Dependencias innecesarias.



Indicar posibles optimizaciones.



3\. Mantenibilidad



Evaluar:



Facilidad de soporte.

Claridad de la solución.

Riesgo de deuda técnica futura.

4\. Consumo de contexto y desarrollo



Evaluar si la implementación propuesta:



Genera archivos innecesarios.

Duplica lógica existente.

Introduce complejidad evitable.

Incrementa innecesariamente el tamaño del proyecto.



Proponer simplificaciones cuando existan.



5\. Veredicto de optimización



Clasificar la solución como:



Óptima

Aceptable

Sobredimensionada



Si es Sobredimensionada:



Explicar por qué.

Proponer una alternativa más simple.

Recomendación final



Emitir uno de los siguientes resultados:



APROBADO



La solución puede avanzar a implementación sin cambios relevantes.



APROBADO CON AJUSTES



La implementación puede continuar, pero se recomiendan ajustes menores.



REQUIERE REDISEÑO



Existen problemas estructurales importantes que deben resolverse antes de implementar.



Cierre



Finalizar con:



Validación estructural completada. ¿Apruebas continuar al Paso 4 — Implementación?



No avanzar sin aprobación explícita.

