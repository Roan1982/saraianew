const { contextBridge, ipcRenderer } = require('electron');

// Exponer APIs seguras al renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // Login
  loginUser: (credentials) => ipcRenderer.invoke('login-user', credentials),
  getCurrentUser: () => ipcRenderer.invoke('get-current-user'),

  // Control del monitoreo
  startMonitoring: () => ipcRenderer.invoke('start-monitoring'),
  stopMonitoring: () => ipcRenderer.invoke('stop-monitoring'),

  // Datos de actividad
  getActivityData: () => ipcRenderer.invoke('get-activity-data'),
  clearActivityData: () => ipcRenderer.invoke('clear-activity-data'),

  // Eventos
  onActivityUpdate: (callback) => {
    ipcRenderer.on('activity-update', (event, data) => callback(data));
  },

  // Remover listeners
  removeAllListeners: (event) => {
    ipcRenderer.removeAllListeners(event);
  }
});

// También exponer versiones de Node.js necesarias
contextBridge.exposeInMainWorld('versions', {
  node: process.versions.node,
  chrome: process.versions.chrome,
  electron: process.versions.electron
});