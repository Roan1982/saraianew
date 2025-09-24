@echo off
REM Instalar dependencias del cliente Electron usando Node.js local

echo Instalando dependencias del cliente SARA Monitor...
echo.

cd sara-monitor
call ..\local-node.bat npm install

echo.
echo Dependencias instaladas correctamente.
echo Para ejecutar el cliente: call ..\run-client.bat
echo.