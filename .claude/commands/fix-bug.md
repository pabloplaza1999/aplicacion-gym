Fix Bug

Objetivo



Corregir un defecto existente con el menor cambio posible y el menor riesgo de regresión posible.



La finalidad de este proceso es restaurar el comportamiento esperado sin rediseñar la solución ni introducir cambios funcionales no solicitados.



Alcance



Este proceso corrige únicamente:



defectos funcionales

errores lógicos

errores de integración

errores de validación

errores de persistencia

errores de cálculo

regresiones detectadas



No debe utilizarse para:



implementar funcionalidades nuevas

realizar mejoras evolutivas

optimizar arquitectura

refactorizar módulos completos

rediseñar soluciones aprobadas

Reglas

No implementar nuevas funcionalidades.

No modificar requerimientos aprobados.

No rediseñar la solución.

No repetir análisis funcionales.

No repetir análisis técnicos ya aprobados.

Mantener arquitectura y convenciones existentes.

Reutilizar todo el contexto ya generado.

Limitarse estrictamente al defecto reportado.



Aplicar siempre el principio:



Menor cambio posible que resuelva completamente el problema.



Optimización obligatoria de contexto



Antes de ejecutar:



Revisar únicamente:



defecto reportado

implementación realizada

resultados del Paso 5

resultados del Paso 5.5 (si existen)



No volver a generar:



análisis de valor

diseño funcional

diseño técnico

validación estructural



Objetivo:



minimizar consumo de tokens

reducir tiempo de resolución

evitar reanálisis innecesarios

Análisis



Identificar:



1\. Defecto



Describir claramente:



comportamiento esperado

comportamiento observado

2\. Causa raíz



Determinar:



origen real del problema

capa afectada

motivo técnico



Evitar hipótesis innecesarias.



Buscar la causa específica.



3\. Archivos afectados



Identificar:



archivos directamente involucrados

dependencias relevantes



No ampliar el alcance sin justificación.



4\. Riesgo de regresión



Evaluar:



módulos relacionados

funcionalidades impactadas

posibles efectos secundarios



Clasificar:



Alto

Medio

Bajo

5\. Impacto histórico



Determinar si el defecto pudo generar:



datos incorrectos

estados incorrectos

fechas incorrectas

cálculos incorrectos

registros inconsistentes



Si existe posible impacto histórico:



documentarlo

cuantificarlo cuando sea posible

indicar que deberá validarse completamente en el Paso 5.5



No ejecutar migraciones durante Fix Bug.



No corregir datos históricos durante esta fase.



Implementación



Aplicar únicamente el cambio mínimo necesario.



Evitar:



cambios cosméticos

refactorizaciones

optimizaciones no relacionadas

mejoras oportunistas



Cada modificación debe tener relación directa con la causa raíz identificada.



Validación



Validar únicamente:



Caso corregido



Confirmar que el defecto desapareció.



Casos relacionados



Confirmar que el comportamiento esperado sigue funcionando.



Regresiones potenciales



Validar únicamente módulos afectados.



Reutilizar pruebas ya ejecutadas cuando sea posible.



No repetir validaciones completas del proyecto.



TECH\_DEBT



Actualizar TECH\_DEBT.md únicamente si aparecen:



riesgos residuales

limitaciones conocidas

soluciones temporales

migraciones futuras recomendadas



No registrar deuda técnica irrelevante.



Resultado



Entregar:



Corrección realizada



Descripción breve.



Archivos modificados



Listado de archivos.



Validaciones ejecutadas



Resultados obtenidos.



Riesgos pendientes



Si existen.



Impacto histórico detectado



Si existe.



Estado final



Clasificar:



PASS



PASS CON RIESGOS



FAIL



Continuidad



Si el resultado es:



PASS



→ Repetir Paso 5 — Validación y pruebas



PASS CON RIESGOS



→ Actualizar TECH\_DEBT



→ Repetir Paso 5 — Validación y pruebas



FAIL



→ Nueva iteración de Fix Bug



No avanzar directamente a Paso 6.



El flujo normal debe continuar mediante:



Fix Bug

→ Paso 5

→ Paso 5.5 (si aplica)

→ Paso 6



Cierre



Finalizar con:



"Fix aplicado. Recomendado ejecutar nuevamente el Paso 5 — Validación y pruebas."



No avanzar automáticamente a pasos posteriores.

