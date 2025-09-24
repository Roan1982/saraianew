# SARA Asistente Virtual

Un asistente inteligente flotante que monitorea tu actividad y proporciona consejos contextuales en tiempo real.

## Características

- **Interfaz flotante**: Siempre visible sin interferir con tu trabajo
- **Monitoreo inteligente**: Detecta aplicaciones activas y proporciona consejos relevantes
- **Chat integrado**: Comunicación directa con la IA
- **Consejos proactivos**: Sugerencias automáticas basadas en tu actividad
- **Notificaciones del sistema**: Alertas importantes sin interrumpir el flujo de trabajo
- **Modo oscuro**: Interfaz adaptable a tus preferencias

## Requisitos del Sistema

- Windows 10/11, macOS 10.14+, o Linux
- Node.js 16+ (para desarrollo)
- Conexión a internet para funcionalidades de IA

## Instalación

### Prerrequisitos

Antes de instalar el asistente virtual, necesitas tener Node.js instalado en tu sistema.

**Instalación de Node.js:**
- Ve a [nodejs.org](https://nodejs.org/)
- Descarga la versión LTS (Recomendada para la mayoría de usuarios)
- Ejecuta el instalador y sigue las instrucciones
- Reinicia tu terminal/PowerShell después de la instalación

### Para Usuarios Finales

1. **Descarga el proyecto:**
   ```bash
   git clone [url-del-repo]
   cd asistente-virtual
   ```

2. **Ejecuta el instalador automático:**
   - **Windows (CMD):** `install.bat`
   - **Windows (PowerShell):** `.\install.ps1`
   - **Linux/Mac:** `./install.sh` (si existe)

3. **Inicia la aplicación:**
   ```bash
   npm start
   ```

### Para Desarrolladores

```bash
# Clonar el repositorio
git clone [url-del-repo]
cd asistente-virtual

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo (con hot reload)
npm run dev

# Construir para producción
npm run build

# Crear instaladores
npm run dist
```

### Instaladores Pre-construidos

Para usuarios que no quieren instalar Node.js, proporcionamos instaladores pre-construidos:

- **Windows:** `SARA-Asistente-Virtual-Setup-1.0.0.exe`
- **macOS:** `SARA-Asistente-Virtual-1.0.0.dmg`
- **Linux:** `SARA-Asistente-Virtual-1.0.0.AppImage`

## Uso

### Primer Inicio

1. Al abrir la aplicación, verás la pantalla de login
2. Ingresa tus credenciales de SARA
3. Una vez conectado, el asistente comenzará a monitorear automáticamente

### Funcionalidades Principales

#### Consejos Proactivos
- El asistente analiza tu actividad actual
- Proporciona sugerencias relevantes automáticamente
- Los consejos aparecen en el panel superior

#### Chat Rápido
- Haz clic en el botón de chat para expandir
- Escribe preguntas o solicita ayuda
- El asistente responde de manera contextual

#### Personalización
- Arrastra la ventana para reposicionarla
- Minimiza cuando no necesites consejos inmediatos
- Configura notificaciones y temas desde el menú

## Configuración

### Archivo de Configuración

El asistente guarda su configuración en:
- **Windows**: `%APPDATA%\sara-assistant\config.json`
- **macOS**: `~/Library/Application Support/sara-assistant/config.json`
- **Linux**: `~/.config/sara-assistant/config.json`

### Opciones Disponibles

```json
{
  "theme": "light|dark",
  "opacity": 0.8,
  "showNotifications": true,
  "proactiveAdvice": true,
  "position": {
    "x": 100,
    "y": 100
  }
}
```

## Desarrollo

### Arquitectura

```
asistente-virtual/
├── src/
│   ├── main/           # Proceso principal de Electron
│   │   └── main.js
│   ├── preload/        # Puente seguro IPC
│   │   └── preload.js
│   ├── renderer/       # Interfaz de usuario
│   │   ├── index.html
│   │   └── assets/
│   │       ├── css/
│   │       ├── js/
│   │       └── icons/
│   └── shared/         # Código compartido
├── package.json
└── build/             # Archivos de construcción
```

### Scripts Disponibles

```bash
npm run dev          # Desarrollo con hot reload
npm run build        # Construir aplicación
npm run dist         # Crear instaladores
npm run lint         # Verificar código
npm test            # Ejecutar pruebas
```

### Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## API Integration

El asistente se conecta con la API REST de SARA para:

- **Autenticación**: `/api/auth/login`
- **Chat**: `/api/chat/message`
- **Consejos**: `/api/advice/proactive`
- **Monitoreo**: `/api/monitoring/context`

## Seguridad

- Comunicación segura con la API mediante HTTPS
- Almacenamiento local encriptado de tokens
- Validación de entrada en todas las interfaces
- Actualizaciones automáticas de seguridad

## Solución de Problemas

### Problemas Comunes

**La aplicación no se conecta**
- Verifica tu conexión a internet
- Confirma que las credenciales sean correctas
- Revisa los logs en la consola de desarrollo

**No aparecen consejos**
- Asegúrate de que el monitoreo esté activo
- Verifica los permisos de la aplicación
- Reinicia la aplicación

**La ventana no responde**
- Cierra y vuelve a abrir la aplicación
- Verifica que no haya otras instancias ejecutándose

### Logs de Depuración

Para habilitar logs detallados:
1. Abre la aplicación
2. Presiona `Ctrl+Shift+I` (o `Cmd+Option+I` en Mac)
3. Ve a la pestaña Console

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

- **Documentación**: [enlace a docs]
- **Issues**: [enlace a issues]
- **Email**: soporte@sara-ai.com

---

**Versión**: 1.0.0
**Última actualización**: Diciembre 2024</content>
<parameter name="filePath">c:\Users\angel.steklein\Documents\desarrollo\saraianew\asistente-virtual\README.md