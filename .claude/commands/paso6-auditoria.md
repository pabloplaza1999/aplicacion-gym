Paso 6 — Auditoría



Guardia de paso



Verifica que:



\* El Paso 5 haya sido completado.

\* El resultado del Paso 5 sea:



&#x20; \* PASS

&#x20; \* PASS CON RIESGOS

\* Si el Paso 5.5 fue requerido, también haya sido completado.



Si alguna condición no se cumple, responde:



"Completa exitosamente el flujo de validación antes de ejecutar la auditoría."



y detente.



\---



Objetivo



Realizar una revisión técnica final de la solución implementada.



No implementar cambios.



No modificar código.



No ejecutar nuevas pruebas.



No actualizar documentación todavía.



La finalidad de esta fase es consolidar los hallazgos obtenidos durante el desarrollo y validar la calidad técnica global de la solución.



\---



Instrucciones



Analiza únicamente la funcionalidad implementada en esta solicitud y su impacto sobre el sistema.



Utiliza la información obtenida durante:



\* Paso 3 — Diseño técnico

\* Paso 4 — Implementación

\* Paso 5 — Validación funcional

\* Paso 5.5 — Validación de datos e impacto histórico (si aplica)



Evita:



\* repetir validaciones

\* repetir pruebas

\* reanalizar módulos no relacionados

\* rediseñar la solución



Objetivo:



\* minimizar consumo de tokens

\* consolidar resultados previos

\* identificar riesgos y deuda técnica remanente



\---



1\. Complejidad de la solución



Evaluar:



\* Baja

\* Media

\* Alta



Justificar brevemente considerando:



\* número de capas afectadas

\* cambios estructurales realizados

\* dependencias involucradas

\* complejidad operativa introducida



\---



2\. Calidad arquitectónica



Verificar:



\* respeto de la arquitectura definida

\* separación de responsabilidades

\* consistencia con patrones existentes

\* reutilización de componentes

\* acoplamiento generado



Clasificar:



\* Correcto

\* Aceptable

\* Requiere revisión



Justificar brevemente.



\---



3\. Riesgos técnicos detectados



Identificar:



\* riesgos inmediatos

\* riesgos futuros

\* casos límite no cubiertos

\* dependencias sensibles

\* riesgos derivados de datos históricos

\* migraciones pendientes

\* inconsistencias aceptadas temporalmente



Para cada riesgo indicar:



\* Descripción

\* Impacto

\* Prioridad:



&#x20; \* Alta

&#x20; \* Media

&#x20; \* Baja



Excluir riesgos irrelevantes o puramente teóricos.



\---



4\. Impacto sobre funcionalidades existentes



Evaluar:



Backend



\* Servicios afectados

\* Endpoints afectados

\* Procesos afectados



Frontend



\* Pantallas afectadas

\* Componentes afectados

\* Navegación afectada



Base de datos



\* Tablas afectadas

\* Migraciones aplicadas

\* Compatibilidad de datos



Indicar si existe riesgo de regresión residual.



\---



5\. Deuda técnica generada



Identificar:



\* soluciones temporales

\* limitaciones conocidas

\* mejoras recomendadas

\* refactorizaciones futuras

\* deuda técnica detectada durante implementación

\* deuda técnica detectada durante validación

\* deuda técnica detectada durante validación histórica (Paso 5.5)



Clasificar cada elemento:



\* Alta

\* Media

\* Baja



No resolverlas.



No proponer implementación.



Solo registrarlas.



\---



6\. Seguridad y robustez



Evaluar únicamente si aplica:



\* validaciones de entrada

\* manejo de errores

\* integridad de datos

\* control de estados

\* casos de borde

\* control de concurrencia

\* protección ante datos inconsistentes



Indicar únicamente hallazgos relevantes.



\---



7\. Rendimiento



Evaluar únicamente si hubo impacto potencial.



Revisar:



\* consultas nuevas

\* procesos repetitivos

\* cálculos complejos

\* operaciones costosas

\* jobs automáticos

\* procesos batch



Si no existe impacto relevante indicar:



"Sin impacto significativo."



\---



8\. Recomendaciones



Listar únicamente recomendaciones realmente necesarias.



Evitar:



\* mejoras cosméticas

\* optimizaciones prematuras

\* refactorizaciones innecesarias



Priorizar:



\* riesgos críticos

\* riesgos medios

\* mejoras futuras justificadas



\---



Resultado final



Presentar:



Complejidad



\* Baja

\* Media

\* Alta



Riesgos detectados



\* Riesgo 1

\* Riesgo 2

\* ...



Deuda técnica



\* TD-001

\* TD-002

\* ...



Estado de auditoría



Clasificar:



\### Aprobada



La implementación es correcta y no existen observaciones relevantes.



\### Aprobada con observaciones



Existen riesgos, deuda técnica o hallazgos históricos aceptados temporalmente.



No impiden el uso de la funcionalidad.



\### Requiere correcciones



Existen problemas suficientemente relevantes como para recomendar corrección antes de documentar o cerrar.



Si el Paso 5.5 identificó:



\* migraciones pendientes

\* inconsistencias históricas

\* registros afectados

\* correcciones diferidas



clasificar al menos como:



"Aprobada con observaciones"



aunque la implementación sea técnicamente correcta.



\---



Próxima acción recomendada



Seleccionar una:



\* Continuar a Paso 7 — Documentación

\* Corregir observaciones antes de continuar



\---



Cierre



Finalizar con:



"Auditoría completada. ¿Apruebas continuar al Paso 7 — Documentación?"



No avanzar sin aprobación explícita.



