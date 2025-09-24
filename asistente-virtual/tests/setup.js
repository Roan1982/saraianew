// Setup para pruebas con Jest
// Este archivo se ejecuta antes de cada suite de pruebas

// Mock de Electron
global.electron = {
  ipcRenderer: {
    invoke: jest.fn(),
    on: jest.fn(),
    removeListener: jest.fn(),
    send: jest.fn()
  }
};

// Mock de window.electronAPI
Object.defineProperty(window, 'electronAPI', {
  value: {
    login: jest.fn(),
    sendMessage: jest.fn(),
    getProactiveAdvice: jest.fn(),
    getConfig: jest.fn(),
    setConfig: jest.fn(),
    closeWindow: jest.fn(),
    onProactiveAdvice: jest.fn(),
    onContextualAdvice: jest.fn(),
    onNotification: jest.fn()
  },
  writable: false
});

// Mock de window.utils
Object.defineProperty(window, 'utils', {
  value: {
    formatTime: jest.fn((date) => date.toLocaleTimeString()),
    isValidEmail: jest.fn((email) => email.includes('@')),
    sanitizeHtml: jest.fn((text) => text),
    generateId: jest.fn(() => Math.random().toString(36)),
    debounce: jest.fn((func) => func),
    throttle: jest.fn((func) => func),
    isDevelopment: jest.fn(() => true),
    getOS: jest.fn(() => 'Windows'),
    getDistance: jest.fn(() => 0),
    animateElement: jest.fn(() => Promise.resolve()),
    showSystemNotification: jest.fn(),
    requestNotificationPermission: jest.fn(() => Promise.resolve(true)),
    copyToClipboard: jest.fn(() => Promise.resolve(true)),
    formatNumber: jest.fn((num) => num.toString()),
    capitalize: jest.fn((str) => str.charAt(0).toUpperCase() + str.slice(1)),
    truncateText: jest.fn((text, max) => text.length > max ? text.substring(0, max) + '...' : text),
    getUrlParams: jest.fn(() => ({})),
    validatePassword: jest.fn(() => ({ isValid: true, errors: {} })),
    getRandomColor: jest.fn(() => '#000000'),
    isMobile: jest.fn(() => false),
    getWindowSize: jest.fn(() => ({ width: 1920, height: 1080 })),
    onWindowResize: jest.fn(() => () => {}),
    createElement: jest.fn((tag) => document.createElement(tag)),
    addEventListeners: jest.fn(),
    removeEventListeners: jest.fn()
  },
  writable: false
});

// Mock de Notification API
global.Notification = class {
  constructor(title, options = {}) {
    this.title = title;
    this.options = options;
  }

  static requestPermission() {
    return Promise.resolve('granted');
  }
};

// Mock de localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
global.localStorage = localStorageMock;

// Mock de fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
    ok: true,
    status: 200
  })
);

// Configuración global de Jest
beforeEach(() => {
  // Limpiar todos los mocks antes de cada prueba
  jest.clearAllMocks();

  // Resetear DOM
  document.body.innerHTML = '';
});

// Configuración de timeouts
jest.setTimeout(10000);

// Helper para esperar a que se resuelvan las promesas
global.flushPromises = () => new Promise(resolve => setImmediate(resolve));