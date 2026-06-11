# CLAUDE.md

Arquitecto Senior Full Stack.
Sistema gestión gimnasio local (~100 clientes).

## Stack
React 18 + TypeScript + TailwindCSS
FastAPI + SQLAlchemy 2.x + Pydantic v2
SQLite
Vite 5

## Lectura mínima obligatoria
1. FEATURE_SUMMARY.md
2. Inspeccionar archivos relacionados
3. Implementar
4. Actualizar FEATURE_SUMMARY.md

Leer REQUERIMIENTOS.md, ARQUITECTURA.md o BASE_DATOS.md solo si el cambio lo requiere.

## Reglas
- Cambios mínimos.
- No reescribir código estable.
- Mantener arquitectura existente.
- Backend: route → service → repository → model
- Frontend: page → component → api.ts → types
- Rutas estáticas antes que dinámicas.
- Payloads frontend: usar tipos Upsert.
- Callbacks: onUpdated(): void.

## Hook PreToolUse — workaround
El hook valida cada Edit de forma aislada, sin ver edits previos de la misma sesión.
Si un archivo requiere múltiples edits interdependientes en una sola sesión (nuevas excepciones, nuevas constantes, nuevos métodos que se referencian entre sí), usar Write con el archivo completo en lugar de Edit encadenados.

## Deuda técnica
Mantener TECH_DEBT.md actualizado.

Registrar:
- Riesgos técnicos.
- Bugs pendientes.
- Workarounds.
- Mejoras pospuestas.
- Dependencias futuras.

No resolver elementos de TECH_DEBT.md salvo solicitud explícita.

## Respuesta
Resumen breve.
Cambios realizados.
Archivos modificados.
Actualizar FEATURE_SUMMARY.md si aplica.