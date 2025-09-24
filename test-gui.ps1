# Script de prueba para interfaz gráfica del asistente SARA
# Este script permite probar la configuración X11

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "    PRUEBA DE INTERFAZ GRÁFICA SARA" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si VcXsrv está ejecutándose
Write-Host "🔍 Verificando servidor X11..." -ForegroundColor Yellow
$vcxsrvRunning = $false
try {
    $vcxsrv = Get-Process -Name "*vcxsrv*" -ErrorAction SilentlyContinue
    if ($vcxsrv) {
        Write-Host "✅ VcXsrv detectado (PID: $($vcxsrv.Id))" -ForegroundColor Green
        $vcxsrvRunning = $true
    } else {
        Write-Host "⚠️  VcXsrv NO detectado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  No se pudo verificar VcXsrv" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 INSTRUCCIONES PARA INTERFAZ GRÁFICA:" -ForegroundColor Cyan
Write-Host "1. Descarga VcXsrv: https://sourceforge.net/projects/vcxsrv/" -ForegroundColor White
Write-Host "2. Instala VcXsrv" -ForegroundColor White
Write-Host "3. Ejecuta XLaunch:" -ForegroundColor White
Write-Host "   • Multiple windows" -ForegroundColor Gray
Write-Host "   • Display number: 0" -ForegroundColor Gray
Write-Host "   • Start no client" -ForegroundColor Gray
Write-Host "   • ✅ Disable access control" -ForegroundColor Gray
Write-Host "4. Vuelve a ejecutar este script" -ForegroundColor White
Write-Host ""

if (-not $vcxsrvRunning) {
    Write-Host "❌ SIN INTERFAZ GRÁFICA:" -ForegroundColor Red
    Write-Host "El asistente funcionará en background (sin ventana visible)" -ForegroundColor White
    Write-Host "Podrás acceder vía API y logs" -ForegroundColor White
    Write-Host ""
}

# Configurar DISPLAY
$env:DISPLAY = "host.docker.internal:0.0"
Write-Host "🔧 Configurando DISPLAY=$env:DISPLAY" -ForegroundColor Green

# Verificar Docker
Write-Host ""
Write-Host "🐳 Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green

    docker info >$null 2>&1
    Write-Host "✅ Docker ejecutándose" -ForegroundColor Green
} catch {
    Write-Host "❌ Error con Docker" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Iniciando servicios..." -ForegroundColor Yellow

# Iniciar servicios
try {
    docker-compose up -d

    Write-Host ""
    Write-Host "✅ Servicios iniciados!" -ForegroundColor Green
    Write-Host ""

    if ($vcxsrvRunning) {
        Write-Host "🎯 INTERFAZ GRÁFICA:" -ForegroundColor Cyan
        Write-Host "• Busca la ventana flotante 'SARA IA'" -ForegroundColor White
        Write-Host "• Debería aparecer en pocos segundos" -ForegroundColor White
        Write-Host "• Si no aparece, revisa la configuración de VcXsrv" -ForegroundColor White
    } else {
        Write-Host "🎯 MODO BACKGROUND:" -ForegroundColor Cyan
        Write-Host "• El asistente está ejecutándose sin interfaz visible" -ForegroundColor White
        Write-Host "• Funciona completamente vía API" -ForegroundColor White
    }

    Write-Host ""
    Write-Host "🔗 ACCESOS DISPONIBLES:" -ForegroundColor Cyan
    Write-Host "• Backend: http://localhost:8000" -ForegroundColor White
    Write-Host "• Admin: http://localhost:8000/admin/" -ForegroundColor White
    Write-Host "• Health: http://localhost:8000/api/health/" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 MONITOREO:" -ForegroundColor Cyan
    Write-Host "• Estado: docker-compose ps" -ForegroundColor White
    Write-Host "• Logs backend: docker-compose logs -f backend" -ForegroundColor White
    Write-Host "• Logs asistente: docker-compose logs -f electron" -ForegroundColor White
    Write-Host ""

    # Probar health check
    Write-Host "🏥 Probando conexión..." -ForegroundColor Yellow
    try {
        $health = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -Method GET -TimeoutSec 10
        if ($health.StatusCode -eq 200) {
            Write-Host "✅ Backend respondiendo correctamente" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Backend no responde aún (espera unos segundos)" -ForegroundColor Yellow
    }

} catch {
    Write-Host "❌ Error al iniciar servicios: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "CONSEJOS:" -ForegroundColor Cyan
Write-Host "- Para detener: docker-compose down" -ForegroundColor White
Write-Host "- Para reconstruir: docker-compose up --build -d" -ForegroundColor White
Write-Host "- Para acceder al contenedor: docker-compose exec electron bash" -ForegroundColor White
Write-Host ""

Write-Host "Presiona Enter para continuar..." -ForegroundColor Gray
Read-Host