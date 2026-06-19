@echo off
cd /d "%~dp0"
echo.
echo [Rhinopower] Creando respaldo manual de la base de datos...
echo.

docker compose exec backend python scripts/create_backup.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] No se pudo crear el respaldo.
    echo Verifica que el sistema este corriendo (usa start.bat primero).
    echo.
    pause
    exit /b 1
)

echo.
pause
