// Utilidades para el Asistente Virtual Sara

const utils = {
  // Formatear tiempo para mensajes
  formatTime: (date) => {
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) { // Menos de 1 minuto
      return 'Ahora';
    } else if (diff < 3600000) { // Menos de 1 hora
      const minutes = Math.floor(diff / 60000);
      return `Hace ${minutes} min`;
    } else if (diff < 86400000) { // Menos de 1 día
      const hours = Math.floor(diff / 3600000);
      return `Hace ${hours} h`;
    } else {
      return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  },

  // Validar email
  isValidEmail: (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // Sanitizar texto para HTML
  sanitizeHtml: (text) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },

  // Generar ID único
  generateId: () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  },

  // Debounce para optimizar llamadas
  debounce: (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Throttle para optimizar llamadas frecuentes
  throttle: (func, limit) => {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  // Detectar si estamos en modo desarrollo
  isDevelopment: () => {
    return process.env.NODE_ENV === 'development' || !process.env.NODE_ENV;
  },

  // Obtener información del sistema operativo
  getOS: () => {
    const userAgent = navigator.userAgent;
    if (userAgent.indexOf('Windows') !== -1) return 'Windows';
    if (userAgent.indexOf('Mac') !== -1) return 'macOS';
    if (userAgent.indexOf('Linux') !== -1) return 'Linux';
    return 'Unknown';
  },

  // Calcular distancia entre dos puntos (para drag)
  getDistance: (x1, y1, x2, y2) => {
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
  },

  // Animar elemento con CSS transitions
  animateElement: (element, properties, duration = 300) => {
    return new Promise((resolve) => {
      element.style.transition = `all ${duration}ms ease`;

      Object.keys(properties).forEach(prop => {
        element.style[prop] = properties[prop];
      });

      setTimeout(() => {
        element.style.transition = '';
        resolve();
      }, duration);
    });
  },

  // Crear notificación del sistema
  showSystemNotification: (title, body, icon = null) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body: body,
        icon: icon || '/assets/icons/sara-icon.png'
      });
    }
  },

  // Solicitar permisos de notificación
  requestNotificationPermission: async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    return false;
  },

  // Copiar texto al portapapeles
  copyToClipboard: async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      // Fallback para navegadores antiguos
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        document.body.removeChild(textArea);
        return true;
      } catch (fallbackErr) {
        document.body.removeChild(textArea);
        return false;
      }
    }
  },

  // Formatear números con separadores
  formatNumber: (num, locale = 'es-ES') => {
    return new Intl.NumberFormat(locale).format(num);
  },

  // Capitalizar primera letra
  capitalize: (str) => {
    return str.charAt(0).toUpperCase() + str.slice(1);
  },

  // Truncar texto con ellipsis
  truncateText: (text, maxLength) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
  },

  // Obtener parámetros de URL
  getUrlParams: (url = window.location.href) => {
    const params = {};
    const urlObj = new URL(url);
    for (let [key, value] of urlObj.searchParams) {
      params[key] = value;
    }
    return params;
  },

  // Validar contraseña (mínimo 8 caracteres, al menos una mayúscula, minúscula y número)
  validatePassword: (password) => {
    const minLength = password.length >= 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);

    return {
      isValid: minLength && hasUpperCase && hasLowerCase && hasNumbers,
      errors: {
        minLength: !minLength,
        hasUpperCase: !hasUpperCase,
        hasLowerCase: !hasLowerCase,
        hasNumbers: !hasNumbers
      }
    };
  },

  // Generar colores aleatorios
  getRandomColor: () => {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  },

  // Detectar si el dispositivo es móvil
  isMobile: () => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  },

  // Obtener tamaño de la ventana
  getWindowSize: () => {
    return {
      width: window.innerWidth,
      height: window.innerHeight
    };
  },

  // Escuchar cambios de tamaño de ventana con debounce
  onWindowResize: (callback, debounceMs = 250) => {
    const debouncedCallback = utils.debounce(callback, debounceMs);
    window.addEventListener('resize', debouncedCallback);
    return () => window.removeEventListener('resize', debouncedCallback);
  },

  // Crear elemento DOM con atributos
  createElement: (tag, attributes = {}, textContent = '') => {
    const element = document.createElement(tag);

    Object.keys(attributes).forEach(attr => {
      if (attr === 'className') {
        element.className = attributes[attr];
      } else if (attr === 'style' && typeof attributes[attr] === 'object') {
        Object.assign(element.style, attributes[attr]);
      } else {
        element.setAttribute(attr, attributes[attr]);
      }
    });

    if (textContent) {
      element.textContent = textContent;
    }

    return element;
  },

  // Agregar múltiples event listeners
  addEventListeners: (element, events) => {
    Object.keys(events).forEach(event => {
      element.addEventListener(event, events[event]);
    });
  },

  // Remover múltiples event listeners
  removeEventListeners: (element, events) => {
    Object.keys(events).forEach(event => {
      element.removeEventListener(event, events[event]);
    });
  }
};

// Exponer utilidades globalmente
window.utils = utils;