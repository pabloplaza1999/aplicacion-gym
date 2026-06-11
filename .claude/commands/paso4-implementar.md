# Paso 4 — Implementación

## Guardia de paso

Verifica que el usuario haya aprobado explícitamente el Paso 3.

Si no existe aprobación registrada, responde:

"Completa y aprueba /paso3-tecnico primero."

y detente.

## Requisitos de implementación

* Reutilizar arquitectura existente.
* Aplicar cambios mínimos.
* Evitar duplicación de lógica.
* Mantener consistencia con los patrones actuales del proyecto.
* No modificar código estable sin necesidad.
* Mantener compatibilidad con funcionalidades existentes.
* Actualizar únicamente la documentación impactada.

## Antes de escribir código

Explica brevemente:

* Estrategia de implementación.
* Componentes que serán modificados.
* Riesgos identificados.
* Cómo se minimizarán regresiones.

Máximo 5 líneas.

## Orden de implementación

Implementar siguiendo la arquitectura existente del proyecto.

Prioridad:

1. Modelos y estructuras de datos.
2. Reglas de negocio.
3. Servicios y APIs.
4. Interfaz de usuario.
5. Documentación.

Si alguna capa no aplica, indicarlo y continuar.

## Durante la implementación

Para cada archivo modificado indicar:

* Ruta.
* Motivo del cambio.
* Impacto esperado.

Mantener la explicación breve.

## Validación obligatoria

Al finalizar:

* Verificar compilación.
* Verificar errores de ejecución.
* Verificar que no existan regresiones evidentes.
* Confirmar que el requerimiento quedó cubierto.

## Actualización documental

Actualizar únicamente los documentos afectados:

* FEATURE\_SUMMARY.md
* TECH\_DEBT.md (si aparecen riesgos o deuda técnica)
* REQUERIMIENTOS.md
* ARQUITECTURA.md

Solo cuando corresponda.

## Cierre

Presentar:

### Archivos modificados

Lista de archivos modificados.

### Archivos nuevos

Lista de archivos creados.

### Validaciones realizadas

Resumen de pruebas ejecutadas.

### Riesgos pendientes

Solo si existen.

### Próximo paso

Invitar a ejecutar:

/paso5-pruebas

