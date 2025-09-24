# Script de PowerShell para verificar estado de SARA Docker

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "    VERIFICACION SARA DOCKER" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Verificando estado de contenedores..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Verificando conectividad del backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -TimeoutSec 10
    Write-Host "✓ Backend responde correctamente" -ForegroundColor Green
    Write-Host "Respuesta: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "✗ Backend no responde: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Verificando logs recientes del backend..." -ForegroundColor Yellow
Write-Host ""
docker-compose logs --tail=10 backend

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Verificando logs recientes de Electron..." -ForegroundColor Yellow
Write-Host ""
docker-compose logs --tail=10 electron

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Comandos utiles:" -ForegroundColor Cyan
Write-Host "- Ver logs en tiempo real backend: docker-compose logs -f backend" -ForegroundColor White
Write-Host "- Ver logs en tiempo real Electron: docker-compose logs -f electron" -ForegroundColor White
Write-Host "- Detener servicios: docker-compose down" -ForegroundColor White
Write-Host ""

Write-Host "Presiona Enter para continuar..." -ForegroundColor Gray
Read-Host