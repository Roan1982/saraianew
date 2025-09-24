# SARA Asist## Inicio Rápido

### Iniciar el Sistema (Interfa### Interfaz Web (Recomendado - Sin Instalar Nada Local)
- **URL**: http://localhost:8000/asistente/
- **Ventajas**: Funciona en cualquier navegador moderno
- **No requiere**: Node.js, X11, VcXsrv, o instalación local
- **Funcionalidad completa**: Login, monitoreo, consejos, chat

### API REST (Para integraciones)
- **Backend**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/
- **API Docs**: Ver `CLIENTE_ESPECIFICACIONES.md``bash
# Windows con PowerShell
.\run-docker.ps1

# Windows con CMD
run-docker.bat

# Linux/Mac
docker-compose up --build -d
```Docker

# SARA Asistente Virtual - Docker

Esta aplicación contiene el backend Django con interfaz web completa empaquetado en contenedores Docker. **No requiere instalación de software adicional** - funciona directamente en el navegador.

## 🚀 Inicio Rápido

### Opción 1: Interfaz Web (Recomendado - Sin Instalar Nada Local)

```bash
# Windows con PowerShell
.\sara-docker.ps1 -Command start

# Windows con CMD
sara-docker.bat start

# Linux/Mac
docker-compose up -d backend
```

### Opción 2: Aplicación Electron (Solo Linux con GUI)

```bash
# Solo funciona en Linux con X11
docker-compose --profile linux-gui up electron
```

### Opción 3: Sistema Completo (Backend + Electron)

```bash
# Linux con GUI completa
docker-compose --profile linux-gui up -d
```

## 🎯 Acceso al Asistente Virtual

### Interfaz Web (Recomendado - Sin Instalar Nada Local)
- **URL**: http://localhost:8000/asistente/web/
- **Ventajas**: Funciona en cualquier navegador moderno
- **No requiere**: Node.js, X11, VcXsrv, o instalación local
- **Funcionalidad completa**: Login, monitoreo, consejos, chat

### Aplicación Electron (Solo Linux)
- **Ventajas**: Interfaz nativa de escritorio
- **Requiere**: Linux con X11 y display gráfico
- **Limitación**: No funciona en Windows/Mac dentro de Docker

### API REST (Para integraciones)
- **Backend**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/

## 🔐 Login del Cliente - Cómo Empezar el Monitoreo

### Paso 1: Iniciar la Aplicación
```bash
# Iniciar el sistema
run-docker.bat
```

### Paso 2: Acceder al Asistente Web
- **URL**: http://localhost:8000/asistente/
- **Abre en navegador**: Chrome, Firefox, Edge, Safari, etc.

### Paso 3: Hacer Login
1. **Ingresa tus credenciales**:
   - Usuario: Tu nombre de usuario de SARA
   - Contraseña: Tu contraseña

2. **Haz clic en "Iniciar Monitoreo"**

### Paso 4: Monitoreo Automático
**¡Automáticamente sucede!**
- ✅ **Monitoreo inicia** (cada 30 segundos)
- ✅ **Consejos proactivos** (cada 2 minutos)
- ✅ **Análisis de actividad** continuo
- ✅ **Estadísticas actualizadas**

### Paso 5: Usar el Asistente
- **💡 Consejos**: Aparecen automáticamente basados en tu actividad
- **💬 Chat**: Pregunta cualquier cosa al asistente IA
- **📊 Estado**: Verde = monitoreando, Rojo = desconectado
- **🚪 Salir**: Solo para cambiar de usuario

## Servicios

### Backend (Django)
- **Puerto**: 8000
- **Base de datos**: SQLite (persistente en `./db.sqlite3`)
- **Interfaz Web**: http://localhost:8000/asistente/web/
- **API Endpoints**:
  - `/api/health/` - Health check
  - `/api/login/` - Autenticación del cliente
  - `/api/asistente/chat/` - Chat con IA
  - `/api/consejos-proactivos/` - Consejos IA
  - `/admin/` - Panel administrativo

### Electron App (Solo Linux)
- **Dependencia**: Backend saludable
- **Interfaz**: Aplicación de escritorio nativa
- **Requisitos**: Linux con X11
- **Limitación**: No funciona en Windows/Mac dentro de Docker
- **Comando**: `docker-compose --profile linux-gui up electron`

## Comandos Útiles

```bash
# Usando los scripts de ayuda
.\sara-docker.ps1 -Command start          # Iniciar backend
.\sara-docker.ps1 -Command stop           # Detener servicios
.\sara-docker.ps1 -Command logs           # Ver logs
.\sara-docker.ps1 -Command status         # Ver estado
.\sara-docker.ps1 -Command clean          # Limpiar contenedores

# Comandos Docker directos
docker-compose up -d backend              # Solo backend
docker-compose --profile linux-gui up electron  # Solo Electron (Linux)
docker-compose --profile linux-gui up     # Sistema completo (Linux)

# Verificación y debugging
docker-compose ps                         # Estado de contenedores
docker-compose logs -f backend           # Logs del backend
curl http://localhost:8000/api/health/   # Health check

# Mantenimiento
docker-compose down                      # Detener servicios
docker-compose up --build --force-recreate  # Reconstruir
docker-compose exec backend bash         # Acceder al contenedor
```

## Solución de Problemas

### ❌ Error de conexión con backend
```bash
# Verificar backend saludable
docker-compose ps
curl http://localhost:8000/api/health/

# Ver logs del backend
docker-compose logs backend
```

### ❌ Cliente no puede hacer login
```bash
# Verificar credenciales en Django admin
# Ir a: http://localhost:8000/admin/

# Ver logs del backend
docker-compose logs backend
```

### ❌ Aplicación Electron no inicia (Linux)
```bash
# Verificar que X11 esté disponible
echo $DISPLAY

# Verificar que Xvfb esté corriendo
docker-compose logs electron

# Verificar dependencias del sistema
docker-compose exec electron apt list --installed | grep libgtk
```

### ❌ Problemas con la interfaz web
```bash
# Verificar que el navegador soporte JavaScript moderno
# Limpiar caché del navegador
# Intentar con un navegador diferente

# Verificar logs del backend
docker-compose logs backend
```

### ❌ Electron no puede conectar al backend
```bash
# Verificar que el backend esté saludable
curl http://localhost:8000/api/health/

# Verificar configuración de API_URL en Electron
docker-compose exec electron env | grep API_URL

# Verificar conectividad entre contenedores
docker-compose exec electron curl http://backend:8000/api/health/
```

## Arquitectura Completa

### Opción 1: Interfaz Web (Multiplataforma)
```
┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Django API    │
│  (Chrome/Firefox│    │   (Backend)     │
│   /Edge/Safari) │    │                 │
│                 │    │ • Autenticación │
│ • Login UI      │    │ • Consejos IA   │
│ • Monitoreo     │    │ • Chat IA       │
│ • Chat          │    │ • Estadísticas  │
│ • Notificaciones│    │ • Base de datos │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   System        │    │   SQLite DB     │
│   Monitoring    │    │   (Persistent)  │
│ (Backend APIs)  │    │                 │
└─────────────────┘    └─────────────────┘
```

### Opción 2: Aplicación Electron (Solo Linux)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Electron App   │◄──►│   Django API    │◄──►│   SQLite DB     │
│  (Linux Native) │    │   (Backend)     │    │   (Persistent)  │
│                 │    │                 │    │                 │
│ • Desktop GUI   │    │ • Autenticación │    │ • User Data     │
│ • System Tray   │    │ • Consejos IA   │    │ • Activity Logs │
│ • Notifications │    │ • Chat IA       │    │ • Statistics    │
│ • Auto-start    │    │ • Estadísticas  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│   System        │
│   Monitoring    │
│ (OS Integration)│
└─────────────────┘
```

## Características del Sistema

- ✅ **Monitoreo continuo** sin controles de pausa
- ✅ **Consejos IA proactivos** basados en actividad
- ✅ **Interfaz web moderna** accesible desde cualquier navegador
- ✅ **Login automático** inicia monitoreo
- ✅ **Logout único** para cambio de usuario
- ✅ **Contenedorizado** con Docker
- ✅ **Base de datos persistente**
- ✅ **Notificaciones del sistema**
- ✅ **Chat con IA** integrado
- ✅ **Sin instalación local** requerida