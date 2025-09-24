#!/bin/bash

# Script de inicialización para SARA en Docker
# Uso: ./init-docker.sh [comando]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes coloreados
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para verificar si Docker está corriendo
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker no está corriendo. Por favor inicia Docker Desktop."
        exit 1
    fi
}

# Función para construir las imágenes
build_images() {
    print_info "Construyendo imágenes Docker..."
    docker-compose build --no-cache
    print_success "Imágenes construidas exitosamente"
}

# Función para iniciar los servicios
start_services() {
    print_info "Iniciando servicios..."
    docker-compose up -d
    print_success "Servicios iniciados"
}

# Función para detener los servicios
stop_services() {
    print_info "Deteniendo servicios..."
    docker-compose down
    print_success "Servicios detenidos"
}

# Función para ver logs
show_logs() {
    print_info "Mostrando logs de servicios..."
    docker-compose logs -f
}

# Función para ejecutar comandos en el backend
exec_backend() {
    docker-compose exec backend "$@"
}

# Función para crear superusuario
create_superuser() {
    print_info "Creando superusuario..."
    docker-compose exec backend python manage.py createsuperuser --noinput --username admin --email admin@sara.com
    print_success "Superusuario creado (usuario: admin, email: admin@sara.com)"
    print_warning "Recuerda cambiar la contraseña después del primer login"
}

# Función para poblar la base de datos con datos de ejemplo
populate_db() {
    print_info "Poblando la base de datos con datos de ejemplo..."
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
    print_success "Base de datos poblada"
}

# Función para mostrar el estado de los servicios
show_status() {
    print_info "Estado de los servicios:"
    docker-compose ps
    echo ""
    print_info "URLs de acceso:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Admin Django: http://localhost:8000/admin/"
    echo "  - Aplicación web: http://localhost:8000"
    echo "  - Nginx (producción): http://localhost"
}

# Función para limpiar todo
clean_all() {
    print_warning "Esto eliminará todos los contenedores, imágenes y volúmenes"
    read -p "¿Estás seguro? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Limpiando todo..."
        docker-compose down -v --rmi all
        docker system prune -f
        print_success "Limpieza completada"
    fi
}

# Función principal
main() {
    case "${1:-help}" in
        "build")
            check_docker
            build_images
            ;;
        "start")
            check_docker
            start_services
            sleep 5
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_services
            ;;
        "logs")
            show_logs
            ;;
        "shell")
            exec_backend bash
            ;;
        "manage")
            shift
            exec_backend python manage.py "$@"
            ;;
        "superuser")
            create_superuser
            ;;
        "populate")
            populate_db
            ;;
        "status")
            show_status
            ;;
        "clean")
            clean_all
            ;;
        "full-setup")
            check_docker
            print_info "Configuración completa de SARA..."
            build_images
            start_services
            print_info "Esperando a que los servicios estén listos..."
            sleep 10
            create_superuser
            populate_db
            show_status
            print_success "¡Configuración completa! SARA está listo para usar."
            ;;
        "help"|*)
            echo "Script de gestión Docker para SARA"
            echo ""
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos disponibles:"
            echo "  build       Construir imágenes Docker"
            echo "  start       Iniciar servicios"
            echo "  stop        Detener servicios"
            echo "  restart     Reiniciar servicios"
            echo "  logs        Ver logs de servicios"
            echo "  shell       Abrir shell en el contenedor backend"
            echo "  manage      Ejecutar comando de Django (ej: migrate, shell)"
            echo "  superuser   Crear superusuario"
            echo "  populate    Poblar DB con datos de ejemplo"
            echo "  status      Mostrar estado y URLs"
            echo "  clean       Limpiar contenedores e imágenes"
            echo "  full-setup  Configuración completa desde cero"
            echo "  help        Mostrar esta ayuda"
            echo ""
            echo "Ejemplos:"
            echo "  $0 full-setup          # Primera vez"
            echo "  $0 start               # Iniciar servicios"
            echo "  $0 manage migrate      # Ejecutar migraciones"
            echo "  $0 manage shell        # Abrir shell de Django"
            ;;
    esac
}

main "$@"