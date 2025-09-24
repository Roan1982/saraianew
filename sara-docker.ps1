param(
    [Parameter(Mandatory=$false)]
    [string]$Command = "help",

    [Parameter(Mandatory=$false)]
    [string]$Service = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    SARA - Sistema de Asistencia IA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Show-Help {
    Write-Host "Uso: .\sara-docker.ps1 [-Command] <comando> [-Service <servicio>]"
    Write-Host ""
    Write-Host "Comandos disponibles:" -ForegroundColor Yellow
    Write-Host "  start    - Inicia el backend de SARA"
    Write-Host "  stop     - Detiene todos los servicios"
    Write-Host "  restart  - Reinicia todos los servicios"
    Write-Host "  logs     - Muestra logs (opcional: especificar servicio)"
    Write-Host "  status   - Muestra estado de los servicios"
    Write-Host "  clean    - Limpia contenedores e imagenes no utilizadas"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor Green
    Write-Host "  .\sara-docker.ps1 -Command start"
    Write-Host "  .\sara-docker.ps1 -Command logs -Service backend"
    Write-Host "  .\sara-docker.ps1 -Command status"
    Write-Host ""
    Write-Host "NOTA: La aplicacion Electron con GUI solo funciona en Linux." -ForegroundColor Red
    Write-Host "En Windows/Mac, ejecuta la aplicacion Electron nativamente." -ForegroundColor Red
}

switch ($Command.ToLower()) {
    "start" {
        Write-Host "Iniciando servicios de SARA..." -ForegroundColor Green
        docker-compose up -d backend
        Write-Host ""
        Write-Host "Servicios iniciados. El backend esta disponible en http://localhost:8000" -ForegroundColor Green
        Write-Host "Para iniciar la aplicacion Electron (solo Linux), usa: docker-compose --profile linux-gui up electron" -ForegroundColor Yellow
    }

    "stop" {
        Write-Host "Deteniendo servicios de SARA..." -ForegroundColor Yellow
        docker-compose down
    }

    "restart" {
        Write-Host "Reiniciando servicios de SARA..." -ForegroundColor Yellow
        docker-compose restart
    }

    "logs" {
        if ($Service) {
            Write-Host "Mostrando logs del servicio $Service..." -ForegroundColor Green
            docker-compose logs -f $Service
        } else {
            Write-Host "Mostrando logs de todos los servicios..." -ForegroundColor Green
            docker-compose logs -f
        }
    }

    "status" {
        Write-Host "Estado de los servicios de SARA:" -ForegroundColor Green
        docker-compose ps
    }

    "clean" {
        Write-Host "Limpiando contenedores e imagenes no utilizadas..." -ForegroundColor Yellow
        docker-compose down --volumes --remove-orphans
        docker system prune -f
    }

    default {
        Show-Help
    }
}