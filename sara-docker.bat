@echo off
echo ========================================
echo    SARA - Sistema de Asistencia IA
echo ========================================
echo.

if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="clean" goto clean
goto help

:start
echo Iniciando servicios de SARA...
docker-compose up -d backend
echo.
echo Servicios iniciados. El backend esta disponible en http://localhost:8000
echo Para iniciar la aplicacion Electron (solo Linux), usa: docker-compose --profile linux-gui up electron
goto end

:stop
echo Deteniendo servicios de SARA...
docker-compose down
goto end

:restart
echo Reiniciando servicios de SARA...
docker-compose restart
goto end

:logs
if "%2"=="" (
    echo Mostrando logs de todos los servicios...
    docker-compose logs -f
) else (
    echo Mostrando logs del servicio %2...
    docker-compose logs -f %2
)
goto end

:status
echo Estado de los servicios de SARA:
docker-compose ps
goto end

:clean
echo Limpiando contenedores e imagenes no utilizadas...
docker-compose down --volumes --remove-orphans
docker system prune -f
goto end

:help
echo Uso: %0 [comando]
echo.
echo Comandos disponibles:
echo   start    - Inicia el backend de SARA
echo   stop     - Detiene todos los servicios
echo   restart  - Reinicia todos los servicios
echo   logs     - Muestra logs (opcional: especificar servicio)
echo   status   - Muestra estado de los servicios
echo   clean    - Limpia contenedores e imagenes no utilizadas
echo.
echo Ejemplos:
echo   %0 start
echo   %0 logs backend
echo   %0 status
echo.
echo NOTA: La aplicacion Electron con GUI solo funciona en Linux.
echo En Windows/Mac, ejecuta la aplicacion Electron nativamente.
goto end

:end