@echo off
echo Verificando entorno virtual...

if not exist ".venv\Scripts\activate.bat" (
    echo Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo Error: No se pudo crear el entorno virtual. Verifica que Python esté instalado.
        pause
        exit /b 1
    )
) else (
    echo Entorno virtual encontrado.
)

echo Activando entorno virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

echo Instalando dependencias de Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: No se pudieron instalar las dependencias de Python.
    pause
    exit /b 1
)

echo Ejecutando migraciones...
python manage.py migrate
if errorlevel 1 (
    echo Error: No se pudieron ejecutar las migraciones.
    pause
    exit /b 1
)

echo Verificando cliente Electron...
if not exist "sara-monitor\node_modules" (
    echo Instalando dependencias del cliente Electron...
    call install-client.bat
    if errorlevel 1 (
        echo Advertencia: No se pudieron instalar las dependencias del cliente.
        echo El servidor seguirá funcionando, pero el cliente no estará disponible.
    )
) else (
    echo Cliente Electron listo.
)

echo.
echo ===========================================
echo SARA Sistema listo!
echo ===========================================
echo.
echo Servidor web: http://127.0.0.1:8000
echo Cliente de monitoreo: Ejecuta run-client.bat
echo.
echo Presiona Ctrl+C para detener el servidor
echo ===========================================
echo.

python manage.py runserver

pause