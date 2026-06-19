@echo off
cd /d "%~dp0"
echo.
echo [Rhinopower] Carga de imagenes para instalacion sin conexion a internet
echo =======================================================================
echo.

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop no esta corriendo.
    echo Abralo desde el menu inicio y espera a que inicie completamente.
    echo Luego ejecuta este script nuevamente.
    echo.
    pause
    exit /b 1
)

if not exist "images\rhinopower-backend.tar" (
    echo [ERROR] No se encontro: images\rhinopower-backend.tar
    echo.
    pause
    exit /b 1
)

if not exist "images\rhinopower-frontend.tar" (
    echo [ERROR] No se encontro: images\rhinopower-frontend.tar
    echo.
    pause
    exit /b 1
)

echo Cargando imagen del servidor (backend)...
docker load -i images\rhinopower-backend.tar
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al cargar imagen del backend.
    pause
    exit /b 1
)

echo.
echo Cargando imagen de la interfaz (frontend)...
docker load -i images\rhinopower-frontend.tar
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al cargar imagen del frontend.
    pause
    exit /b 1
)

echo.
echo [OK] Imagenes cargadas correctamente.
echo Ahora ejecuta start.bat para iniciar el sistema.
echo.
pause
