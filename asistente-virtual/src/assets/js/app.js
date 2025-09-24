class SaraAsistenteVirtual {
  constructor() {
    this.config = null;
    this.isAuthenticated = false;
    this.user = null;
    this.currentAdvice = null;
    this.chatMessages = [];
    this.isDragging = false;
    this.dragOffset = { x: 0, y: 0 };
    this.isMinimized = false;

    this.init();
  }

  async init() {
    await this.loadConfig();
    this.setupEventListeners();
    this.setupWindowControls();
    this.checkAuthentication();

    // Configurar listeners de Electron
    this.setupElectronListeners();

    // Actualizar estado inicial
    this.updateUI();
  }

  async loadConfig() {
    try {
      this.config = await window.electronAPI.getConfig();
    } catch (error) {
      console.error('Error cargando configuración:', error);
      this.config = {
        theme: 'light',
        opacity: 0.9,
        showNotifications: true,
        proactiveAdvice: true
      };
    }
  }

  setupEventListeners() {
    // Login
    const loginBtn = document.getElementById('login-btn');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    loginBtn.addEventListener('click', () => this.handleLogin());
    passwordInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.handleLogin();
      }
    });

    // Chat
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');

    messageInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.sendMessage();
      }
    });

    sendBtn.addEventListener('click', () => this.sendMessage());

    // Toggle chat
    const toggleChatBtn = document.getElementById('toggle-chat-btn');
    toggleChatBtn.addEventListener('click', () => this.toggleChat());

    // Logout
    const logoutBtn = document.getElementById('logout-btn');
    logoutBtn.addEventListener('click', () => this.handleLogout());
  }

  setupWindowControls() {
    const header = document.getElementById('assistant-header');
    const minimizeBtn = document.getElementById('minimize-btn');
    const closeBtn = document.getElementById('close-btn');

    // Drag functionality
    header.addEventListener('mousedown', (e) => this.startDrag(e));
    document.addEventListener('mousemove', (e) => this.onDrag(e));
    document.addEventListener('mouseup', () => this.stopDrag());

    // Window controls
    minimizeBtn.addEventListener('click', () => this.minimize());
    closeBtn.addEventListener('click', () => this.close());
  }

  setupElectronListeners() {
    // Escuchar consejos proactivos
    window.electronAPI.onProactiveAdvice((advice) => {
      this.showAdvice(advice, 'info');
    });

    // Escuchar consejos contextuales
    window.electronAPI.onContextualAdvice((advice) => {
      this.showAdvice(advice, 'success');
    });

    // Escuchar notificaciones
    window.electronAPI.onNotification((notification) => {
      this.showNotification(notification);
    });
  }

  startDrag(event) {
    if (this.isMinimized) return;

    this.isDragging = true;
    const assistant = document.getElementById('assistant');
    const rect = assistant.getBoundingClientRect();

    this.dragOffset.x = event.clientX - rect.left;
    this.dragOffset.y = event.clientY - rect.top;

    assistant.style.cursor = 'grabbing';
  }

  onDrag(event) {
    if (!this.isDragging || this.isMinimized) return;

    const assistant = document.getElementById('assistant');
    const newX = event.clientX - this.dragOffset.x;
    const newY = event.clientY - this.dragOffset.y;

    // Limitar a los bordes de la pantalla
    const maxX = window.innerWidth - assistant.offsetWidth;
    const maxY = window.innerHeight - assistant.offsetHeight;

    const clampedX = Math.max(0, Math.min(maxX, newX));
    const clampedY = Math.max(0, Math.min(maxY, newY));

    assistant.style.left = `${clampedX}px`;
    assistant.style.top = `${clampedY}px`;
  }

  stopDrag() {
    if (!this.isDragging) return;

    this.isDragging = false;
    const assistant = document.getElementById('assistant');
    assistant.style.cursor = 'default';

    // Guardar nueva posición
    this.savePosition();
  }

  async savePosition() {
    const assistant = document.getElementById('assistant');
    const rect = assistant.getBoundingClientRect();

    const newConfig = {
      ...this.config,
      position: { x: rect.left, y: rect.top }
    };

    try {
      await window.electronAPI.setConfig(newConfig);
      this.config = newConfig;
    } catch (error) {
      console.error('Error guardando posición:', error);
    }
  }

  minimize() {
    const assistant = document.getElementById('assistant');
    this.isMinimized = !this.isMinimized;

    if (this.isMinimized) {
      assistant.classList.add('minimized');
    } else {
      assistant.classList.remove('minimized');
    }
  }

  close() {
    window.electronAPI.closeWindow();
  }

  async handleLogin() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('login-btn');
    const statusDiv = document.getElementById('login-status');

    if (!username || !password) {
      this.showStatus('Por favor complete todos los campos', 'error');
      return;
    }

    // Deshabilitar botón durante login
    loginBtn.disabled = true;
    loginBtn.textContent = 'Conectando...';
    this.showStatus('Conectando...', 'info');

    try {
      const result = await window.electronAPI.login({ username, password });

      if (result.success) {
        this.isAuthenticated = true;
        this.user = result.user;
        this.showMainScreen();
        this.showStatus('¡Conectado exitosamente!', 'success');

        // Mostrar notificación de bienvenida
        setTimeout(() => {
          this.showAdvice('¡Bienvenido! El monitoreo está activo y funcionando. Usa el botón "Salir" para cambiar de usuario.', 'success');
        }, 1000);

      } else {
        this.showStatus(result.error || 'Error de autenticación', 'error');
      }
    } catch (error) {
      console.error('Error en login:', error);
      this.showStatus('Error de conexión', 'error');
    } finally {
      loginBtn.disabled = false;
      loginBtn.textContent = 'Conectar';
    }
  }

  async handleLogout() {
    try {
      // Llamar a la API de logout
      await window.electronAPI.logout();

      // Limpiar estado local
      this.isAuthenticated = false;
      this.user = null;
      this.chatMessages = [];

      // Limpiar inputs de login
      document.getElementById('username').value = '';
      document.getElementById('password').value = '';

      // Mostrar pantalla de login
      this.showLoginScreen();

      // Mostrar mensaje de despedida
      this.showStatus('Sesión cerrada. Puedes iniciar sesión con otro usuario.', 'info');

    } catch (error) {
      console.error('Error en logout:', error);
      // Forzar logout local aunque falle la API
      this.isAuthenticated = false;
      this.user = null;
      this.chatMessages = [];
      this.showLoginScreen();
      this.showStatus('Sesión cerrada localmente.', 'info');
    }
  }

  showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('login-status');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;

    // Auto-ocultar mensajes de éxito después de 3 segundos
    if (type === 'success') {
      setTimeout(() => {
        statusDiv.textContent = '';
        statusDiv.className = 'status-message';
      }, 3000);
    }
  }

  showMainScreen() {
    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('main-screen').classList.add('active');
    this.updateConnectionStatus();
  }

  showLoginScreen() {
    document.getElementById('main-screen').classList.remove('active');
    document.getElementById('login-screen').classList.add('active');

    // Asegurar que el botón de logout esté oculto
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
      logoutBtn.style.display = 'none';
    }
  }

  async sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();

    if (!message) return;

    // Agregar mensaje del usuario
    this.addMessage(message, 'user');
    messageInput.value = '';

    try {
      const response = await window.electronAPI.sendMessage(message);

      if (response.respuesta) {
        this.addMessage(response.respuesta, 'assistant');
      } else if (response.error) {
        this.addMessage(`Error: ${response.error}`, 'assistant');
      }
    } catch (error) {
      console.error('Error enviando mensaje:', error);
      this.addMessage('Error de conexión. Inténtalo de nuevo.', 'assistant');
    }
  }

  addMessage(text, type) {
    const message = {
      id: Date.now(),
      text: text,
      type: type,
      timestamp: new Date()
    };

    this.chatMessages.push(message);
    this.renderMessages();

    // Auto-scroll al final
    const messagesContainer = document.getElementById('chat-messages');
    setTimeout(() => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
  }

  renderMessages() {
    const container = document.getElementById('chat-messages');
    container.innerHTML = '';

    this.chatMessages.slice(-10).forEach(message => { // Mostrar últimas 10 mensajes
      const messageDiv = document.createElement('div');
      messageDiv.className = `message ${message.type}`;

      messageDiv.innerHTML = `
        <div class="message-content">${this.escapeHtml(message.text)}</div>
        <div class="message-time">${window.utils.formatTime(message.timestamp)}</div>
      `;

      container.appendChild(messageDiv);
    });
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  toggleChat() {
    const chatContent = document.getElementById('chat-content');
    const toggleBtn = document.getElementById('toggle-chat-btn');
    const icon = toggleBtn.querySelector('i');

    chatContent.classList.toggle('collapsed');
    icon.classList.toggle('rotated');
  }

  showAdvice(advice, type = 'info') {
    const container = document.getElementById('advice-content');

    // Limpiar consejos anteriores
    container.innerHTML = '';

    const adviceDiv = document.createElement('div');
    adviceDiv.className = `advice-item ${type} fade-in`;

    adviceDiv.innerHTML = `
      <div class="advice-content">${this.escapeHtml(advice)}</div>
    `;

    container.appendChild(adviceDiv);

    // Auto-ocultar después de 30 segundos
    setTimeout(() => {
      adviceDiv.classList.remove('fade-in');
      adviceDiv.style.opacity = '0';
      setTimeout(() => {
        if (container.contains(adviceDiv)) {
          container.innerHTML = '<div class="no-advice"><i class="fas fa-brain"></i><p>Esperando consejos...</p></div>';
        }
      }, 300);
    }, 30000);
  }

  showNotification(notification) {
    // Crear notificación visual en la interfaz
    const notificationDiv = document.createElement('div');
    notificationDiv.className = 'notification-toast fade-in';
    notificationDiv.innerHTML = `
      <div class="notification-icon">
        <i class="fas fa-bell"></i>
      </div>
      <div class="notification-content">
        <div class="notification-title">${notification.title}</div>
        <div class="notification-message">${notification.message}</div>
      </div>
      <button class="notification-close" onclick="this.parentElement.remove()">
        <i class="fas fa-times"></i>
      </button>
    `;

    document.body.appendChild(notificationDiv);

    // Auto-remover después de 5 segundos
    setTimeout(() => {
      if (document.body.contains(notificationDiv)) {
        notificationDiv.remove();
      }
    }, 5000);
  }

  updateConnectionStatus() {
    const statusIcon = document.getElementById('connection-status');
    const statusText = document.getElementById('connection-text');
    const logoutBtn = document.getElementById('logout-btn');

    if (this.isAuthenticated) {
      statusIcon.className = 'fas fa-circle connected';
      statusText.textContent = 'Conectado - Monitoreo Activo';
      logoutBtn.style.display = 'inline-block';
    } else {
      statusIcon.className = 'fas fa-circle disconnected';
      statusText.textContent = 'Desconectado';
      logoutBtn.style.display = 'none';
    }
  }

  checkAuthentication() {
    // Verificar si ya hay una sesión activa
    if (this.config && this.config.authToken) {
      // Intentar reconectar automáticamente
      this.attemptReconnect();
    }
  }

  async attemptReconnect() {
    try {
      // Verificar si el token aún es válido
      const advice = await window.electronAPI.getProactiveAdvice();
      if (advice !== null) {
        this.isAuthenticated = true;
        this.showMainScreen();
      } else {
        // Token inválido, mostrar login
        this.showLoginScreen();
      }
    } catch (error) {
      console.error('Error reconectando:', error);
      this.showLoginScreen();
    }
  }

  updateUI() {
    // Aplicar tema
    if (this.config && this.config.theme === 'dark') {
      document.body.classList.add('dark-theme');
    }

    // Aplicar opacidad
    if (this.config && this.config.opacity) {
      const assistant = document.getElementById('assistant');
      assistant.style.opacity = this.config.opacity;
    }

    this.updateConnectionStatus();
  }
}

// Notificaciones toast
const style = document.createElement('style');
style.textContent = `
  .notification-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    padding: 15px;
    max-width: 300px;
    z-index: 1000;
    border-left: 4px solid #667eea;
    display: flex;
    align-items: flex-start;
    gap: 10px;
  }

  .notification-icon {
    color: #667eea;
    font-size: 18px;
    margin-top: 2px;
  }

  .notification-content {
    flex: 1;
  }

  .notification-title {
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 5px;
  }

  .notification-message {
    font-size: 13px;
    color: #666;
    line-height: 1.4;
  }

  .notification-close {
    background: none;
    border: none;
    color: #999;
    cursor: pointer;
    padding: 2px;
    border-radius: 3px;
  }

  .notification-close:hover {
    background: #f0f0f0;
    color: #666;
  }
`;
document.head.appendChild(style);

// Iniciar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  new SaraAsistenteVirtual();
});