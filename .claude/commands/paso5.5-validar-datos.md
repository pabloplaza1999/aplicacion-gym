# Paso 5.5 — Validación de datos e impacto histórico

# 

# Guardia de paso

# 

# Verifica que:

# 

# \- El Paso 5 haya sido completado.

# \- El resultado del Paso 5 sea:

# &#x20; - PASS

# &#x20; - PASS CON RIESGOS

# 

# Si el Paso 5 terminó en FAIL, responde:

# 

# "Completa exitosamente /paso5-pruebas primero."

# 

# y detente.

# 

# Objetivo

# 

# Validar que la implementación:

# 

# \- No genere inconsistencias sobre datos existentes.

# \- No deje registros históricos en estado incorrecto.

# \- No requiera migraciones correctivas no identificadas.

# \- No introduzca diferencias entre datos antiguos y nuevos.

# 

# Este paso NO valida la implementación.

# 

# La implementación ya fue validada en el Paso 5.

# 

# Este paso valida exclusivamente datos persistidos e impacto histórico.

# 

# Cuándo ejecutar este paso

# 

# Ejecutar únicamente si la funcionalidad afecta alguno de los siguientes elementos:

# 

# Datos persistidos

# 

# \- Tablas

# \- Registros

# \- Columnas

# \- Relaciones

# \- Datos calculados almacenados

# 

# Reglas de negocio históricas

# 

# \- Estados

# \- Fechas

# \- Vencimientos

# \- Alertas

# \- Acumulados

# \- Métricas

# \- Cálculos persistidos

# 

# Procesos automáticos

# 

# \- Scheduler

# \- Jobs

# \- Procesos batch

# \- Backfills

# \- Recalculos automáticos

# 

# Migraciones

# 

# \- CREATE

# \- ALTER

# \- UPDATE masivos

# \- Scripts correctivos

# \- Conversión de datos

# 

# Omitir este paso si

# 

# La funcionalidad únicamente afecta:

# 

# \- UI

# \- estilos

# \- colores

# \- layouts

# \- componentes visuales

# \- navegación

# \- textos

# \- mejoras cosméticas

# \- formularios sin persistencia

# 

# En ese caso responder:

# 

# "Paso 5.5 no requerido. No existe impacto sobre datos históricos. Continuar a Paso 6."

# 

# y finalizar.

# 

# Instrucciones

# 

# NO implementar código.

# 

# NO modificar archivos.

# 

# NO ejecutar migraciones.

# 

# NO corregir datos.

# 

# NO proponer rediseños.

# 

# La responsabilidad de esta fase es:

# 

# \- validar

# \- cuantificar impacto

# \- detectar inconsistencias

# \- recomendar acciones

# 

# Optimización obligatoria

# 

# Reutilizar toda la información obtenida durante:

# 

# \- Paso 3

# \- Paso 4

# \- Paso 5

# 

# No repetir consultas o verificaciones ya realizadas.

# 

# Analizar únicamente:

# 

# \- datos afectados

# \- registros impactados

# \- inconsistencias detectadas

# 

# Objetivo:

# 

# \- minimizar consumo de tokens

# \- evitar análisis redundantes

# \- enfocarse únicamente en impacto histórico

# 

# Validaciones

# 

# 1\. Compatibilidad con datos existentes

# 

# Validar:

# 

# \- registros actuales

# \- compatibilidad con la nueva lógica

# \- compatibilidad con reglas históricas

# 

# Identificar:

# 

# \- registros incompatibles

# \- valores obsoletos

# \- estados inválidos

# 

# 2\. Impacto sobre datos históricos

# 

# Verificar:

# 

# \- información generada antes del cambio

# \- registros históricos

# \- estados derivados

# \- cálculos persistidos

# 

# Determinar:

# 

# \- si los datos históricos siguen siendo válidos

# \- si existen diferencias entre comportamiento antiguo y nuevo

# 

# 3\. Impacto operativo

# 

# Determinar si existen:

# 

# \- estados incorrectos

# \- alertas incorrectas

# \- vencimientos incorrectos

# \- cálculos incorrectos

# \- reportes incorrectos

# \- indicadores incorrectos

# 

# Cuantificar el impacto cuando sea posible.

# 

# 4\. Necesidad de migración

# 

# Clasificar:

# 

# No requerida

# 

# Los datos existentes siguen siendo válidos.

# 

# Opcional

# 

# Existen inconsistencias menores o cosméticas.

# 

# Requerida

# 

# Existen datos funcionalmente incorrectos.

# 

# Indicar:

# 

# \- cantidad de registros afectados

# \- severidad

# \- prioridad recomendada

# 

# 5\. Riesgos detectados

# 

# Para cada riesgo indicar:

# 

# \- Descripción

# \- Alcance

# \- Registros afectados

# \- Probabilidad

# &#x20; - Alta

# &#x20; - Media

# &#x20; - Baja

# \- Impacto

# &#x20; - Alto

# &#x20; - Medio

# &#x20; - Bajo

# \- Mitigación propuesta

# 

# Excluir riesgos irrelevantes.

# 

# Generar

# 

# 1\. Datos analizados

# 

# Indicar:

# 

# \- tablas revisadas

# \- registros revisados

# \- alcance de la validación

# 

# 2\. Hallazgos

# 

# Indicar:

# 

# \- inconsistencias encontradas

# \- diferencias detectadas

# \- registros afectados

# 

# 3\. Impacto operativo

# 

# Explicar:

# 

# \- efecto sobre usuarios

# \- efecto sobre procesos

# \- efecto sobre reportes

# \- efecto sobre automatizaciones

# 

# 4\. Migración requerida

# 

# Clasificar:

# 

# \- No requerida

# \- Opcional

# \- Requerida

# 

# Justificar brevemente.

# 

# 5\. Riesgos detectados

# 

# Listar riesgos relevantes.

# 

# 6\. Recomendación final

# 

# Indicar la acción recomendada.

# 

# Resultado final

# 

# Clasificar:

# 

# PASS

# 

# \- No existen inconsistencias.

# \- No se requieren acciones adicionales.

# 

# PASS CON RIESGOS

# 

# \- Existen registros afectados.

# \- No impiden el funcionamiento actual.

# \- Puede requerirse:

# &#x20; - migración opcional

# &#x20; - limpieza futura

# &#x20; - registro en TECH\_DEBT

# 

# FAIL

# 

# \- Existen datos funcionalmente incorrectos.

# \- Se requiere:

# &#x20; - /fix-bug

# &#x20; - migración correctiva

# &#x20; - nueva validación

# 

# Registro de deuda técnica

# 

# Si existen:

# 

# \- inconsistencias aceptadas temporalmente

# \- migraciones pospuestas

# \- riesgos conocidos

# \- limitaciones operativas

# 

# registrarlos o actualizarlos en TECH\_DEBT.md.

# 

# Entrega

# 

# Presentar:

# 

# \- Datos analizados

# \- Hallazgos encontrados

# \- Impacto operativo

# \- Migración requerida

# \- Riesgos detectados

# \- Recomendación final

# 

# Flujo de salida

# 

# Si el resultado es:

# 

# PASS

# 

# → Continuar a Paso 6

# 

# PASS CON RIESGOS

# 

# → Registrar TECH\_DEBT si aplica

# 

# → Continuar a Paso 6

# 

# FAIL

# 

# → Ejecutar /fix-bug

# 

# → Repetir:

# 

# 1\. Paso 5

# 2\. Paso 5.5

# 

# Cierre

# 

# Finalizar con:

# 

# "Validación de datos e impacto histórico completada. ¿Apruebas continuar al Paso 6 — Auditoría?"

# 

# No avanzar sin aprobación explícita.

