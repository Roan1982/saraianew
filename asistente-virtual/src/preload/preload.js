const { contextBridge, ipcRenderer } = require('electron');

// API segura para el renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // Configuración
  getConfig: () => ipcRenderer.invoke('get-config'),
  setConfig: (config) => ipcRenderer.invoke('set-config', config),

  // Autenticación
  login: (credentials) => ipcRenderer.invoke('login', credentials),
  logout: () => ipcRenderer.invoke('logout'),

  // Chat y consejos
  sendMessage: (message) => ipcRenderer.invoke('send-message', message),
  getProactiveAdvice: () => ipcRenderer.invoke('get-proactive-advice'),

  // Notificaciones
  showNotification: (notification) => ipcRenderer.invoke('show-notification', notification),

  // Control de ventana
  minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
  closeWindow: () => ipcRenderer.invoke('close-window'),

  // Eventos del main process
  onProactiveAdvice: (callback) => {
    ipcRenderer.on('proactive-advice', (event, advice) => callback(advice));
  },

  onContextualAdvice: (callback) => {
    ipcRenderer.on('contextual-advice', (event, advice) => callback(advice));
  },

  onNotification: (callback) => {
    ipcRenderer.on('notification', (event, notification) => callback(notification));
  },

  // Remover listeners
  removeAllListeners: (event) => {
    ipcRenderer.removeAllListeners(event);
  }
});

// Utilidades adicionales
contextBridge.exposeInMainWorld('utils', {
  platform: process.platform,
  version: process.version,

  // Funciones de ayuda
  formatTime: (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  formatDate: (timestamp) => {
    return new Date(timestamp).toLocaleDateString('es-ES');
  }
});