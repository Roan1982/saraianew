@echo off
echo ========================================
echo   INSTALADOR SARA ASISTENTE VIRTUAL
echo ========================================
echo.

echo Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js no está instalado
    echo.
    echo Para instalar Node.js:
    echo 1. Ve a https://nodejs.org/
    echo 2. Descarga la versión LTS (Recomendada)
    echo 3. Instala Node.js
    echo 4. Reinicia la terminal
    echo 5. Vuelve a ejecutar este script
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Node.js encontrado
    node --version
)

echo.
echo Verificando npm...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm no está disponible
    echo.
    echo npm debería venir incluido con Node.js.
    echo Intenta reinstalar Node.js desde https://nodejs.org/
    pause
    exit /b 1
) else (
    echo ✅ npm encontrado
    npm --version
)

echo.
echo Instalando dependencias del proyecto...
echo Esto puede tomar varios minutos...
echo.

npm install

if %errorlevel% neq 0 (
    echo.
    echo ❌ Error instalando dependencias
    echo.
    echo Posibles soluciones:
    echo - Verifica tu conexión a internet
    echo - Borra node_modules y ejecuta npm install nuevamente
    echo - Ejecuta: npm cache clean --force
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Dependencias instaladas correctamente
echo.
echo Para ejecutar el asistente:
echo - Modo desarrollo: npm run dev
echo - Producción: npm start
echo.
echo ¡Listo para usar SARA Asistente Virtual!
echo.

pause