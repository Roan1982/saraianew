# Especificaciones para Cliente de Monitoreo SARA

## 📋 Requisitos del Sistema

### ✅ Auto-inicio del Monitoreo
El cliente debe iniciar automáticamente el monitoreo cuando el usuario hace login exitosamente.

**Implementación requerida:**
1. Al recibir respuesta exitosa de `/api/login/`, verificar el campo `auto_start: true`
2. Iniciar automáticamente el monitoreo de actividad sin intervención del usuario
3. Mostrar mensaje: "Monitoreo iniciado automáticamente. Solo puedes detenerlo con logout."

### ❌ Eliminación de Opción de Pausa
**NO debe existir** ninguna opción para pausar/detener el monitoreo durante la sesión activa.

**Restricciones:**
- No mostrar botones de "Pausar", "Detener", o "Suspender"
- No permitir atajos de teclado para pausar
- El monitoreo debe ser **continuo e ininterrumpido**
- Solo el **logout** puede detener el monitoreo

### 🔄 Ciclo de Vida del Monitoreo

```
Usuario hace Login → Cliente recibe auto_start=true → Monitoreo inicia automáticamente
                                                                    ↓
Monitoreo continuo (sin opción de pausa) ────────────────────────────┘
                                                                    ↓
Solo Logout detiene el monitoreo ←───────────────────────────────────┘
```

## 🚀 API Endpoints

### POST `/api/login/`
**Request:**
```json
{
    "username": "usuario",
    "password": "contraseña",
    "auto_start": true
}
```

**Response (éxito):**
```json
{
    "user": {
        "id": 1,
        "username": "usuario",
        "first_name": "Nombre",
        "last_name": "Apellido",
        "email": "usuario@email.com",
        "rol": "empleado"
    },
    "auto_start": true,
    "monitoring_enabled": true,
    "message": "Monitoreo iniciado automáticamente. Solo puedes detenerlo con logout."
}
```

### GET `/api/consejos-proactivos/`
**Headers:** `Authorization: Bearer <token>` o sesión activa

**Response:**
```json
{
    "consejos": "⏰ Llevas tiempo considerable en Excel. ¿Necesitas ayuda con alguna fórmula específica? | 💡 Prueba la Técnica Pomodoro: 25 min trabajo + 5 min descanso",
    "timestamp": "2025-09-23T13:45:00.000Z",
    "tipo": "proactivo"
}
```

## 📊 Funcionalidades del Asistente Proactivo

### 🎯 Consejos Contextuales
El asistente analiza la actividad del usuario y proporciona consejos relevantes:

- **Tiempo prolongado en aplicación**: Sugerencias de descanso, mejores prácticas
- **Patrones de productividad**: Alertas sobre baja productividad, técnicas de mejora
- **Horarios del día**: Recordatorios de comidas, finales de jornada
- **Aplicaciones específicas**: Consejos para Excel, navegación web, desarrollo, etc.

### ⏱️ Frecuencia de Consejos
- **Cada 2 minutos** desde el dashboard web
- **Cada actividad registrada** desde el cliente (análisis automático)
- **Prevención de duplicados**: No repetir consejos similares en intervalos cortos

## 🔧 Implementación Técnica

### Cliente de Escritorio (Electron/Node.js)
```javascript
// Ejemplo de implementación
async function login(username, password) {
    try {
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, auto_start: true })
        });

        const data = await response.json();

        if (data.auto_start && data.monitoring_enabled) {
            // Iniciar monitoreo automáticamente
            startMonitoring();
            showMessage(data.message);

            // Configurar que solo logout detiene el monitoreo
            disablePauseOptions();
        }
    } catch (error) {
        console.error('Error en login:', error);
    }
}

function startMonitoring() {
    // Iniciar captura de actividad
    // Enviar datos cada 30 segundos
    // NO permitir pausar
}

function disablePauseOptions() {
    // Ocultar/deshabilitar todos los controles de pausa
    // Solo logout puede detener
}
```

### 📱 Notificaciones del Asistente
- Mostrar notificaciones del sistema cuando hay consejos importantes
- Integrar con notificaciones nativas del SO
- Permitir que el usuario responda directamente desde la notificación

## 🎨 Interfaz de Usuario

### Dashboard Web
- **Sección "Asistente IA Proactivo"**: Muestra consejos en tiempo real
- **Actualización automática**: Cada 2 minutos
- **Enlace al chat**: Botón para conversación completa

### Cliente de Escritorio
- **Sin controles de pausa**: Interfaz limpia y minimalista
- **Indicador de estado**: "Monitoreo activo - Logout para detener"
- **Notificaciones inteligentes**: Solo cuando hay consejos relevantes

## 🔒 Seguridad y Privacidad

### Control de Acceso
- Monitoreo solo para usuarios autenticados
- Datos encriptados en tránsito
- Almacenamiento seguro de credenciales

### Transparencia
- Usuario siempre sabe que está siendo monitoreado
- Opción clara de logout en cualquier momento
- No hay monitoreo oculto o en segundo plano sin sesión activa

## 📈 Métricas y Monitoreo

### KPIs del Sistema
- **Tasa de actividad**: Porcentaje de tiempo productivo
- **Frecuencia de consejos**: Consejos útiles vs spam
- **Engagement del usuario**: Uso del chat del asistente
- **Satisfacción**: Feedback sobre consejos proporcionados

### Logs del Sistema
- Registro de inicio/fin de sesiones
- Timestamp de cada consejo enviado
- Métricas de uso del asistente

---

## 🚀 Próximos Pasos

1. **Implementar auto-inicio** en el cliente de escritorio
2. **Eliminar controles de pausa** de la interfaz
3. **Probar integración** con las nuevas APIs
4. **Implementar notificaciones** del asistente
5. **Recopilar feedback** de usuarios para mejorar consejos