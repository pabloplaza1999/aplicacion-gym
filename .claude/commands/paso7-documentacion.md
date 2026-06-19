# Paso 7 — Documentación

## Guardia de paso

Verifica que:

* El Paso 6 (Auditoría) haya sido completado.
* El usuario haya aprobado continuar.

Si no existe aprobación registrada, responde:

"Completa y aprueba el Paso 6 primero."

y detente.

---

## Objetivo

Consolidar y validar la documentación final afectada por la funcionalidad implementada.

Verificar que la documentación técnica actualizada durante el Paso 4 siga siendo correcta después de:

* Paso 5 (Pruebas)
* Paso 5.5 (Impacto histórico, si aplica)
* Paso 6 (Auditoría)

No implementar código.

No corregir errores.

No ejecutar pruebas nuevas.

No realizar auditorías adicionales.

---

## Optimización obligatoria

Antes de ejecutar:

* Reutilizar conclusiones ya aprobadas de:

  * Paso 1
  * Paso 2
  * Paso 3
  * Paso 5
  * Paso 5.5 (si aplica)
  * Paso 6

* Revisar cambios documentales realizados durante el Paso 4.

* Confirmar que siguen siendo válidos tras pruebas y auditoría.

* Actualizar únicamente aquello que haya cambiado entre la implementación y el resultado final validado.

No repetir análisis.

No regenerar documentación completa.

No duplicar documentación ya actualizada correctamente.

Localizar únicamente las secciones afectadas.

Actualizar solo los documentos realmente impactados.

Objetivo:

* minimizar consumo de tokens
* minimizar lecturas innecesarias
* evitar documentación duplicada

---

## Analizar

### 1. Documentación afectada

Identificar qué documentos requieren:

* creación
* actualización
* validación final
* o ninguna modificación adicional

Ejemplos:

* FEATURE_SUMMARY.md
* TECH_DEBT.md
* REQUERIMIENTOS.md
* ARQUITECTURA.md
* BASE_DATOS.md
* README.md
* MANUAL_TECNICO.md
* MANUAL_OPERADOR.md

Si un documento ya fue actualizado durante el Paso 4 y continúa siendo correcto tras pruebas y auditoría, indicar explícitamente:

"Sin cambios adicionales requeridos."

No modificar documentos sin cambios reales.

---

### 2. Resumen funcional

Documentar:

* Qué se implementó.
* Qué problema resuelve.
* Alcance final de la solución.
* Funcionalidades incluidas.
* Funcionalidades explícitamente fuera de alcance.

---

### 3. Impacto técnico

Documentar únicamente si hubo cambios.

Registrar:

* Componentes afectados.
* Servicios afectados.
* APIs nuevas o modificadas.
* Tablas nuevas o modificadas.
* Dependencias agregadas.
* Jobs scheduler agregados o modificados.
* Cambios Docker relevantes.

---

### 4. Riesgos pendientes

Revisar conclusiones del Paso 6.

Registrar únicamente:

* Riesgos abiertos.
* Limitaciones conocidas.
* Mejoras futuras.
* Deuda técnica aprobada.

Actualizar TECH_DEBT.md cuando corresponda.

No resolver riesgos.

---

### 5. Compatibilidad

Confirmar:

* Compatibilidad con funcionalidades existentes.
* Compatibilidad de datos.
* Compatibilidad de APIs.
* Compatibilidad operativa.

Documentar únicamente restricciones reales.

---

### 6. Impacto histórico (solo si aplica)

Ejecutar únicamente si el Paso 5.5 fue requerido.

Documentar:

* Datos afectados.
* Registros impactados.
* Migraciones ejecutadas.
* Correcciones históricas realizadas.
* Backups generados previamente.
* Validaciones posteriores a la corrección.

Si no hubo impacto histórico:

Omitir esta sección.

---

## Entregable

### Archivos actualizados

Listar:

* archivo
* archivo
* archivo

Para cada uno indicar:

* Estado:

  * Actualizado
  * Validado sin cambios
  * No requerido
* Breve descripción del resultado.

---

### Resumen final

Incluir:

* Funcionalidad implementada.
* Estado final.
* Riesgos pendientes.
* Deuda técnica registrada.
* Impacto histórico (si aplica).
* Próximos pasos sugeridos.

---

## Resultado

Clasificar:

### DOCUMENTACIÓN COMPLETADA

o

### DOCUMENTACIÓN COMPLETADA CON OBSERVACIONES

(si existen riesgos o deuda técnica relevante).

---

## Cierre

Finalizar con:

"Documentación actualizada y validada.

¿Deseas continuar al Paso 8 — Cierre y Publicación?"

Opciones:

1. Sí → ejecutar Paso 8.
2. No → finalizar el flujo actual.
