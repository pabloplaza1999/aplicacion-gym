@echo off
cd /d "%~dp0"
echo.
echo [Rhinopower] Deteniendo sistema...
echo.

docker compose down
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] No se pudo detener el sistema correctamente.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Sistema detenido. Los datos estan guardados.
echo.
pause
