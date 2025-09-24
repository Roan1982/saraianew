const { SaraAsistenteVirtual } = require('../src/assets/js/app');

describe('SaraAsistenteVirtual', () => {
  let assistant;
  let mockElectronAPI;

  beforeEach(() => {
    // Limpiar el DOM
    document.body.innerHTML = `
      <div id="app">
        <div class="floating-assistant" id="assistant">
          <div class="assistant-header" id="assistant-header">
            <div class="assistant-title">
              <i class="fas fa-robot"></i>
              <span>SARA IA</span>
            </div>
            <div class="assistant-controls">
              <button id="minimize-btn" class="control-btn">
                <i class="fas fa-minus"></i>
              </button>
              <button id="close-btn" class="control-btn">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
          <div class="assistant-content">
            <div id="login-screen" class="screen active">
              <div class="login-form">
                <h3>Iniciar Sesión</h3>
                <div class="form-group">
                  <input type="text" id="username" placeholder="Usuario">
                </div>
                <div class="form-group">
                  <input type="password" id="password" placeholder="Contraseña">
                </div>
                <button id="login-btn" class="btn btn-primary">Conectar</button>
                <div id="login-status" class="status-message"></div>
              </div>
            </div>
            <div id="main-screen" class="screen">
              <div class="advice-panel" id="advice-panel">
                <div class="panel-header">
                  <h4><i class="fas fa-lightbulb"></i> Consejos</h4>
                </div>
                <div id="advice-content" class="panel-content">
                  <div class="no-advice">
                    <i class="fas fa-brain"></i>
                    <p>Esperando consejos...</p>
                  </div>
                </div>
              </div>
              <div class="chat-panel" id="chat-panel">
                <div class="panel-header">
                  <h4><i class="fas fa-comments"></i> Chat Rápido</h4>
                  <button id="toggle-chat-btn" class="toggle-btn">
                    <i class="fas fa-chevron-down"></i>
                  </button>
                </div>
                <div id="chat-content" class="panel-content collapsed">
                  <div id="chat-messages" class="chat-messages"></div>
                  <div class="chat-input">
                    <input type="text" id="message-input" placeholder="Pregunta algo..." maxlength="200">
                    <button id="send-btn" class="btn btn-sm">
                      <i class="fas fa-paper-plane"></i>
                    </button>
                  </div>
                </div>
              </div>
              <div class="status-panel">
                <div class="status-item">
                  <i class="fas fa-circle" id="connection-status"></i>
                  <span id="connection-text">Desconectado</span>
                </div>
                <div class="status-item">
                  <i class="fas fa-eye"></i>
                  <span id="current-app">Sin monitoreo</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Mock de electronAPI
    mockElectronAPI = {
      getConfig: jest.fn().mockResolvedValue({
        theme: 'light',
        opacity: 0.9,
        showNotifications: true,
        proactiveAdvice: true
      }),
      login: jest.fn(),
      sendMessage: jest.fn(),
      getProactiveAdvice: jest.fn(),
      setConfig: jest.fn(),
      closeWindow: jest.fn(),
      onProactiveAdvice: jest.fn(),
      onContextualAdvice: jest.fn(),
      onNotification: jest.fn()
    };

    window.electronAPI = mockElectronAPI;

    // Crear instancia del asistente
    assistant = new SaraAsistenteVirtual();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Inicialización', () => {
    test('debería inicializar correctamente', async () => {
      await flushPromises();

      expect(mockElectronAPI.getConfig).toHaveBeenCalled();
      expect(assistant.config).toBeDefined();
      expect(assistant.isAuthenticated).toBe(false);
    });

    test('debería cargar configuración por defecto si falla la carga', async () => {
      mockElectronAPI.getConfig.mockRejectedValue(new Error('Config error'));

      const newAssistant = new SaraAsistenteVirtual();
      await flushPromises();

      expect(newAssistant.config.theme).toBe('light');
      expect(newAssistant.config.opacity).toBe(0.9);
    });
  });

  describe('Autenticación', () => {
    test('debería manejar login exitoso', async () => {
      mockElectronAPI.login.mockResolvedValue({
        success: true,
        user: { username: 'testuser' }
      });

      // Simular entrada de usuario
      document.getElementById('username').value = 'testuser';
      document.getElementById('password').value = 'password123';

      // Ejecutar login
      await assistant.handleLogin();
      await flushPromises();

      expect(mockElectronAPI.login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123'
      });
      expect(assistant.isAuthenticated).toBe(true);
      expect(assistant.user.username).toBe('testuser');
    });

    test('debería manejar login fallido', async () => {
      mockElectronAPI.login.mockResolvedValue({
        success: false,
        error: 'Credenciales inválidas'
      });

      document.getElementById('username').value = 'wronguser';
      document.getElementById('password').value = 'wrongpass';

      await assistant.handleLogin();
      await flushPromises();

      expect(assistant.isAuthenticated).toBe(false);
      expect(document.getElementById('login-status').textContent).toContain('Credenciales inválidas');
    });

    test('debería validar campos requeridos', async () => {
      // Campos vacíos
      document.getElementById('username').value = '';
      document.getElementById('password').value = '';

      await assistant.handleLogin();

      expect(mockElectronAPI.login).not.toHaveBeenCalled();
      expect(document.getElementById('login-status').textContent).toContain('complete todos los campos');
    });
  });

  describe('Chat', () => {
    beforeEach(async () => {
      // Simular usuario autenticado
      assistant.isAuthenticated = true;
      assistant.showMainScreen();
      await flushPromises();
    });

    test('debería enviar mensaje correctamente', async () => {
      mockElectronAPI.sendMessage.mockResolvedValue({
        respuesta: 'Hola, ¿en qué puedo ayudarte?'
      });

      const messageInput = document.getElementById('message-input');
      messageInput.value = 'Hola SARA';

      await assistant.sendMessage();
      await flushPromises();

      expect(mockElectronAPI.sendMessage).toHaveBeenCalledWith('Hola SARA');
      expect(assistant.chatMessages).toHaveLength(2); // Usuario + respuesta
    });

    test('debería manejar mensajes vacíos', async () => {
      const messageInput = document.getElementById('message-input');
      messageInput.value = '';

      await assistant.sendMessage();

      expect(mockElectronAPI.sendMessage).not.toHaveBeenCalled();
    });
  });

  describe('Consejos', () => {
    test('debería mostrar consejos proactivos', () => {
      const advice = 'Considera revisar tu código antes de commitear';

      assistant.showAdvice(advice, 'info');

      const adviceContent = document.getElementById('advice-content');
      expect(adviceContent.innerHTML).toContain(advice);
      expect(adviceContent.innerHTML).toContain('advice-item');
    });

    test('debería mostrar diferentes tipos de consejos', () => {
      assistant.showAdvice('¡Bienvenido!', 'success');

      const adviceItem = document.querySelector('.advice-item');
      expect(adviceItem.classList.contains('success')).toBe(true);
    });
  });

  describe('Interfaz de Usuario', () => {
    test('debería alternar pantalla de login a principal', () => {
      assistant.showMainScreen();

      expect(document.getElementById('login-screen').classList.contains('active')).toBe(false);
      expect(document.getElementById('main-screen').classList.contains('active')).toBe(true);
    });

    test('debería actualizar estado de conexión', () => {
      assistant.isAuthenticated = true;
      assistant.updateConnectionStatus();

      const statusIcon = document.getElementById('connection-status');
      const statusText = document.getElementById('connection-text');

      expect(statusIcon.classList.contains('connected')).toBe(true);
      expect(statusText.textContent).toBe('Conectado');
    });

    test('debería alternar chat', () => {
      const chatContent = document.getElementById('chat-content');
      const toggleBtn = document.getElementById('toggle-chat-btn');

      expect(chatContent.classList.contains('collapsed')).toBe(true);

      assistant.toggleChat();

      expect(chatContent.classList.contains('collapsed')).toBe(false);
      expect(toggleBtn.querySelector('i').classList.contains('rotated')).toBe(true);
    });
  });

  describe('Utilidades', () => {
    test('debería formatear tiempo correctamente', () => {
      const now = new Date();
      const recent = new Date(now.getTime() - 300000); // 5 minutos atrás

      const formatted = window.utils.formatTime(recent);
      expect(formatted).toContain('min');
    });

    test('debería validar emails', () => {
      expect(window.utils.isValidEmail('test@example.com')).toBe(true);
      expect(window.utils.isValidEmail('invalid-email')).toBe(false);
    });

    test('debería generar IDs únicos', () => {
      const id1 = window.utils.generateId();
      const id2 = window.utils.generateId();

      expect(id1).not.toBe(id2);
      expect(typeof id1).toBe('string');
    });

    test('debería truncar texto', () => {
      const longText = 'Este es un texto muy largo que debería ser truncado';
      const truncated = window.utils.truncateText(longText, 20);

      expect(truncated.length).toBeLessThan(longText.length);
      expect(truncated.endsWith('...')).toBe(true);
    });
  });
});