# Paso 8 — Cierre y Publicación (Opcional)

## Guardia de paso

Verifica que:

- El Paso 7 haya sido completado.
- El usuario haya aprobado continuar.

Si no existe aprobación registrada:

"Completa y aprueba el Paso 7 primero."

y detente.

---

## Objetivo

Preparar el repositorio para publicación.

No implementar cambios.
No ejecutar pruebas.
No modificar documentación.
No realizar auditorías adicionales.

---

## Optimización obligatoria

Reutilizar toda la información obtenida en:

- Paso 5
- Paso 5.5 (si aplica)
- Paso 6
- Paso 7

No repetir análisis previos.

---

## Verificaciones

### 1. Estado Git

Verificar:

- branch actual
- archivos modificados
- archivos nuevos
- archivos eliminados
- staged
- unstaged
- untracked

---

### 2. Archivos excluibles

Detectar archivos que no deberían publicarse.

Ejemplos:

- logs
- backups
- bases de datos locales
- archivos temporales
- artefactos de build

Indicar únicamente hallazgos relevantes.

---

### 3. Commit recomendado

Generar:

- tipo
- scope
- mensaje

Ejemplos:

feat(notifications): add membership expiration reminders

fix(members): handle duplicate document conflicts

---

### 4. Publicación

Si existe repositorio Git:

Generar únicamente los comandos sugeridos:

git status
git add .
git commit -m "<mensaje>"
git push

No ejecutar comandos automáticamente.

No usar force push.

---

## Entregable

### Estado Git

### Archivos a publicar

### Archivos recomendados para excluir

### Commit recomendado

### Comandos Git sugeridos

---

## Cierre

Finalizar con:

"Repositorio preparado para publicación."

o

"Repositorio revisado. Publicación omitida por decisión del usuario."