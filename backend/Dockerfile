FROM python:3.11-slim

# SEC-007: gosu lets the entrypoint start as root (to reconcile volume
# permissions) and then drop privileges to a non-root user for the app process.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

# SEC-007: dedicated non-root user with a fixed UID/GID (stable across rebuilds).
RUN groupadd --gid 10001 gymuser \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin gymuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Directorio para la BD (volumen montado desde docker-compose).
# La propiedad real del volumen se reconcilia en cada arranque (R1, entrypoint).
RUN mkdir -p /app/data && chown -R gymuser:gymuser /app/data

# R1: entrypoint corre como root, ajusta permisos del volumen de forma
# idempotente y baja privilegios a gymuser antes de ejecutar la app/scheduler.
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
