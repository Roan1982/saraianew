# Script de PowerShell para ejecutar S    Write-Host "✓ Servicios iniciados exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 ACCESO AL ASISTENTE:" -ForegroundColor Cyan
    Write-Host "- Interfaz Web: http://localhost:8000/asistente/" -ForegroundColor White
    Write-Host "- Admin Django: http://localhost:8000/admin/" -ForegroundColor White
    Write-Host "- API Health: http://localhost:8000/api/health/" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 INSTRUCCIONES:" -ForegroundColor Cyan
    Write-Host "1. Abre http://localhost:8000/asistente/" -ForegroundColor White
    Write-Host "2. Haz login con tu usuario y contraseña" -ForegroundColor White
    Write-Host "3. ¡El monitoreo se inicia automáticamente!" -ForegroundColor White
    Write-Host "4. Recibe consejos inteligentes cada 2 minutos" -ForegroundColor White
    Write-Host "5. Chatea con SARA IA" -ForegroundColor White
    Write-Host ""er
# Requiere Docker Desktop instalado y ejecutándose

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "    SARA ASISTENTE VIRTUAL - DOCKER" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Docker está instalado
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "✓ Docker encontrado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker no está instalado o no está en PATH" -ForegroundColor Red
    Write-Host "Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar si Docker está ejecutándose
try {
    docker info >$null 2>&1
    Write-Host "✓ Docker está ejecutándose" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker no está ejecutándose" -ForegroundColor Red
    Write-Host "Por favor inicia Docker Desktop" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "Construyendo e iniciando servicios..." -ForegroundColor Yellow

# Ejecutar docker-compose
try {
    docker-compose up --build -d

    Write-Host ""
    Write-Host "✓ Servicios iniciados exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 ACCESO AL ASISTENTE:" -ForegroundColor Cyan
    Write-Host "- Interfaz Web: http://localhost:8000/asistente/" -ForegroundColor White
    Write-Host "- Admin Django: http://localhost:8000/admin/" -ForegroundColor White
    Write-Host "- API Health: http://localhost:8000/api/health/" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 INSTRUCCIONES:" -ForegroundColor Cyan
    Write-Host "1. Abre http://localhost:8000/asistente/" -ForegroundColor White
    Write-Host "2. Haz login con tu usuario y contraseña" -ForegroundColor White
    Write-Host "3. ¡El monitoreo se inicia automáticamente!" -ForegroundColor White
    Write-Host "4. Recibe consejos inteligentes cada 2 minutos" -ForegroundColor White
    Write-Host "5. Chatea con SARA IA" -ForegroundColor White
    Write-Host ""

    Write-Host "Servicios disponibles:" -ForegroundColor Cyan
    Write-Host "- Backend Django: http://localhost:8000" -ForegroundColor White
    Write-Host "- Interfaz Web SARA: http://localhost:8000/asistente/" -ForegroundColor White
    Write-Host ""
    Write-Host "Comandos útiles:" -ForegroundColor Cyan
    Write-Host "- Ver estado: docker-compose ps" -ForegroundColor White
    Write-Host "- Ver logs: docker-compose logs -f backend" -ForegroundColor White
    Write-Host "- Detener servicios: docker-compose down" -ForegroundColor White

} catch {
    Write-Host "✗ Error al iniciar servicios: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "Presiona Enter para continuar..." -ForegroundColor Gray
Read-Host