# Asistente Virtual IA - Aplicación de Escritorio Flotante

## 🎯 **Objetivo**
Crear un asistente virtual flotante que esté siempre presente en el escritorio del usuario, proporcionando ayuda proactiva sin necesidad de abrir ventanas adicionales.

## 🏗️ **Arquitectura Técnica**

### **Tecnologías**
- **Electron.js**: Para crear la aplicación de escritorio flotante
- **React/Vue**: Para la interfaz del asistente
- **WebSocket/SSE**: Para comunicación en tiempo real con el backend
- **SQLite/LocalStorage**: Para cache local de consejos
- **APIs del sistema**: Para detección de aplicaciones activas

### **Componentes**
1. **Ventana Flotante Principal**: Siempre visible, minimizable
2. **Panel de Consejos**: Muestra consejos proactivos
3. **Chat Rápido**: Interacción directa con IA
4. **Notificaciones**: Alertas del sistema
5. **Configuración**: Personalización del asistente

## 📁 **Estructura del Proyecto**

```
asistente-virtual/
├── src/
│   ├── main/                 # Proceso principal Electron
│   │   ├── main.js          # Punto de entrada
│   │   ├── tray.js          # Icono en bandeja
│   │   └── window.js        # Gestión de ventanas
│   ├── renderer/            # Proceso renderer
│   │   ├── components/      # Componentes React/Vue
│   │   │   ├── FloatingAssistant.vue
│   │   │   ├── AdvicePanel.vue
│   │   │   ├── QuickChat.vue
│   │   │   └── NotificationCenter.vue
│   │   ├── services/        # Servicios
│   │   │   ├── api.js       # Comunicación con backend
│   │   │   ├── advice.js    # Gestión de consejos
│   │   │   └── system.js    # APIs del sistema
│   │   └── store/           # Estado de la aplicación
│   ├── shared/              # Código compartido
│   │   ├── config.js        # Configuración
│   │   └── utils.js         # Utilidades
│   └── preload.js           # Preload script
├── public/
│   ├── icons/               # Iconos de la aplicación
│   └── sounds/              # Sonidos de notificaciones
├── dist/                    # Archivos compilados
├── package.json
├── electron-builder.json    # Configuración de empaquetado
└── README.md
```

## 🚀 **Funcionalidades Principales**

### **1. Ventana Flotante Siempre Visible**
```javascript
// main.js - Ventana principal flotante
const createFloatingWindow = () => {
  const mainWindow = new BrowserWindow({
    width: 350,
    height: 500,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    movable: true,
    transparent: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Posicionar en esquina superior derecha
  const { screen } = require('electron');
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  mainWindow.setPosition(width - 370, 50);
  mainWindow.loadFile('src/renderer/index.html');

  return mainWindow;
};
```

### **2. Comunicación en Tiempo Real**
```javascript
// services/api.js
class APIClient {
  constructor() {
    this.baseURL = 'http://localhost:8000/api';
    this.token = localStorage.getItem('auth_token');
  }

  // Consejos proactivos
  async getProactiveAdvice() {
    const response = await fetch(`${this.baseURL}/consejos-proactivos/`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }

  // Enviar mensaje al chat
  async sendMessage(message) {
    const response = await fetch(`${this.baseURL}/asistente/chat/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ mensaje: message })
    });
    return response.json();
  }
}
```

### **3. Detección de Aplicaciones Activas**
```javascript
// services/system.js
const activeWin = require('active-win');

class SystemMonitor {
  constructor() {
    this.currentApp = null;
    this.checkInterval = null;
  }

  startMonitoring() {
    this.checkInterval = setInterval(async () => {
      try {
        const activeWindow = await activeWin();
        if (activeWindow && activeWindow.owner.name !== this.currentApp) {
          this.currentApp = activeWindow.owner.name;
          this.onAppChanged(activeWindow);
        }
      } catch (error) {
        console.error('Error detecting active window:', error);
      }
    }, 5000); // Verificar cada 5 segundos
  }

  onAppChanged(windowInfo) {
    // Notificar al backend sobre cambio de aplicación
    this.sendAppChange(windowInfo);
  }

  async sendAppChange(windowInfo) {
    // Enviar información al backend para análisis contextual
    const api = new APIClient();
    await api.sendActivity({
      ventana_activa: windowInfo.title,
      aplicacion: windowInfo.owner.name,
      timestamp: new Date().toISOString()
    });
  }
}
```

### **4. Notificaciones Inteligentes**
```javascript
// components/NotificationCenter.vue
<template>
  <div class="notification-center">
    <transition-group name="notification" tag="div" class="notifications">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification-item"
        :class="notification.type"
      >
        <div class="notification-icon">
          <i :class="getIconClass(notification.type)"></i>
        </div>
        <div class="notification-content">
          <h4>{{ notification.title }}</h4>
          <p>{{ notification.message }}</p>
        </div>
        <button @click="dismiss(notification.id)" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script>
export default {
  data() {
    return {
      notifications: []
    }
  },
  methods: {
    showNotification(notification) {
      const id = Date.now();
      this.notifications.push({
        id,
        ...notification
      });

      // Auto-ocultar después de 10 segundos
      setTimeout(() => {
        this.dismiss(id);
      }, 10000);
    },

    dismiss(id) {
      const index = this.notifications.findIndex(n => n.id === id);
      if (index > -1) {
        this.notifications.splice(index, 1);
      }
    },

    getIconClass(type) {
      const icons = {
        advice: 'fas fa-lightbulb',
        warning: 'fas fa-exclamation-triangle',
        success: 'fas fa-check-circle',
        error: 'fas fa-times-circle'
      };
      return icons[type] || 'fas fa-info-circle';
    }
  }
}
</script>
```

### **5. Chat Rápido Integrado**
```javascript
// components/QuickChat.vue
<template>
  <div class="quick-chat" :class="{ expanded: isExpanded }">
    <div class="chat-toggle" @click="toggleChat">
      <i class="fas fa-comments"></i>
      <span class="notification-badge" v-if="unreadCount > 0">
        {{ unreadCount }}
      </span>
    </div>

    <div class="chat-window" v-if="isExpanded">
      <div class="chat-header">
        <h4>Asistente IA</h4>
        <button @click="toggleChat" class="minimize-btn">
          <i class="fas fa-minus"></i>
        </button>
      </div>

      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="message in messages"
          :key="message.id"
          class="message"
          :class="{ 'user-message': message.isUser }"
        >
          <div class="message-content">
            {{ message.text }}
          </div>
          <div class="message-time">
            {{ formatTime(message.timestamp) }}
          </div>
        </div>
      </div>

      <div class="chat-input">
        <input
          v-model="newMessage"
          @keyup.enter="sendMessage"
          placeholder="Pregunta algo..."
          ref="messageInput"
        >
        <button @click="sendMessage" :disabled="!newMessage.trim()">
          <i class="fas fa-paper-plane"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isExpanded: false,
      messages: [],
      newMessage: '',
      unreadCount: 0
    }
  },
  methods: {
    toggleChat() {
      this.isExpanded = !this.isExpanded;
      if (this.isExpanded) {
        this.unreadCount = 0;
        this.$nextTick(() => {
          this.$refs.messageInput.focus();
          this.scrollToBottom();
        });
      }
    },

    async sendMessage() {
      if (!this.newMessage.trim()) return;

      const userMessage = {
        id: Date.now(),
        text: this.newMessage,
        isUser: true,
        timestamp: new Date()
      };

      this.messages.push(userMessage);
      const messageToSend = this.newMessage;
      this.newMessage = '';

      this.scrollToBottom();

      try {
        const api = new APIClient();
        const response = await api.sendMessage(messageToSend);

        const aiMessage = {
          id: Date.now() + 1,
          text: response.respuesta,
          isUser: false,
          timestamp: new Date()
        };

        this.messages.push(aiMessage);
        this.scrollToBottom();
      } catch (error) {
        console.error('Error sending message:', error);
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        if (this.$refs.messagesContainer) {
          this.$refs.messagesContainer.scrollTop =
            this.$refs.messagesContainer.scrollHeight;
        }
      });
    },

    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
}
</script>
```

## 🎨 **Interfaz de Usuario**

### **Diseño de la Ventana Flotante**
- **Tamaño compacto**: 350x500 píxeles
- **Siempre visible**: Opción always-on-top
- **Transparente**: Fondo semi-transparente
- **Arrastrable**: Se puede mover por la pantalla
- **Minimizable**: Se puede colapsar a un icono pequeño

### **Estados del Asistente**
1. **Compacto**: Solo icono flotante
2. **Expandido**: Panel completo visible
3. **Chat activo**: Conversación abierta
4. **Notificación**: Mostrando consejo importante

## 🔧 **Configuración y Personalización**

### **Archivo de Configuración**
```javascript
// shared/config.js
const config = {
  // Apariencia
  theme: 'dark', // 'light', 'dark', 'auto'
  opacity: 0.9,
  position: { x: 'right', y: 50 },

  // Comportamiento
  autoStart: true,
  showNotifications: true,
  proactiveAdvice: true,
  adviceInterval: 120000, // 2 minutos

  // Notificaciones
  notificationSound: true,
  notificationDuration: 10000,

  // API
  apiUrl: 'http://localhost:8000/api',
  reconnectInterval: 5000
};

export default config;
```

## 📦 **Empaquetado y Distribución**

### **Electron Builder Configuration**
```json
// electron-builder.json
{
  "appId": "com.sara.asistente-virtual",
  "productName": "SARA Asistente Virtual",
  "directories": {
    "output": "dist"
  },
  "files": [
    "dist/**/*",
    "node_modules/**/*",
    "package.json"
  ],
  "mac": {
    "category": "public.app-category.productivity"
  },
  "win": {
    "target": "nsis",
    "icon": "public/icons/icon.ico"
  },
  "linux": {
    "target": "AppImage",
    "icon": "public/icons/icon.png"
  },
  "nsis": {
    "oneClick": false,
    "perMachine": false,
    "allowToChangeInstallationDirectory": true
  }
}
```

## 🚀 **Implementación Paso a Paso**

### **Paso 1: Configuración del Proyecto**
```bash
# Crear proyecto Electron
npm init -y
npm install electron electron-builder concurrently wait-on

# Instalar dependencias adicionales
npm install active-win node-notifier axios electron-store
npm install vue vue-router vuex --save-dev
```

### **Paso 2: Estructura Básica**
```javascript
// main.js
const { app, BrowserWindow, Tray, Menu } = require('electron');
const path = require('path');

let mainWindow;
let tray;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 350,
    height: 500,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    },
    show: false,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true
  });

  mainWindow.loadFile('src/renderer/index.html');

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
}

function createTray() {
  tray = new Tray(path.join(__dirname, 'assets/tray-icon.png'));

  const contextMenu = Menu.buildFromTemplate([
    { label: 'Mostrar Asistente', click: () => mainWindow.show() },
    { label: 'Ocultar Asistente', click: () => mainWindow.hide() },
    { type: 'separator' },
    { label: 'Salir', click: () => app.quit() }
  ]);

  tray.setToolTip('SARA Asistente Virtual');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
  });
}

app.whenReady().then(() => {
  createWindow();
  createTray();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
```

### **Paso 3: Interfaz React/Vue**
```vue
<!-- FloatingAssistant.vue -->
<template>
  <div class="floating-assistant" :style="windowStyle">
    <!-- Header arrastrable -->
    <div class="assistant-header" @mousedown="startDrag">
      <div class="assistant-title">
        <i class="fas fa-robot"></i>
        SARA IA
      </div>
      <div class="assistant-controls">
        <button @click="minimize" class="control-btn">
          <i class="fas fa-minus"></i>
        </button>
        <button @click="close" class="control-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="assistant-content">
      <!-- Panel de consejos -->
      <AdvicePanel
        :advice="currentAdvice"
        @dismiss="dismissAdvice"
      />

      <!-- Chat rápido -->
      <QuickChat
        :isVisible="chatVisible"
        @toggle="toggleChat"
      />

      <!-- Centro de notificaciones -->
      <NotificationCenter
        :notifications="notifications"
        @dismiss="dismissNotification"
      />
    </div>
  </div>
</template>

<script>
import AdvicePanel from './AdvicePanel.vue';
import QuickChat from './QuickChat.vue';
import NotificationCenter from './NotificationCenter.vue';

export default {
  components: {
    AdvicePanel,
    QuickChat,
    NotificationCenter
  },

  data() {
    return {
      chatVisible: false,
      currentAdvice: null,
      notifications: [],
      isDragging: false,
      dragOffset: { x: 0, y: 0 }
    }
  },

  computed: {
    windowStyle() {
      return {
        left: `${this.position.x}px`,
        top: `${this.position.y}px`
      };
    }
  },

  mounted() {
    this.loadPosition();
    this.startAdvicePolling();
    this.setupEventListeners();
  },

  methods: {
    startDrag(event) {
      this.isDragging = true;
      const rect = this.$el.getBoundingClientRect();
      this.dragOffset.x = event.clientX - rect.left;
      this.dragOffset.y = event.clientY - rect.top;

      document.addEventListener('mousemove', this.onDrag);
      document.addEventListener('mouseup', this.stopDrag);
    },

    onDrag(event) {
      if (!this.isDragging) return;

      const newX = event.clientX - this.dragOffset.x;
      const newY = event.clientY - this.dragOffset.y;

      this.position.x = Math.max(0, Math.min(window.innerWidth - 350, newX));
      this.position.y = Math.max(0, Math.min(window.innerHeight - 500, newY));
    },

    stopDrag() {
      this.isDragging = false;
      this.savePosition();
      document.removeEventListener('mousemove', this.onDrag);
      document.removeEventListener('mouseup', this.stopDrag);
    },

    minimize() {
      // Minimizar a icono pequeño
      this.$el.classList.add('minimized');
    },

    close() {
      // Ocultar ventana (no cerrar aplicación)
      this.$el.style.display = 'none';
    },

    toggleChat() {
      this.chatVisible = !this.chatVisible;
    },

    async startAdvicePolling() {
      setInterval(async () => {
        try {
          const advice = await this.fetchAdvice();
          if (advice) {
            this.showAdvice(advice);
          }
        } catch (error) {
          console.error('Error fetching advice:', error);
        }
      }, 120000); // Cada 2 minutos
    },

    async fetchAdvice() {
      // Llamar a la API de consejos proactivos
      const response = await fetch('/api/consejos-proactivos/');
      const data = await response.json();
      return data.consejos;
    },

    showAdvice(advice) {
      this.currentAdvice = advice;
      this.showNotification({
        type: 'advice',
        title: 'Consejo de SARA',
        message: advice.substring(0, 100) + '...'
      });
    },

    dismissAdvice() {
      this.currentAdvice = null;
    },

    showNotification(notification) {
      this.notifications.push({
        id: Date.now(),
        ...notification
      });
    },

    dismissNotification(id) {
      this.notifications = this.notifications.filter(n => n.id !== id);
    },

    loadPosition() {
      const saved = localStorage.getItem('assistant-position');
      if (saved) {
        this.position = JSON.parse(saved);
      } else {
        // Posición por defecto: esquina superior derecha
        this.position = {
          x: window.innerWidth - 370,
          y: 50
        };
      }
    },

    savePosition() {
      localStorage.setItem('assistant-position', JSON.stringify(this.position));
    },

    setupEventListeners() {
      // Escuchar eventos del sistema
      window.electronAPI.onAdvice((advice) => {
        this.showAdvice(advice);
      });

      window.electronAPI.onNotification((notification) => {
        this.showNotification(notification);
      });
    }
  }
}
</script>

<style scoped>
.floating-assistant {
  position: fixed;
  width: 350px;
  height: 500px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  z-index: 9999;
  overflow: hidden;
  transition: all 0.3s ease;
}

.floating-assistant.minimized {
  width: 60px;
  height: 60px;
  border-radius: 50%;
}

.assistant-header {
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 15px;
  cursor: move;
  user-select: none;
}

.assistant-title {
  font-weight: 600;
  font-size: 14px;
}

.assistant-controls {
  display: flex;
  gap: 5px;
}

.control-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 5px;
  border-radius: 3px;
  transition: background 0.2s;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.assistant-content {
  height: calc(100% - 40px);
  overflow-y: auto;
}

/* Animaciones */
@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.floating-assistant {
  animation: slideIn 0.3s ease-out;
}
</style>
```

## 🎯 **Características Avanzadas**

### **1. Modo Inteligente**
- **Detección de inactividad**: Sugerencias cuando el usuario está inactivo
- **Análisis de patrones**: Aprende hábitos del usuario
- **Adaptación contextual**: Cambia consejos según la aplicación activa

### **2. Integración con Sistema**
- **Notificaciones nativas**: Alertas del sistema operativo
- **Accesos directos**: Teclas rápidas para activar el asistente
- **Modo oscuro**: Adaptación automática al tema del sistema

### **3. Personalización Avanzada**
- **Temas personalizables**: Colores, transparencias, tamaños
- **Comandos de voz**: Activación por voz (opcional)
- **Widgets personalizados**: Consejos específicos por aplicación

## 📋 **Próximos Pasos de Implementación**

1. **Configurar proyecto Electron básico**
2. **Implementar ventana flotante principal**
3. **Crear sistema de consejos proactivos**
4. **Desarrollar interfaz de chat rápido**
5. **Implementar notificaciones del sistema**
6. **Agregar detección de aplicaciones activas**
7. **Empaquetar y distribuir**

¿Te gustaría que comience a implementar alguna parte específica del asistente virtual flotante?