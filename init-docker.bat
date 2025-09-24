@echo off
REM Script de inicialización para SARA en Docker (Windows)
REM Uso: init-docker.bat [comando]

setlocal enabledelayedexpansion

REM Colores para output (aproximados en Windows)
set "RED=[ERROR]"
set "GREEN=[SUCCESS]"
set "YELLOW=[WARNING]"
set "BLUE=[INFO]"

REM Función para imprimir mensajes coloreados
:print_info
echo %BLUE% %~1
goto :eof

:print_success
echo %GREEN% %~1
goto :eof

:print_warning
echo %YELLOW% %~1
goto :eof

:print_error
echo %RED% %~1
goto :eof

REM Función para verificar si Docker está corriendo
:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker no está corriendo. Por favor inicia Docker Desktop."
    exit /b 1
)
goto :eof

REM Función para construir las imágenes
:build_images
call :print_info "Construyendo imágenes Docker..."
docker-compose build --no-cache
if errorlevel 1 (
    call :print_error "Error al construir imágenes"
    exit /b 1
)
call :print_success "Imágenes construidas exitosamente"
goto :eof

REM Función para iniciar los servicios
:start_services
call :print_info "Iniciando servicios..."
docker-compose up -d
if errorlevel 1 (
    call :print_error "Error al iniciar servicios"
    exit /b 1
)
call :print_success "Servicios iniciados"
timeout /t 5 /nobreak >nul
call :show_status
goto :eof

REM Función para detener los servicios
:stop_services
call :print_info "Deteniendo servicios..."
docker-compose down
if errorlevel 1 (
    call :print_error "Error al detener servicios"
    exit /b 1
)
call :print_success "Servicios detenidos"
goto :eof

REM Función para ver logs
:show_logs
call :print_info "Mostrando logs de servicios..."
docker-compose logs -f
goto :eof

REM Función para ejecutar comandos en el backend
:exec_backend
docker-compose exec backend %*
goto :eof

REM Función para crear superusuario
:create_superuser
call :print_info "Creando superusuario..."
docker-compose exec backend python manage.py createsuperuser --noinput --username admin --email admin@sara.com
if errorlevel 1 (
    call :print_error "Error al crear superusuario"
    exit /b 1
)
call :print_success "Superusuario creado (usuario: admin, email: admin@sara.com)"
call :print_warning "Recuerda cambiar la contraseña después del primer login"
goto :eof

REM Función para poblar la base de datos con datos de ejemplo
:populate_db
call :print_info "Poblando la base de datos con datos de ejemplo..."
docker-compose exec backend python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
from core.models import Registro, Estadistica, IAAnalisis, ActividadUsuario

User = get_user_model()

# Crear usuarios de ejemplo si no existen
usuarios_data = [
    {'username': 'admin', 'email': 'admin@sara.com', 'rol': 'admin'},
    {'username': 'supervisor1', 'email': 'supervisor1@sara.com', 'rol': 'supervisor'},
    {'username': 'empleado1', 'email': 'empleado1@sara.com', 'rol': 'empleado'},
    {'username': 'empleado2', 'email': 'empleado2@sara.com', 'rol': 'empleado'},
]

for user_data in usuarios_data:
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults={
            'email': user_data['email'],
            'rol': user_data['rol'],
            'is_active': True
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f'Usuario {user.username} creado')
    else:
        print(f'Usuario {user.username} ya existe')

print('Base de datos poblada con datos de ejemplo')
"
if errorlevel 1 (
    call :print_error "Error al poblar la base de datos"
    exit /b 1
)
call :print_success "Base de datos poblada"
goto :eof

REM Función para mostrar el estado de los servicios
:show_status
call :print_info "Estado de los servicios:"
docker-compose ps
echo.
call :print_info "URLs de acceso:"
echo   - Aplicación Web: http://localhost
echo   - API Backend: http://localhost:8000
echo   - Admin Django: http://localhost:8000/admin/
echo   - Asistente IA: http://localhost/asistente/
goto :eof

REM Función para limpiar todo
:clean_all
call :print_warning "Esto eliminará todos los contenedores, imágenes y volúmenes"
set /p choice="¿Estás seguro? (y/N): "
if /i not "!choice!"=="y" (
    call :print_info "Operación cancelada"
    goto :eof
)
call :print_info "Limpiando todo..."
docker-compose down -v --rmi all
docker system prune -f
call :print_success "Limpieza completada"
goto :eof

REM Función principal
:main
if "%1"=="" goto help
if "%1"=="build" goto build
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" (
    call :stop_services
    timeout /t 2 /nobreak >nul
    goto start
)
if "%1"=="logs" goto show_logs
if "%1"=="shell" (
    call :exec_backend bash
    goto :eof
)
if "%1"=="manage" (
    shift
    call :exec_backend python manage.py %1 %2 %3 %4 %5 %6 %7 %8 %9
    goto :eof
)
if "%1"=="superuser" goto create_superuser
if "%1"=="populate" goto populate_db
if "%1"=="status" goto show_status
if "%1"=="clean" goto clean_all
if "%1"=="full-setup" goto full_setup
goto help

:full_setup
call :check_docker
call :print_info "Configuración completa de SARA..."
call :build_images
call :start_services
call :print_info "Esperando a que los servicios estén listos..."
timeout /t 10 /nobreak >nul
call :create_superuser
call :populate_db
call :show_status
call :print_success "¡Configuración completa! SARA está listo para usar."
goto :eof

:build
call :check_docker
call :build_images
goto :eof

:start
call :check_docker
call :start_services
goto :eof

:stop
call :stop_services
goto :eof

:help
echo Script de gestión Docker para SARA ^(Windows^)
echo.
echo Uso: %0 [comando]
echo.
echo Comandos disponibles:
echo   build       Construir imágenes Docker
echo   start       Iniciar servicios
echo   stop        Detener servicios
echo   restart     Reiniciar servicios
echo   logs        Ver logs de servicios
echo   shell       Abrir shell en el contenedor backend
echo   manage      Ejecutar comando de Django ^(ej: migrate, shell^)
echo   superuser   Crear superusuario
echo   populate    Poblar DB con datos de ejemplo
echo   status      Mostrar estado y URLs
echo   clean       Limpiar contenedores e imágenes
echo   full-setup  Configuración completa desde cero
echo   help        Mostrar esta ayuda
echo.
echo Ejemplos:
echo   %0 full-setup          # Primera vez
echo   %0 start               # Iniciar servicios
echo   %0 manage migrate      # Ejecutar migraciones
echo   %0 manage shell        # Abrir shell de Django
goto :eof

REM Ejecutar función principal
call :main %*