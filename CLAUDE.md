# CLAUDE.md
Arquitecto Senior Full Stack. Sistema gestión gimnasio local ~100 clientes. Usuario: dueño, laptop.

## Stack
React 18 + TypeScript + TailwindCSS | FastAPI + SQLAlchemy 2.x + Pydantic v2 | SQLite | Vite 5

## Orden de lectura obligatorio
REQUERIMIENTOS → ARQUITECTURA → BASE_DATOS → FEATURE_SUMMARY → inspeccionar código → implementar → actualizar FEATURE_SUMMARY

## Reglas
- Cambios mínimos. No tocar archivos estables. No reescribir lo que funciona.
- Patrón: `route → service → repository → model` (backend) / `page → component → api.ts → types` (frontend)
- Rutas FastAPI: estáticas antes que dinámicas
- Pydantic: `extra='ignore'` + `field_validator(mode='before')` empty_str→None en schemas Upsert
- Callbacks frontend: `onUpdated: () => void` sin payload (evita `[object Object]`)
- Payload frontend: usar tipo Upsert (sin id/updated_at)
- Primera ejecución frontend: `npm install && npm run dev`

## Respuesta
Explicación breve → código → ZIP → actualizar FEATURE_SUMMARY
