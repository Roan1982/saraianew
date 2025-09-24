@echo off
echo ========================================
echo    SARA ASISTENTE VIRTUAL - DOCKER
echo ========================================
echo.

echo Construyendo y ejecutando servicios...
docker-compose up --build -d

echo.
echo Servicios iniciados:
echo - Backend Django: http://localhost:8000
echo - Interfaz Web del Asistente: http://localhost:8000/asistente/
echo.

echo INSTRUCCIONES:
echo 1. Abre http://localhost:8000/asistente/
echo 2. Haz login con tu usuario y contrasena
echo 3. ¡El monitoreo se inicia automaticamente!
echo 4. Recibe consejos inteligentes cada 2 minutos
echo 5. Chatea con SARA IA
echo.

echo Para verificar estado:
echo docker-compose ps
echo.

echo Para ver logs del backend:
echo docker-compose logs -f backend
echo.

echo Para detener servicios:
echo docker-compose down
echo.

echo Presiona cualquier tecla para continuar...
pause >nul