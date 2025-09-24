param(
    [switch]$SkipNodeCheck,
    [switch]$Force
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALADOR SARA ASISTENTE VIRTUAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Función para verificar comandos
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Verificar Node.js
if (-not $SkipNodeCheck) {
    Write-Host "Verificando Node.js..." -ForegroundColor Yellow

    if (Test-Command "node") {
        Write-Host "✅ Node.js encontrado" -ForegroundColor Green
        $nodeVersion = & node --version
        Write-Host "   Versión: $nodeVersion" -ForegroundColor Gray
    } else {
        Write-Host "❌ Node.js no está instalado" -ForegroundColor Red
        Write-Host ""
        Write-Host "Para instalar Node.js:" -ForegroundColor Yellow
        Write-Host "1. Ve a https://nodejs.org/" -ForegroundColor White
        Write-Host "2. Descarga la versión LTS (Recomendada)" -ForegroundColor White
        Write-Host "3. Instala Node.js" -ForegroundColor White
        Write-Host "4. Reinicia PowerShell" -ForegroundColor White
        Write-Host "5. Vuelve a ejecutar este script" -ForegroundColor White
        Write-Host ""
        Read-Host "Presiona Enter para salir"
        exit 1
    }

    # Verificar npm
    Write-Host ""
    Write-Host "Verificando npm..." -ForegroundColor Yellow

    if (Test-Command "npm") {
        Write-Host "✅ npm encontrado" -ForegroundColor Green
        $npmVersion = & npm --version
        Write-Host "   Versión: $npmVersion" -ForegroundColor Gray
    } else {
        Write-Host "❌ npm no está disponible" -ForegroundColor Red
        Write-Host ""
        Write-Host "npm debería venir incluido con Node.js." -ForegroundColor Yellow
        Write-Host "Intenta reinstalar Node.js desde https://nodejs.org/" -ForegroundColor Yellow
        Read-Host "Presiona Enter para salir"
        exit 1
    }
}

# Instalar dependencias
Write-Host ""
Write-Host "Instalando dependencias del proyecto..." -ForegroundColor Yellow
Write-Host "Esto puede tomar varios minutos..." -ForegroundColor Gray
Write-Host ""

try {
    if ($Force) {
        Write-Host "Forzando instalación completa..." -ForegroundColor Yellow
        if (Test-Path "node_modules") {
            Write-Host "Eliminando node_modules existentes..." -ForegroundColor Yellow
            Remove-Item -Recurse -Force node_modules
        }
        & npm cache clean --force 2>$null
    }

    & npm install

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Dependencias instaladas correctamente" -ForegroundColor Green
        Write-Host ""
        Write-Host "Para ejecutar el asistente:" -ForegroundColor Cyan
        Write-Host "- Modo desarrollo: npm run dev" -ForegroundColor White
        Write-Host "- Producción: npm start" -ForegroundColor White
        Write-Host ""
        Write-Host "¡Listo para usar SARA Asistente Virtual!" -ForegroundColor Green
        Write-Host ""
    } else {
        throw "Error en npm install"
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error instalando dependencias" -ForegroundColor Red
    Write-Host ""
    Write-Host "Posibles soluciones:" -ForegroundColor Yellow
    Write-Host "- Verifica tu conexión a internet" -ForegroundColor White
    Write-Host "- Ejecuta con -Force para reinstalar: .\install.ps1 -Force" -ForegroundColor White
    Write-Host "- Borra node_modules manualmente y ejecuta nuevamente" -ForegroundColor White
    Write-Host "- Ejecuta: npm cache clean --force" -ForegroundColor White
    Write-Host ""
    exit 1
}

Read-Host "Presiona Enter para continuar"