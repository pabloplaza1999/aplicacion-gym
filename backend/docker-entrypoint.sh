#!/bin/sh
# R1 — Reconciliación automática e idempotente de permisos del volumen.
#
# El volumen db-data puede contener archivos creados por root en instalaciones
# previas (gym.db, backups). Antes de ejecutar la app como usuario no-root,
# este entrypoint —que arranca como root— ajusta la propiedad de /app/data y
# luego baja privilegios a gymuser. Cubre por igual al backend y al scheduler
# (comparten imagen). Es idempotente: en instalaciones nuevas no hay nada que
# cambiar y la operación es inocua.
set -e

DATA_DIR="/app/data"

mkdir -p "$DATA_DIR"
# chown recursivo idempotente: garantiza escritura sobre gym.db, su directorio
# (-wal/-shm/journal) y las carpetas de backups (automatic/manual).
chown -R gymuser:gymuser "$DATA_DIR"

# Drop de privilegios: el proceso de la aplicación corre como gymuser, no root.
exec gosu gymuser "$@"
