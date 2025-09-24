@echo off
echo ========================================
echo    VERIFICACION SARA DOCKER
echo ========================================
echo.

echo Verificando estado de contenedores...
docker-compose ps

echo.
echo ========================================
echo.

echo Verificando conectividad del backend...
curl -s http://localhost:8000/api/health/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backend responde correctamente
    curl -s http://localhost:8000/api/health/
) else (
    echo ✗ Backend no responde
)

echo.
echo ========================================
echo.

echo Verificando logs recientes del backend...
echo.
docker-compose logs --tail=10 backend

echo.
echo ========================================
echo.

echo Verificando logs recientes de Electron...
echo.
docker-compose logs --tail=10 electron

echo.
echo ========================================
echo.

echo Para ver logs en tiempo real:
echo - Backend: docker-compose logs -f backend
echo - Electron: docker-compose logs -f electron
echo.

echo Para detener servicios:
echo docker-compose down
echo.

pause