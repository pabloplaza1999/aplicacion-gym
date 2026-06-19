@echo off
cd /d "%~dp0"
echo.
echo [Rhinopower] Iniciando sistema...
echo.

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop no esta corriendo.
    echo.
    echo Pasos a seguir:
    echo   1. Busca "Docker Desktop" en el menu inicio y abralo.
    echo   2. Espera a que el icono de Docker en la barra de tareas deje de animarse.
    echo   3. Ejecuta este script nuevamente.
    echo.
    pause
    exit /b 1
)

docker compose up -d
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] No se pudo iniciar el sistema.
    echo Verifica que el archivo docker-compose.yml este en esta carpeta.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Sistema iniciado. Abriendo Rhinopower en el navegador...
timeout /t 3 /nobreak >nul
start http://localhost
echo.
echo Rhinopower disponible en: http://localhost
echo Para cerrar el sistema usa stop.bat
echo.
pause
