# Paso 5 — Validación y pruebas

# Objetivo

# 

# Validar que la funcionalidad implementada:

# 

# Funciona correctamente.

# Cumple los requisitos aprobados.

# No genera regresiones.

# Está lista para evaluación de datos históricos (Paso 5.5).

# Alcance

# 

# Este paso valida exclusivamente:

# 

# Implementación realizada.

# Flujos funcionales afectados.

# Reglas de negocio implementadas.

# Integraciones afectadas.

# Regresiones funcionales.

# 

# No valida:

# 

# Datos históricos existentes.

# Migraciones correctivas.

# Calidad de datos acumulados.

# Impacto sobre registros previos.

# Consistencia histórica de información.

# 

# Estos aspectos corresponden al Paso 5.5.

# 

# Instrucciones

# 

# NO implementar nuevas funcionalidades.

# 

# NO corregir errores durante esta fase.

# 

# NO realizar refactorizaciones.

# 

# La responsabilidad de esta fase es únicamente validar y reportar.

# 

# Si se detecta un defecto:

# 

# Documentarlo.

# Clasificar severidad.

# Identificar impacto.

# Registrar o actualizar TECH\_DEBT.md si aplica.

# Recomendar ejecutar /fix-bug.

# Estrategia de validación

# 

# Validar en el siguiente orden:

# 

# 1\. Validación estática

# 

# Verificar:

# 

# Compilación.

# Imports.

# Tipado.

# Dependencias.

# Errores de construcción.

# 2\. Validación funcional

# 

# Ejecutar:

# 

# Escenarios positivos

# 

# Casos que deben funcionar correctamente.

# 

# Escenarios negativos

# 

# Casos inválidos que deben ser rechazados.

# 

# Casos límite

# 

# Condiciones extremas, excepcionales o poco frecuentes.

# 

# 3\. Validación de regresión

# 

# Validar:

# 

# Funcionalidades relacionadas.

# Flujos previamente existentes.

# Módulos potencialmente impactados.

# 4\. Validación manual

# 

# Ejecutar únicamente si aporta valor real.

# 

# No realizar validaciones manuales innecesarias.

# 

# Optimización obligatoria

# 

# Si durante el Paso 3 o Paso 4 ya se ejecutaron validaciones equivalentes:

# 

# Reutilizar resultados existentes.

# No repetir pruebas idénticas.

# Ejecutar únicamente validaciones nuevas o afectadas por cambios recientes.

# 

# Objetivo:

# 

# Reducir consumo de tokens.

# Reducir tiempo de ejecución.

# Evitar validaciones redundantes.

# Límite de esfuerzo

# 

# Si aparecen problemas de infraestructura o entorno:

# 

# encoding

# PowerShell

# Bash

# terminal

# puertos

# navegador

# Playwright

# drivers

# permisos

# stdout/stderr

# herramientas externas

# 

# Realizar máximo 3 intentos de resolución.

# 

# Si el problema persiste:

# 

# detener la automatización

# documentar el bloqueo

# clasificar la validación como parcial

# continuar con el informe final

# 

# No consumir tiempo ni tokens intentando resolver problemas de infraestructura que no pertenecen a la funcionalidad implementada.

# 

# Generar

# 1\. Escenarios positivos

# 

# Casos ejecutados correctamente.

# 

# 2\. Escenarios negativos

# 

# Casos rechazados correctamente.

# 

# 3\. Casos límite

# 

# Condiciones extremas validadas.

# 

# 4\. Impacto sobre funcionalidades existentes

# 

# Indicar:

# 

# módulos validados

# resultado de cada validación

# 5\. Riesgos detectados

# 

# Identificar:

# 

# riesgos técnicos

# limitaciones conocidas

# comportamientos inesperados

# 6\. Defectos encontrados

# 

# Para cada defecto indicar:

# 

# Descripción

# Severidad:

# Crítica

# Alta

# Media

# Baja

# Impacto

# Reproducibilidad

# Archivos potencialmente afectados

# Requiere /fix-bug:

# Sí

# No

# 7\. Resultado final

# 

# Clasificar:

# 

# PASS

# 

# No se encontraron defectos.

# 

# La funcionalidad cumple los requisitos aprobados.

# 

# PASS CON RIESGOS

# 

# Existen riesgos o limitaciones conocidas.

# 

# No impiden el uso de la funcionalidad.

# 

# FAIL

# 

# Existen defectos que requieren ejecutar /fix-bug.

# 

# No se recomienda avanzar.

# 

# Registro de deuda técnica

# 

# Si existen:

# 

# riesgos no corregidos

# limitaciones conocidas

# mejoras pospuestas

# soluciones temporales

# 

# registrarlos o actualizarlos en TECH\_DEBT.md.

# 

# Entrega

# 

# Presentar:

# 

# Casos ejecutados

# Resultado de cada caso

# Cobertura funcional validada

# Riesgos encontrados

# Defectos encontrados

# Pruebas pendientes (si aplica)

# Recomendación final

# Flujo de salida

# 

# Si el resultado es:

# 

# PASS

# 

# → Continuar a Paso 5.5 — Validación de datos e impacto histórico

# 

# PASS CON RIESGOS

# 

# → Registrar TECH\_DEBT si aplica

# 

# → Continuar a Paso 5.5 — Validación de datos e impacto histórico

# 

# FAIL

# 

# → Ejecutar /fix-bug

# 

# → Repetir Paso 5

