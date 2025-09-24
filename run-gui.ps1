# Script para configurar X11 en Windows y ejecutar SARA con interfaz gráfica
# Requiere: VcXsrv instalado (https://sourceforge.net/projects/vcxsrv/)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "    SARA ASISTENTE VIRTUAL - GUI MODE" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si VcXsrv está ejecutándose
Write-Host "Verificando servidor X11..." -ForegroundColor Yellow
try {
    $vcxsrv = Get-Process -Name "vcxsrv" -ErrorAction SilentlyContinue
    if ($vcxsrv) {
        Write-Host "✓ VcXsrv está ejecutándose (PID: $($vcxsrv.Id))" -ForegroundColor Green
    } else {
        Write-Host "⚠ VcXsrv no está ejecutándose" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Para habilitar la interfaz gráfica:" -ForegroundColor Cyan
        Write-Host "1. Descarga VcXsrv desde: https://sourceforge.net/projects/vcxsrv/" -ForegroundColor White
        Write-Host "2. Instala VcXsrv" -ForegroundColor White
        Write-Host "3. Ejecuta XLaunch con estas opciones:" -ForegroundColor White
        Write-Host "   - Multiple windows" -ForegroundColor Gray
        Write-Host "   - Display number: 0" -ForegroundColor Gray
        Write-Host "   - Start no client" -ForegroundColor Gray
        Write-Host "   - Disable access control" -ForegroundColor Gray
        Write-Host ""
        $response = Read-Host "¿Quieres continuar sin interfaz gráfica? (s/n)"
        if ($response -ne 's' -and $response -ne 'S') {
            exit 1
        }
    }
} catch {
    Write-Host "No se pudo verificar VcXsrv" -ForegroundColor Yellow
}

# Configurar variable DISPLAY
$env:DISPLAY = "host.docker.internal:0.0"
Write-Host "✓ Variable DISPLAY configurada: $env:DISPLAY" -ForegroundColor Green

# Verificar Docker
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "✓ Docker encontrado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker no está instalado" -ForegroundColor Red
    exit 1
}

# Verificar Docker ejecutándose
try {
    docker info >$null 2>&1
    Write-Host "✓ Docker está ejecutándose" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker no está ejecutándose" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Iniciando SARA con interfaz gráfica..." -ForegroundColor Yellow

# Ejecutar docker-compose
try {
    docker-compose up --build -d

    Write-Host ""
    Write-Host "✓ Servicios iniciados exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 ACCESO AL ASISTENTE:" -ForegroundColor Cyan
    Write-Host "1. El asistente debería aparecer como una ventana flotante" -ForegroundColor White
    Write-Host "2. Si no aparece, verifica que VcXsrv esté ejecutándose" -ForegroundColor White
    Write-Host "3. La ventana del asistente tiene:" -ForegroundColor White
    Write-Host "   - Login (usuario/contraseña)" -ForegroundColor Gray
    Write-Host "   - Panel de consejos" -ForegroundColor Gray
    Write-Host "   - Chat rápido" -ForegroundColor Gray
    Write-Host "   - Estado de monitoreo" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📊 SERVICIOS DISPONIBLES:" -ForegroundColor Cyan
    Write-Host "- Backend Django: http://localhost:8000" -ForegroundColor White
    Write-Host "- Base de datos: SQLite (persistente)" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 COMANDOS ÚTILES:" -ForegroundColor Cyan
    Write-Host "- Ver estado: docker-compose ps" -ForegroundColor White
    Write-Host "- Ver logs backend: docker-compose logs -f backend" -ForegroundColor White
    Write-Host "- Ver logs asistente: docker-compose logs -f electron" -ForegroundColor White
    Write-Host "- Detener todo: docker-compose down" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host "✗ Error al iniciar servicios: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Presiona Enter para continuar..." -ForegroundColor Gray
Read-Host