// renderer.js - Lógica del frontend para SARA Monitor

let activityHistory = [];
let timeChart = null;
let startTime = Date.now();
let currentUser = null;

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    initializeCharts();
    showLoginScreen();
});

// Inicializar aplicación
function initializeApp() {
    console.log('SARA Monitor inicializado');
    console.log('Versiones:', window.versions);

    // Actualizar tiempo inicial
    updateTimeDisplay();
}

// Configurar event listeners
function setupEventListeners() {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);

    // Botones de control (solo después del login)
    document.getElementById('startBtn').addEventListener('click', startMonitoring);
    document.getElementById('stopBtn').addEventListener('click', stopMonitoring);
    document.getElementById('getSuggestionsBtn').addEventListener('click', getAISuggestions);

    // Listener para actualizaciones de actividad
    window.electronAPI.onActivityUpdate((activity) => {
        handleActivityUpdate(activity);
    });
}

// Inicializar gráficos
function initializeCharts() {
    const ctx = document.getElementById('timeChart').getContext('2d');

    timeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Productivo', 'No Productivo', 'Juegos', 'Neutral'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: [
                    '#28a745', // Productivo
                    '#dc3545', // No productivo
                    '#ffc107', // Juegos
                    '#6c757d'  // Neutral
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Iniciar monitoreo
async function startMonitoring() {
    try {
        const result = await window.electronAPI.startMonitoring();
        if (result.success) {
            showNotification('Monitoreo iniciado', 'success');
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
        }
    } catch (error) {
        console.error('Error al iniciar monitoreo:', error);
        showNotification('Error al iniciar monitoreo', 'error');
    }
}

// Detener monitoreo
async function stopMonitoring() {
    try {
        const result = await window.electronAPI.stopMonitoring();
        if (result.success) {
            showNotification('Monitoreo detenido', 'warning');
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        }
    } catch (error) {
        console.error('Error al detener monitoreo:', error);
        showNotification('Error al detener monitoreo', 'error');
    }
}

// Manejar actualización de actividad
function handleActivityUpdate(activity) {
    console.log('Nueva actividad:', activity);

    // Agregar a historial
    activityHistory.unshift(activity);
    if (activityHistory.length > 50) {
        activityHistory = activityHistory.slice(0, 50);
    }

    // Actualizar UI
    updateCurrentActivity(activity);
    updateActivityHistory();
    updateCharts();
    updateMetrics();

    // Verificar si necesita sugerencias
    checkForSuggestions(activity);
}

// Actualizar actividad actual
function updateCurrentActivity(activity) {
    document.getElementById('currentWindow').textContent = activity.activeWindow;

    const indicator = document.getElementById('productivityIndicator');
    const status = document.getElementById('productivityStatus');

    // Limpiar clases anteriores
    indicator.className = 'productivity-indicator';

    // Agregar clase según productividad
    indicator.classList.add(activity.productivity);

    // Actualizar texto
    const statusTexts = {
        'productive': 'Productivo',
        'unproductive': 'No Productivo',
        'gaming': 'Jugando',
        'neutral': 'Neutral'
    };

    status.textContent = statusTexts[activity.productivity] || 'Analizando...';

    // Actualizar procesos
    updateTopProcesses(activity.topProcesses);
}

// Actualizar lista de procesos
function updateTopProcesses(processes) {
    const container = document.getElementById('topProcesses');

    if (!processes || processes.length === 0) {
        container.innerHTML = '<div class="text-muted">No se detectaron procesos activos</div>';
        return;
    }

    const html = processes.map(process => `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span>${process.name}</span>
            <div>
                <small class="text-primary">CPU: ${process.cpu}%</small>
                <small class="text-info ms-2">MEM: ${process.memory}%</small>
            </div>
        </div>
    `).join('');

    container.innerHTML = html;
}

// Actualizar historial de actividad
function updateActivityHistory() {
    const container = document.getElementById('activityHistory');

    if (activityHistory.length === 0) {
        container.innerHTML = '<div class="text-center text-muted"><i class="fas fa-list"></i> No hay actividad registrada aún</div>';
        return;
    }

    const html = activityHistory.slice(0, 10).map(activity => {
        const time = moment(activity.timestamp).format('HH:mm:ss');
        const productivityClass = `productivity-indicator ${activity.productivity}`;

        return `
            <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                <div>
                    <span class="${productivityClass}"></span>
                    <strong>${activity.activeWindow}</strong>
                </div>
                <small class="text-muted">${time}</small>
            </div>
        `;
    }).join('');

    container.innerHTML = html;
}

// Actualizar gráficos
function updateCharts() {
    if (!timeChart) return;

    // Calcular distribución de tiempo
    const distribution = {
        productive: 0,
        unproductive: 0,
        gaming: 0,
        neutral: 0
    };

    activityHistory.forEach(activity => {
        distribution[activity.productivity] = (distribution[activity.productivity] || 0) + 1;
    });

    timeChart.data.datasets[0].data = [
        distribution.productive,
        distribution.unproductive,
        distribution.gaming,
        distribution.neutral
    ];

    timeChart.update();
}

// Actualizar métricas
function updateMetrics() {
    // Tiempo hoy
    updateTimeDisplay();

    // Productividad (basado en distribución)
    const productiveCount = activityHistory.filter(a => a.productivity === 'productive').length;
    const totalCount = activityHistory.length;
    const productivityPercent = totalCount > 0 ? Math.round((productiveCount / totalCount) * 100) : 0;

    document.getElementById('productivityScore').textContent = `${productivityPercent}%`;

    // Apps activas
    const uniqueApps = new Set(activityHistory.map(a => a.activeWindow)).size;
    document.getElementById('activeApps').textContent = uniqueApps;

    // Sugerencias (simulado)
    document.getElementById('suggestions').textContent = Math.floor(Math.random() * 5);
}

// Actualizar display de tiempo
function updateTimeDisplay() {
    const elapsed = Date.now() - startTime;
    const hours = Math.floor(elapsed / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);

    document.getElementById('timeToday').textContent =
        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// Verificar si necesita sugerencias
function checkForSuggestions(activity) {
    // Lógica simple para sugerencias automáticas
    if (activity.productivity === 'unproductive' && activityHistory.filter(a => a.productivity === 'unproductive').length > 5) {
        showAISuggestion('Has estado mucho tiempo en aplicaciones no productivas. ¿Quieres establecer un límite de tiempo?');
    }

    if (activity.productivity === 'gaming' && new Date().getHours() < 18) {
        showAISuggestion('Es hora laboral. ¿Quieres pausar el monitoreo durante el trabajo?');
    }
}

// Obtener sugerencias de IA
function getAISuggestions() {
    const suggestions = [
        'Considera tomar un descanso de 5 minutos cada hora para mantener la concentración.',
        'Has estado alternando entre muchas aplicaciones. Intenta enfocarte en una tarea a la vez.',
        'Tu tiempo productivo ha bajado. ¿Quieres que te ayude a crear un horario de trabajo?',
        'Detecté patrones de fatiga. ¿Quieres que te recuerde hacer pausas activas?',
        'Excelente productividad hoy. ¿Quieres mantener este ritmo?'
    ];

    const randomSuggestion = suggestions[Math.floor(Math.random() * suggestions.length)];
    showAISuggestion(randomSuggestion);
}

// Mostrar sugerencia de IA
function showAISuggestion(suggestion) {
    const container = document.getElementById('aiSuggestions');

    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        <i class="fas fa-lightbulb me-2"></i>
        ${suggestion}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    container.appendChild(alert);

    // Auto-remover después de 10 segundos
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 10000);
}

// Actualizaciones en tiempo real
function startRealTimeUpdates() {
    setInterval(() => {
        updateTimeDisplay();
    }, 1000);
}

// Mostrar notificaciones en UI
function showNotification(message, type = 'info') {
    // Crear toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(toast);

    // Auto-remover
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

// Mostrar pantalla de login
function showLoginScreen() {
    document.getElementById('loginScreen').style.display = 'flex';
    document.getElementById('mainDashboard').style.display = 'none';
}

// Mostrar dashboard principal
function showMainDashboard() {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('mainDashboard').style.display = 'block';
    startRealTimeUpdates();
}

// Manejar login
async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('loginBtn');
    const loginMessage = document.getElementById('loginMessage');

    // Deshabilitar botón y mostrar loading
    loginBtn.disabled = true;
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Iniciando sesión...';

    try {
        const result = await window.electronAPI.loginUser({ username, password });

        if (result.success) {
            currentUser = result.user;
            showMainDashboard();
            showNotification('¡Bienvenido!', `Sesión iniciada como ${currentUser.username}`);
        } else {
            showLoginMessage(result.error || 'Error de autenticación', 'danger');
        }
    } catch (error) {
        showLoginMessage('Error de conexión con el servidor', 'danger');
    } finally {
        // Restaurar botón
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Iniciar Sesión';
    }
}

// Mostrar mensaje en pantalla de login
function showLoginMessage(message, type = 'info') {
    const loginMessage = document.getElementById('loginMessage');
    loginMessage.style.display = 'block';
    loginMessage.className = `alert alert-${type}`;
    loginMessage.textContent = message;

    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        loginMessage.style.display = 'none';
    }, 5000);
}

// Cleanup al cerrar
window.addEventListener('beforeunload', () => {
    window.electronAPI.removeAllListeners('activity-update');
});