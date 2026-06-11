# Paso 6 — Auditoría

## Guardia de paso

Verifica que el Paso 5 (Validación) haya sido completado y aprobado.

Si no existe aprobación explícita, responde:

"Completa y aprueba el Paso 5 primero."

y detente.

---

## Objetivo

Realizar una revisión técnica de la solución implementada.

No implementar cambios.

No modificar código.

No ejecutar nuevas pruebas.

No actualizar documentación todavía.

---

## Instrucciones

Analiza únicamente la funcionalidad implementada en esta solicitud y su impacto sobre el sistema.

Utiliza la información obtenida durante:

- Diseño técnico
- Implementación
- Validación

Evita reanalizar módulos no relacionados.

---

## 1. Complejidad de la solución

Evaluar:

- Baja
- Media
- Alta

Justificar brevemente:

- Número de capas afectadas
- Cambios estructurales realizados
- Dependencias involucradas

---

## 2. Calidad arquitectónica

Verificar:

- Respeto de la arquitectura definida
- Separación de responsabilidades
- Consistencia con patrones existentes
- Acoplamiento generado

Indicar:

- Correcto
- Aceptable
- Requiere revisión

---

## 3. Riesgos técnicos detectados

Identificar:

- Riesgos inmediatos
- Riesgos futuros
- Casos límite no cubiertos
- Dependencias sensibles

Para cada riesgo indicar:

- Descripción
- Impacto
- Prioridad (Alta / Media / Baja)

---

## 4. Impacto sobre funcionalidades existentes

Evaluar:

### Backend

- Servicios afectados
- Endpoints afectados
- Procesos afectados

### Frontend

- Pantallas afectadas
- Componentes afectados
- Navegación afectada

### Base de datos

- Tablas afectadas
- Migraciones aplicadas
- Compatibilidad de datos

Indicar si existe riesgo de regresión.

---

## 5. Deuda técnica generada

Identificar:

- Soluciones temporales
- Limitaciones conocidas
- Mejoras recomendadas
- Refactorizaciones futuras

Clasificar:

- Alta
- Media
- Baja

No resolverlas.

---

## 6. Seguridad y robustez

Evaluar si aplica:

- Validaciones de entrada
- Manejo de errores
- Integridad de datos
- Control de estados
- Casos de borde

Indicar hallazgos relevantes.

---

## 7. Rendimiento

Evaluar únicamente si hubo impacto potencial.

Revisar:

- Consultas nuevas
- Procesos repetitivos
- Cálculos complejos
- Operaciones costosas

Si no existe impacto relevante indicar:

"Sin impacto significativo."

---

## 8. Recomendaciones

Listar únicamente recomendaciones realmente necesarias.

Evitar mejoras cosméticas.

Priorizar:

1. Riesgos críticos
2. Riesgos medios
3. Mejoras futuras

---

## Resultado final

Presentar:

### Complejidad

- Baja / Media / Alta

### Riesgos detectados

- Riesgo 1
- Riesgo 2

### Deuda técnica

- TD-001
- TD-002

### Estado de auditoría

- Aprobada
- Aprobada con observaciones
- Requiere correcciones

### Próxima acción recomendada

- Continuar a Paso 7 — Documentación
- Corregir observaciones antes de continuar

---

Finalizar con:

> "Auditoría completada. ¿Apruebas continuar al Paso 7 — Documentación?"