const { app, BrowserWindow, ipcMain, Tray, Menu, Notification } = require('electron');
const path = require('path');
const si = require('systeminformation');
const axios = require('axios');
const machineId = require('node-machine-id').machineIdSync();

let mainWindow;
let tray;
let activityData = [];
let monitoringInterval;

// Configuración del servidor Django
const DJANGO_SERVER = 'http://127.0.0.1:8000';
let currentUser = null; // Usuario autenticado

// Función de login
async function loginUser(username, password) {
  try {
    const response = await axios.post(`${DJANGO_SERVER}/api/login/`, {
      username,
      password
    });

    if (response.data && response.data.user) {
      currentUser = response.data.user;
      console.log('Usuario autenticado:', currentUser.username);
      return { success: true, user: currentUser };
    } else {
      return { success: false, error: 'Respuesta inválida del servidor' };
    }
  } catch (error) {
    console.error('Error de login:', error.response?.data || error.message);
    let errorMessage = 'Error de conexión';

    if (error.response) {
      if (error.response.status === 401) {
        errorMessage = 'Usuario o contraseña incorrectos';
      } else if (error.response.data && error.response.data.error) {
        errorMessage = error.response.data.error;
      }
    }

    return { success: false, error: errorMessage };
  }
}
const API_ENDPOINT = '/api/activity/';

// Crear ventana principal
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: getIconPath(),
    show: false
  });

  mainWindow.loadFile('index.html');

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Función auxiliar para obtener ruta de icono
function getIconPath() {
  try {
    const iconPath = path.join(__dirname, 'assets', 'icon.png');
    if (require('fs').existsSync(iconPath)) {
      return iconPath;
    }
  } catch (error) {
    // Ignorar error
  }
  return undefined;
}

// Crear bandeja del sistema
function createTray() {
  try {
    // Intentar usar un icono del sistema o crear uno básico
    let trayIcon;
    try {
      trayIcon = path.join(__dirname, 'assets', 'tray-icon.png');
      // Verificar si el archivo existe
      if (!require('fs').existsSync(trayIcon)) {
        // Usar un icono alternativo o ninguno
        trayIcon = undefined;
      }
    } catch (error) {
      trayIcon = undefined;
    }

    tray = new Tray(trayIcon || path.join(__dirname, 'assets', 'icon.png') || undefined);

    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Mostrar SARA Monitor',
        click: () => {
          if (mainWindow) {
            mainWindow.show();
          } else {
            createWindow();
          }
        }
      },
      {
        label: 'Pausar Monitoreo',
        click: () => {
          stopMonitoring();
          showNotification('Monitoreo pausado', 'El monitoreo de actividad ha sido detenido.');
        }
      },
      {
        label: 'Reanudar Monitoreo',
        click: () => {
          startMonitoring();
          showNotification('Monitoreo reanudado', 'El monitoreo de actividad ha sido iniciado.');
        }
      },
      { type: 'separator' },
      {
        label: 'Salir',
        click: () => {
          stopMonitoring();
          app.quit();
        }
      }
    ]);

    tray.setToolTip('SARA Monitor - Sistema de Productividad');
    tray.setContextMenu(contextMenu);

    tray.on('click', () => {
      if (mainWindow) {
        mainWindow.show();
      } else {
        createWindow();
      }
    });
  } catch (error) {
    console.log('Error creando bandeja del sistema:', error.message);
    // Continuar sin bandeja si hay error
  }
}

// Mostrar notificaciones
function showNotification(title, body) {
  try {
    let iconPath;
    try {
      iconPath = path.join(__dirname, 'assets', 'icon.png');
      if (!require('fs').existsSync(iconPath)) {
        iconPath = undefined;
      }
    } catch (error) {
      iconPath = undefined;
    }

    new Notification({
      title: title,
      body: body,
      icon: iconPath
    }).show();
  } catch (error) {
    console.log('Error mostrando notificación:', error.message);
    // Continuar sin notificación si hay error
  }
}

// Iniciar monitoreo de actividad
function startMonitoring() {
  if (monitoringInterval) return;

  console.log('Iniciando monitoreo de actividad...');

  monitoringInterval = setInterval(async () => {
    try {
      const activity = await captureActivity();
      activityData.push(activity);

      // Enviar datos al servidor cada 30 segundos
      if (activityData.length >= 6) {
        await sendActivityData();
      }

      // Enviar a la interfaz
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('activity-update', activity);
      }
    } catch (error) {
      console.error('Error en monitoreo:', error);
    }
  }, 5000); // Cada 5 segundos
}

// Detener monitoreo
function stopMonitoring() {
  if (monitoringInterval) {
    clearInterval(monitoringInterval);
    monitoringInterval = null;
    console.log('Monitoreo detenido');
  }
}

// Capturar actividad actual
async function captureActivity() {
  const timestamp = new Date().toISOString();

  // Información del sistema
  const [processes, currentLoad] = await Promise.all([
    si.processes(),
    si.currentLoad()
  ]);

  // Procesos activos ordenados por uso de CPU
  const topProcesses = processes.list
    .filter(p => p.cpu > 0.1) // Solo procesos con CPU > 0.1%
    .sort((a, b) => b.cpu - a.cpu)
    .slice(0, 5)
    .map(p => ({
      name: p.name,
      cpu: Math.round(p.cpu * 100) / 100,
      memory: Math.round(p.mem * 100) / 100
    }));

  // Ventana activa (simplificado)
  let activeWindow = 'Desconocido';
  try {
    // En Windows, podríamos usar otras librerías para detectar ventana activa
    // Por ahora usamos el proceso más activo
    activeWindow = topProcesses[0]?.name || 'Sistema';
  } catch (error) {
    console.log('No se pudo detectar ventana activa');
  }

  return {
    timestamp,
    machineId,
    activeWindow,
    topProcesses,
    systemLoad: {
      cpu: Math.round(currentLoad.currentLoad * 100) / 100,
      cpus: currentLoad.cpus.length
    },
    productivity: analyzeProductivity(activeWindow, topProcesses)
  };
}

// Análisis básico de productividad
function analyzeProductivity(activeWindow, processes) {
  const productiveApps = [
    'code', 'vscode', 'sublime', 'notepad++', 'excel', 'word',
    'chrome', 'firefox', 'edge', 'outlook', 'teams'
  ];

  const unproductiveApps = [
    'whatsapp', 'telegram', 'discord', 'steam', 'epicgames',
    'netflix', 'youtube', 'facebook', 'instagram', 'twitter'
  ];

  const gamingApps = [
    'steam', 'epicgames', 'battle.net', 'origin', 'uplay',
    'gog', 'minecraft', 'valorant', 'league', 'csgo'
  ];

  const window = activeWindow.toLowerCase();

  if (productiveApps.some(app => window.includes(app))) {
    return 'productive';
  } else if (unproductiveApps.some(app => window.includes(app))) {
    return 'unproductive';
  } else if (gamingApps.some(app => window.includes(app))) {
    return 'gaming';
  } else {
    return 'neutral';
  }
}

// Enviar datos de actividad al servidor Django
async function sendActivityData() {
  if (activityData.length === 0 || !currentUser) return;

  try {
    const response = await axios.post(`${DJANGO_SERVER}${API_ENDPOINT}`, {
      machineId,
      userId: currentUser.id,
      activities: activityData
    }, {
      headers: {
        'Content-Type': 'application/json',
        // Aquí iría autenticación JWT si fuera necesario
      }
    });

    console.log('Datos enviados al servidor:', response.status);
    activityData = []; // Limpiar datos enviados

  } catch (error) {
    console.error('Error enviando datos:', error.message);
    // Guardar localmente si falla el envío
    saveLocalData(activityData);
    activityData = [];
  }
}

// Guardar datos localmente (fallback)
function saveLocalData(data) {
  const fs = require('fs');
  const fileName = `activity_backup_${Date.now()}.json`;
  fs.writeFileSync(fileName, JSON.stringify(data, null, 2));
  console.log(`Datos guardados localmente: ${fileName}`);
}

// IPC handlers
ipcMain.handle('login-user', async (event, credentials) => {
  if (!credentials || !credentials.username || !credentials.password) {
    return { success: false, error: 'Usuario y contraseña son requeridos' };
  }
  return await loginUser(credentials.username, credentials.password);
});

ipcMain.handle('get-current-user', () => {
  return currentUser;
});

ipcMain.handle('start-monitoring', () => {
  if (!currentUser) {
    return { success: false, error: 'Usuario no autenticado' };
  }
  startMonitoring();
  return { success: true };
});

ipcMain.handle('stop-monitoring', () => {
  stopMonitoring();
  return { success: true };
});

ipcMain.handle('get-activity-data', () => {
  return activityData;
});

ipcMain.handle('clear-activity-data', () => {
  activityData = [];
  return { success: true };
});

// App events
app.whenReady().then(() => {
  createTray();
  createWindow();

  // No iniciar monitoreo automáticamente - esperar login
  showNotification(
    'SARA Monitor Iniciado',
    'Por favor, inicia sesión para comenzar el monitoreo.'
  );
});

app.on('window-all-closed', (event) => {
  event.preventDefault(); // Evitar cerrar completamente
});

app.on('before-quit', () => {
  stopMonitoring();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});