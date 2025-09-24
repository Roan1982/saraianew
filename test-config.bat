@echo off
echo ========================================
echo    SARA ASISTENTE VIRTUAL - PRUEBA
echo ========================================
echo.

echo Verificando archivos de configuracion...
echo.

if exist "docker-compose.yml" (
    echo ✓ docker-compose.yml encontrado
) else (
    echo ✗ docker-compose.yml no encontrado
    goto :error
)

if exist "Dockerfile.backend" (
    echo ✓ Dockerfile.backend encontrado
) else (
    echo ✗ Dockerfile.backend no encontrado
    goto :error
)

if exist "Dockerfile.electron" (
    echo ✓ Dockerfile.electron encontrado
) else (
    echo ✗ Dockerfile.electron no encontrado
    goto :error
)

if exist "requirements.txt" (
    echo ✓ requirements.txt encontrado
) else (
    echo ✗ requirements.txt no encontrado
    goto :error
)

if exist "check-status.bat" (
    echo ✓ check-status.bat encontrado
) else (
    echo ✗ check-status.bat no encontrado
    goto :error
)

if exist "run-docker.ps1" (
    echo ✓ run-docker.ps1 encontrado
) else (
    echo ✗ run-docker.ps1 no encontrado
    goto :error
)

echo.
echo Verificando sintaxis de archivos...
echo.

echo Verificando docker-compose.yml...
docker-compose config >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Sintaxis de docker-compose.yml correcta
) else (
    echo ✗ Error en sintaxis de docker-compose.yml
    goto :error
)

echo Verificando comandos de inicio...
findstr /C:"command:" docker-compose.yml >nul
if %errorlevel% equ 0 (
    echo ✓ Comandos de inicio configurados
) else (
    echo ✗ Comandos de inicio no encontrados
    goto :error
)

echo.
echo Verificando requirements.txt...
python -c "import pkg_resources; [pkg_resources.require(line.strip()) for line in open('requirements.txt') if line.strip()]" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Dependencias de Python verificadas
) else (
    echo ! Advertencia: No se pudieron verificar dependencias de Python (Python no disponible)
)

echo.
echo Verificando package.json...
if exist "asistente-virtual\node_modules" (
    echo ✓ Dependencias de Node.js instaladas
) else (
    echo ! Advertencia: Dependencias de Node.js no instaladas
)

echo.
echo ========================================
echo    CONFIGURACION VALIDADA
echo ========================================
echo.
echo La configuracion Docker esta correcta.
echo Para ejecutar la aplicacion completa:
echo.
echo 1. Asegurate de tener Docker Desktop ejecutandose
echo 2. Ejecuta: run-docker.bat (o .\run-docker.ps1 en PowerShell)
echo 3. Verifica el estado: check-status.bat (o .\check-status.ps1)
echo.
echo Servicios disponibles:
echo - Backend Django: http://localhost:8000
echo - Aplicacion Electron: Ventana flotante
echo.

pause
goto :end

:error
echo.
echo ========================================
echo         ERROR DE CONFIGURACION
echo ========================================
echo.
echo Corrige los errores mostrados arriba.
echo.
pause
goto :end

:end