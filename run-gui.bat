@echo off
REM Script para configurar X11 en Windows y ejecutar SARA con interfaz gráfica
REM Requiere: VcXsrv instalado (https://sourceforge.net/projects/vcxsrv/)

echo =========================================
echo     SARA ASISTENTE VIRTUAL - GUI MODE
echo =========================================
echo.

echo Verificando servidor X11...
tasklist /FI "IMAGENAME eq vcxsrv.exe" 2>NUL | find /I /N "vcxsrv.exe">NUL
if %ERRORLEVEL% EQU 0 (
    echo ✓ VcXsrv está ejecutándose
) else (
    echo ⚠ VcXsrv no está ejecutándose
    echo.
    echo Para habilitar la interfaz gráfica:
    echo 1. Descarga VcXsrv desde: https://sourceforge.net/projects/vcxsrv/
    echo 2. Instala VcXsrv
    echo 3. Ejecuta XLaunch con estas opciones:
    echo    - Multiple windows
    echo    - Display number: 0
    echo    - Start no client
    echo    - Disable access control
    echo.
    set /p continuar="¿Quieres continuar sin interfaz gráfica? (s/n): "
    if /i not "!continuar!"=="s" exit /b 1
)

echo.
echo Verificando Docker...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ✗ Docker no está instalado
    pause
    exit /b 1
)
echo ✓ Docker encontrado

docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ✗ Docker no está ejecutándose
    pause
    exit /b 1
)
echo ✓ Docker está ejecutándose

echo.
echo Iniciando SARA con interfaz gráfica...

docker-compose up --build -d

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Servicios iniciados exitosamente!
    echo.
    echo 🎯 ACCESO AL ASISTENTE:
    echo 1. El asistente debería aparecer como una ventana flotante
    echo 2. Si no aparece, verifica que VcXsrv esté ejecutándose
    echo 3. La ventana del asistente tiene:
    echo    - Login (usuario/contraseña)
    echo    - Panel de consejos
    echo    - Chat rápido
    echo    - Estado de monitoreo
    echo.
    echo 📊 SERVICIOS DISPONIBLES:
    echo - Backend Django: http://localhost:8000
    echo - Base de datos: SQLite (persistente)
    echo.
    echo 🔧 COMANDOS ÚTILES:
    echo - Ver estado: docker-compose ps
    echo - Ver logs backend: docker-compose logs -f backend
    echo - Ver logs asistente: docker-compose logs -f electron
    echo - Detener todo: docker-compose down
    echo.
) else (
    echo ✗ Error al iniciar servicios
)

echo Presiona cualquier tecla para continuar...
pause >nul