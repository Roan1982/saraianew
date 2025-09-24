#!/bin/bash

# Iniciar Xvfb en background para proporcionar un display virtual
echo "Iniciando Xvfb..."
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99

# Esperar a que Xvfb esté listo
sleep 2

# Verificar que las dependencias estén instaladas
echo "Verificando dependencias..."
cd /app
if [ -d "node_modules/electron-store" ]; then
    echo "✓ electron-store está instalado"
else
    echo "✗ electron-store NO está instalado"
    exit 1
fi

# Esperar a que el backend esté listo
echo "Esperando a que el backend esté listo..."
while ! curl -s http://backend:8000/api/health/ > /dev/null; do
  echo "Backend no está listo, esperando..."
  sleep 2
done

echo "Backend listo, iniciando aplicación Electron..."
npm start