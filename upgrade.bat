@echo off
cd /d "%~dp0"
echo.
echo [Rhinopower] Actualizacion del sistema
echo ========================================
echo.

REM 1. Verificar Docker Desktop
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

REM 2. Detener el stack actual (seguro aunque no este corriendo)
docker compose down >nul 2>&1

REM 3. Si rhinopower_db-data ya existe: no se necesita migracion (idempotente)
docker volume inspect rhinopower_db-data >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Los datos ya estan en rhinopower_db-data.
    echo      No se requiere migracion.
    goto :start_stack
)

REM 4. Buscar volumen de instalacion anterior
docker volume inspect aplicacion-gym_db-data >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] No se encontro instalacion anterior.
    echo        Primera instalacion detectada.
    goto :start_stack
)

REM 5. Migrar datos (ESTRICTAMENTE ADITIVO — aplicacion-gym_db-data NO se modifica ni elimina)
echo [INFO] Instalacion anterior detectada: aplicacion-gym_db-data
echo [INFO] Migrando datos al nuevo volumen rhinopower_db-data...
echo [INFO] Los datos originales NO seran modificados ni eliminados.
echo.

docker volume create rhinopower_db-data >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo crear el volumen de destino.
    echo         Los datos originales en aplicacion-gym_db-data permanecen intactos.
    echo.
    echo Para soporte: pabloplaza1999@gmail.com
    echo.
    pause
    exit /b 1
)

docker run --rm ^
    -v aplicacion-gym_db-data:/src ^
    -v rhinopower_db-data:/dst ^
    alpine sh -c "cp -a /src/. /dst/"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] La copia de datos no pudo completarse.
    echo         Se cancela la actualizacion para proteger la informacion.
    echo         Los datos originales en aplicacion-gym_db-data permanecen intactos.
    echo.
    echo Para soporte: pabloplaza1999@gmail.com
    echo.
    pause
    exit /b 1
)

REM 6. Validar que gym.db existe en el volumen destino antes de iniciar contenedores
docker run --rm -v rhinopower_db-data:/data alpine test -f /data/gym.db
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Validacion fallida: la base de datos no se encontro en el destino.
    echo         Se cancela el inicio del sistema para proteger la informacion.
    echo         Los datos originales en aplicacion-gym_db-data permanecen intactos.
    echo.
    echo Para soporte: pabloplaza1999@gmail.com
    echo.
    pause
    exit /b 1
)

echo [OK] Migracion completada y validada correctamente.
echo [OK] Los datos originales en aplicacion-gym_db-data se conservan sin cambios.
echo.

:start_stack
echo Iniciando Rhinopower...
docker compose up -d
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] No se pudo iniciar el sistema.
    echo         Verifica que el archivo docker-compose.yml este en esta carpeta.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Rhinopower actualizado e iniciado correctamente.
echo.
timeout /t 3 /nobreak >nul
start http://localhost
echo Rhinopower disponible en: http://localhost
echo Para uso diario utiliza start.bat y stop.bat
echo.
pause
