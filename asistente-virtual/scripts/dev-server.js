#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class DevServer {
  constructor() {
    this.electronProcess = null;
    this.watching = false;
  }

  start() {
    console.log('🚀 Iniciando servidor de desarrollo para SARA Asistente Virtual...');

    this.checkDependencies();
    this.startElectron();
    this.watchFiles();
  }

  checkDependencies() {
    console.log('📦 Verificando dependencias...');

    const packageJson = require('./package.json');
    const requiredDeps = Object.keys(packageJson.dependencies || {});

    // Aquí podrías verificar si las dependencias están instaladas
    console.log(`✅ Dependencias requeridas: ${requiredDeps.length}`);
  }

  startElectron() {
    console.log('⚡ Iniciando Electron...');

    const electronPath = path.join(__dirname, 'node_modules', '.bin', 'electron');
    const mainPath = path.join(__dirname, 'src', 'main', 'main.js');

    this.electronProcess = spawn(electronPath, [mainPath], {
      stdio: 'inherit',
      env: { ...process.env, NODE_ENV: 'development' }
    });

    this.electronProcess.on('close', (code) => {
      console.log(`🔄 Electron cerrado con código ${code}`);
      if (this.watching) {
        console.log('🔄 Reiniciando Electron...');
        setTimeout(() => this.startElectron(), 1000);
      }
    });

    this.electronProcess.on('error', (error) => {
      console.error('❌ Error iniciando Electron:', error);
    });
  }

  watchFiles() {
    console.log('👀 Iniciando watcher de archivos...');

    const chokidar = require('chokidar');

    const watchPaths = [
      'src/main/**/*.js',
      'src/preload/**/*.js',
      'src/renderer/**/*.{html,css,js}',
      'package.json'
    ];

    const watcher = chokidar.watch(watchPaths, {
      ignored: /(^|[\/\\])\../, // Ignorar archivos ocultos
      persistent: true,
      ignoreInitial: true
    });

    watcher.on('change', (filePath) => {
      console.log(`📝 Archivo modificado: ${filePath}`);
      this.restartElectron();
    });

    watcher.on('add', (filePath) => {
      console.log(`➕ Archivo agregado: ${filePath}`);
      this.restartElectron();
    });

    watcher.on('unlink', (filePath) => {
      console.log(`➖ Archivo eliminado: ${filePath}`);
      this.restartElectron();
    });

    this.watching = true;
    console.log('✅ Watcher activo');
  }

  restartElectron() {
    if (this.electronProcess) {
      console.log('🛑 Deteniendo Electron...');
      this.electronProcess.kill('SIGTERM');

      // Esperar un poco antes de reiniciar
      setTimeout(() => {
        this.startElectron();
      }, 500);
    }
  }

  stop() {
    console.log('🛑 Deteniendo servidor de desarrollo...');

    if (this.electronProcess) {
      this.electronProcess.kill('SIGTERM');
    }

    this.watching = false;
    process.exit(0);
  }
}

// Manejar señales de terminación
process.on('SIGINT', () => {
  console.log('\n👋 Recibida señal de interrupción...');
  if (global.devServer) {
    global.devServer.stop();
  }
});

process.on('SIGTERM', () => {
  console.log('\n👋 Recibida señal de terminación...');
  if (global.devServer) {
    global.devServer.stop();
  }
});

// Iniciar servidor si se ejecuta directamente
if (require.main === module) {
  const devServer = new DevServer();
  global.devServer = devServer;
  devServer.start();
}

module.exports = DevServer;