const { app, BrowserWindow, Tray, Menu, ipcMain, Notification } = require('electron');
const path = require('path');
const Store = require('electron-store');
const activeWin = require('active-win');
const notifier = require('node-notifier');

// Configuración de almacenamiento
const store = new Store();

let mainWindow;
let tray;
let adviceInterval;
let systemMonitorInterval;

// Configuración por defecto
const defaultConfig = {
  apiUrl: process.env.API_URL || 'http://localhost:8000/api',
  authToken: null,
  userId: null,
  theme: 'dark',
  opacity: 0.9,
  position: { x: null, y: 50 },
  autoStart: true,
  showNotifications: true,
  proactiveAdvice: true,
  adviceInterval: 120000, // 2 minutos
  systemMonitorInterval: 30000, // 30 segundos
  reconnectInterval: 5000
};

class SaraAsistenteVirtual {
  constructor() {
    this.config = { ...defaultConfig, ...store.get('config', {}) };
    this.isAuthenticated = false;
    this.currentApp = null;
    // Detectar si estamos en modo headless (Docker)
    this.isHeadless = process.env.DOCKER_CONTAINER === 'true' || process.env.NODE_ENV === 'docker';
  }

  init() {
    app.whenReady().then(() => {
      if (!this.isHeadless) {
        this.createTray();
        this.createWindow();
      } else {
        console.log('🚀 Ejecutando en modo headless (Docker) - Sin interfaz gráfica');
        console.log('🔍 Iniciando monitoreo automático...');
        // En modo headless, no crear bandeja ni ventana
      }

      this.setupIPC();
      this.startSystemMonitoring();
      this.startAdvicePolling();

      // En modo headless, intentar login automático con credenciales de entorno
      if (this.isHeadless) {
        this.autoLogin();
      }
    });

    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0 && !this.isHeadless) {
        this.createWindow();
      }
    });
  }

  createWindow() {
    const { screen } = require('electron');
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;

    // Calcular posición por defecto (esquina superior derecha)
    const defaultX = width - 370;
    const defaultY = 50;

    const position = this.config.position;
    const x = position.x !== null ? position.x : defaultX;
    const y = position.y !== null ? position.y : defaultY;

    mainWindow = new BrowserWindow({
      width: 350,
      height: 500,
      x: x,
      y: y,
      frame: false,
      alwaysOnTop: true,
      skipTaskbar: true,
      resizable: false,
      movable: true,
      transparent: true,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, '../preload/preload.js')
      },
      show: false
      // Removido icon para evitar errores si no existe
    });

    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

    mainWindow.once('ready-to-show', () => {
      if (this.config.autoStart) {
        mainWindow.show();
      }
    });

    // Guardar posición cuando se mueva la ventana
    mainWindow.on('moved', () => {
      const [x, y] = mainWindow.getPosition();
      this.config.position = { x, y };
      store.set('config', this.config);
    });

    // Ocultar en lugar de cerrar
    mainWindow.on('close', (event) => {
      if (!app.isQuitting) {
        event.preventDefault();
        mainWindow.hide();
      }
    });

    return mainWindow;
  }

  createTray() {
    // Intentar cargar icono personalizado, si no existe usar icono del sistema
    let iconPath;
    try {
      iconPath = path.join(__dirname, '../../assets/icons/tray-icon.png');
      // Verificar si el archivo existe
      require('fs').accessSync(iconPath);
    } catch (error) {
      // Si no existe el icono personalizado, usar icono por defecto del sistema
      console.log('Icono personalizado no encontrado, usando icono del sistema');
      iconPath = undefined; // Electron usará un icono por defecto
    }

    try {
      tray = new Tray(iconPath);
    } catch (trayError) {
      console.error('Error creando bandeja del sistema:', trayError.message);
      // Crear tray sin icono si hay error
      try {
        tray = new Tray('');
      } catch (fallbackError) {
        console.error('Error creando bandeja sin icono:', fallbackError.message);
        // Continuar sin bandeja si es necesario
        return;
      }
    }

    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Mostrar Asistente',
        click: () => {
          if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
          }
        }
      },
      {
        label: 'Ocultar Asistente',
        click: () => {
          if (mainWindow) {
            mainWindow.hide();
          }
        }
      },
      { type: 'separator' },
      {
        label: 'Configuración',
        click: () => {
          // Abrir ventana de configuración
          this.openSettings();
        }
      },
      { type: 'separator' },
      {
        label: 'Salir',
        click: () => {
          app.isQuitting = true;
          app.quit();
        }
      }
    ]);

    tray.setToolTip('SARA Asistente Virtual - Siempre aquí para ayudar');
    tray.setContextMenu(contextMenu);

    // Doble click en tray muestra/oculta ventana
    tray.on('double-click', () => {
      if (mainWindow) {
        if (mainWindow.isVisible()) {
          mainWindow.hide();
        } else {
          mainWindow.show();
          mainWindow.focus();
        }
      }
    });
  }

  setupIPC() {
    // Comunicación con el renderer
    ipcMain.handle('get-config', () => {
      return this.config;
    });

    ipcMain.handle('set-config', (event, newConfig) => {
      this.config = { ...this.config, ...newConfig };
      store.set('config', this.config);
      return this.config;
    });

    ipcMain.handle('login', async (event, credentials) => {
      return await this.authenticate(credentials);
    });

    ipcMain.handle('logout', () => {
      this.logout();
    });

    ipcMain.handle('send-message', async (event, message) => {
      return await this.sendMessage(message);
    });

    ipcMain.handle('get-proactive-advice', async () => {
      return await this.getProactiveAdvice();
    });

    ipcMain.handle('show-notification', (event, notification) => {
      this.showNotification(notification);
    });

    ipcMain.handle('minimize-window', () => {
      if (mainWindow && !this.isHeadless) {
        mainWindow.minimize();
      }
    });

    ipcMain.handle('close-window', () => {
      if (mainWindow && !this.isHeadless) {
        mainWindow.hide();
      }
    });
  }

  async autoLogin() {
    // Intentar login automático con credenciales de entorno o por defecto
    const username = process.env.SARA_USERNAME || 'admin';
    const password = process.env.SARA_PASSWORD || 'admin123';

    console.log(`🔐 Intentando login automático con usuario: ${username}`);

    const result = await this.authenticate({ username, password });

    if (result.success) {
      console.log('✅ Login automático exitoso - Monitoreo iniciado');
      console.log(`👤 Usuario: ${result.user.username} (${result.user.rol})`);
      console.log('📊 El monitoreo está funcionando en background');
    } else {
      console.error('❌ Error en login automático:', result.error);
      console.log('🔄 Reintentando en 30 segundos...');
      setTimeout(() => this.autoLogin(), 30000);
    }
  }

  async authenticate(credentials) {
    try {
      const response = await fetch(`${this.config.apiUrl}/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: credentials.username,
          password: credentials.password,
          auto_start: true
        })
      });

      const data = await response.json();

      if (response.ok && data.user) {
        this.isAuthenticated = true;
        this.config.authToken = `Bearer ${data.user.id}`; // Simplificado
        this.config.userId = data.user.id;
        store.set('config', this.config);

        // Notificar autenticación exitosa
        this.showNotification({
          title: 'SARA Asistente',
          message: '¡Bienvenido! Monitoreo iniciado automáticamente.'
        });

        return { success: true, user: data.user };
      } else {
        return { success: false, error: data.error || 'Error de autenticación' };
      }
    } catch (error) {
      console.error('Error de autenticación:', error);
      return { success: false, error: 'Error de conexión' };
    }
  }

  logout() {
    this.isAuthenticated = false;
    this.config.authToken = null;
    this.config.userId = null;
    store.set('config', this.config);

    // Detener monitoreo
    this.stopSystemMonitoring();
    this.stopAdvicePolling();

    this.showNotification({
      title: 'SARA Asistente',
      message: 'Sesión cerrada. Monitoreo detenido.'
    });
  }

  async sendMessage(message) {
    if (!this.isAuthenticated) {
      return { error: 'No autenticado' };
    }

    try {
      const response = await fetch(`${this.config.apiUrl}/asistente/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.config.authToken
        },
        body: JSON.stringify({ mensaje: message })
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error enviando mensaje:', error);
      return { error: 'Error de conexión' };
    }
  }

  async getProactiveAdvice() {
    if (!this.isAuthenticated) {
      return null;
    }

    try {
      const response = await fetch(`${this.config.apiUrl}/consejos-proactivos/`, {
        headers: {
          'Authorization': this.config.authToken
        }
      });

      const data = await response.json();
      return data.consejos;
    } catch (error) {
      console.error('Error obteniendo consejos:', error);
      return null;
    }
  }

  startSystemMonitoring() {
    if (systemMonitorInterval) {
      clearInterval(systemMonitorInterval);
    }

    systemMonitorInterval = setInterval(async () => {
      if (!this.isAuthenticated) return;

      try {
        if (this.isHeadless) {
          // En modo headless, enviar actividad básica del sistema
          console.log('📊 Monitoreo activo - Sistema funcionando en background');

          // Enviar actividad básica al backend
          await this.sendActivity({
            ventana_activa: 'Sistema Docker',
            aplicacion: 'SARA Monitor',
            timestamp: new Date().toISOString(),
            tipo: 'background_monitoring'
          });
          return;
        }

        const activeWindow = await activeWin();

        if (activeWindow && activeWindow.owner.name !== this.currentApp) {
          this.currentApp = activeWindow.owner.name;

          // Enviar información de actividad al backend
          await this.sendActivity({
            ventana_activa: activeWindow.title,
            aplicacion: activeWindow.owner.name,
            timestamp: new Date().toISOString()
          });

          // Generar consejos contextuales basados en la aplicación
          const contextualAdvice = this.generateContextualAdvice(activeWindow);
          if (contextualAdvice) {
            this.showNotification({
              title: 'Consejo Contextual',
              message: contextualAdvice
            });

            // Enviar a la ventana del asistente solo si no estamos en modo headless
            if (mainWindow && !mainWindow.isDestroyed() && !this.isHeadless) {
              mainWindow.webContents.send('contextual-advice', contextualAdvice);
            }
          }
        }
      } catch (error) {
        if (!this.isHeadless) {
          console.error('Error monitoreando sistema:', error);
        }
        // En modo headless, ignorar errores de monitoreo silenciosamente
      }
    }, this.config.systemMonitorInterval);
  }

  stopSystemMonitoring() {
    if (systemMonitorInterval) {
      clearInterval(systemMonitorInterval);
      systemMonitorInterval = null;
    }
  }

  startAdvicePolling() {
    if (adviceInterval) {
      clearInterval(adviceInterval);
    }

    adviceInterval = setInterval(async () => {
      if (!this.isAuthenticated || !this.config.proactiveAdvice) return;

      const advice = await this.getProactiveAdvice();
      if (advice) {
        // Mostrar notificación
        this.showNotification({
          title: 'SARA tiene un consejo',
          message: advice.substring(0, 100) + (advice.length > 100 ? '...' : '')
        });

        // Enviar a la ventana del asistente solo si no estamos en modo headless
        if (mainWindow && !mainWindow.isDestroyed() && !this.isHeadless) {
          mainWindow.webContents.send('proactive-advice', advice);
        }
      }
    }, this.config.adviceInterval);
  }

  stopAdvicePolling() {
    if (adviceInterval) {
      clearInterval(adviceInterval);
      adviceInterval = null;
    }
  }

  async sendActivity(activityData) {
    if (!this.isAuthenticated) return;

    try {
      await fetch(`${this.config.apiUrl}/activity/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.config.authToken
        },
        body: JSON.stringify(activityData)
      });
    } catch (error) {
      console.error('Error enviando actividad:', error);
    }
  }

  generateContextualAdvice(activeWindow) {
    const appName = activeWindow.owner.name.toLowerCase();
    const windowTitle = activeWindow.title.toLowerCase();

    // Consejos basados en aplicación activa
    if (appName.includes('excel') || windowTitle.includes('excel')) {
      return '💡 Tip: Usa Ctrl+S para guardar frecuentemente tu trabajo en Excel';
    }

    if (appName.includes('word') || windowTitle.includes('word')) {
      return '💡 Tip: Usa Ctrl+B para negrita y Ctrl+I para cursiva en Word';
    }

    if (appName.includes('vscode') || appName.includes('visual studio')) {
      return '💡 Tip: Usa Ctrl+Shift+P para abrir la paleta de comandos en VS Code';
    }

    if (appName.includes('chrome') || appName.includes('firefox') || appName.includes('edge')) {
      const tabCount = this.countBrowserTabs(windowTitle);
      if (tabCount > 10) {
        return '🌐 Tienes muchas pestañas abiertas. Considera organizarlas o cerrar las innecesarias';
      }
    }

    return null;
  }

  countBrowserTabs(windowTitle) {
    // Estimación simple basada en el título
    const tabIndicators = [' - ', ' | ', ' – '];
    let count = 1;

    tabIndicators.forEach(indicator => {
      const parts = windowTitle.split(indicator);
      if (parts.length > count) {
        count = parts.length;
      }
    });

    return count;
  }

  showNotification(notification) {
    if (!this.config.showNotifications) return;

    if (this.isHeadless) {
      // En modo headless, mostrar notificaciones como logs
      console.log(`🔔 NOTIFICACIÓN: ${notification.title}`);
      console.log(`📝 ${notification.message}`);
      return;
    }

    const notificationOptions = {
      title: notification.title,
      message: notification.message,
      sound: true,
      wait: false
    };

    // Solo agregar icono si existe
    if (notification.icon) {
      try {
        require('fs').accessSync(notification.icon);
        notificationOptions.icon = notification.icon;
      } catch (error) {
        // Icono no existe, continuar sin él
      }
    }

    notifier.notify(notificationOptions);
  }

  openSettings() {
    // Crear ventana de configuración
    const settingsWindow = new BrowserWindow({
      width: 500,
      height: 600,
      parent: mainWindow,
      modal: true,
      show: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, '../preload/preload.js')
      }
    });

    settingsWindow.loadFile(path.join(__dirname, '../renderer/settings.html'));

    settingsWindow.once('ready-to-show', () => {
      settingsWindow.show();
    });
  }
}

// Iniciar aplicación
const asistente = new SaraAsistenteVirtual();
asistente.init();