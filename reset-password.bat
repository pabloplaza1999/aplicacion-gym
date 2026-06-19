@echo off
cd /d "%~dp0"
echo.
echo [Rhinopower] Restablecimiento de contrasena del administrador
echo ============================================================
echo.
echo ATENCION: La contrasena sera restablecida a la contrasena
echo inicial configurada en el archivo .env
echo (variable ADMIN_INITIAL_PASSWORD).
echo.
echo El operador debera cambiarla en el proximo inicio de sesion.
echo.
echo Presiona cualquier tecla para continuar o cierra esta ventana para cancelar.
pause >nul

echo.
docker compose exec backend python scripts/reset_admin.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] No se pudo restablecer la contrasena.
    echo Verifica que el sistema este corriendo (usa start.bat primero).
    echo.
    pause
    exit /b 1
)

echo.
pause
