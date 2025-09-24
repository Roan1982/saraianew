# SARA - Sistema de Productividad Proactiva

SARA es un sistema avanzado de monitoreo y análisis de productividad que combina un servidor web Django con un cliente de escritorio Electron para monitoreo proactivo de la actividad del usuario.

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)
```batch
# Ejecuta todo: servidor + cliente
run_server.bat
```

### Opción 2: Manual
```batch
# 1. Instalar dependencias del servidor
pip install -r requirements.txt
python manage.py migrate

# 2. Instalar dependencias del cliente
install-client.bat

# 3. Ejecutar servidor
python manage.py runserver

# 4. Ejecutar cliente (en otra terminal)
run-client.bat
```

## 📊 Características

### Servidor Web (Django)
- **Dashboard administrativo** con métricas en tiempo real
- **Gestión completa de usuarios** (admin/supervisor/empleado)
- **Análisis IA automático** de patrones de error
- **API REST** para comunicación con cliente de escritorio
- **Estadísticas detalladas** de productividad

### Cliente de Escritorio (Electron)
- **Monitoreo en tiempo real** cada 5 segundos
- **Clasificación automática** de aplicaciones (productivo/no productivo/juegos)
- **Análisis proactivo** con sugerencias inteligentes
- **Dashboard visual** con gráficos y métricas
- **Bandeja del sistema** para control discreto

## 🎯 Funcionalidades de IA Proactiva

### Análisis Automático
- Detección de patrones de improductividad
- Alertas de tiempo excesivo en aplicaciones distractivas
- Recordatorios de pausas durante horas laborales
- Análisis de fatiga basado en patrones de uso

### Sugerencias Inteligentes
- Recomendaciones personalizadas basadas en comportamiento
- Consejos para mejorar la concentración
- Alertas de horarios de trabajo vs ocio

## 🔧 Arquitectura Técnica

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   Cliente       │◄──────────────►│   Servidor      │
│   Electron      │                 │   Django        │
│                 │                 │                 │
│ • Monitoreo     │                 │ • API REST      │
│ • UI/UX         │                 │ • Base de datos │
│ • Gráficos      │                 │ • IA            │
└─────────────────┘                 └─────────────────┘
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│   Sistema       │                 │   Base de       │
│   Operativo     │                 │   Datos         │
│                 │                 │   SQLite        │
│ • Procesos      │                 │                 │
│ • Ventanas      │                 │ • Actividad     │
│ • CPU/Memoria   │                 │ • Usuarios      │
└─────────────────┘                 └─────────────────┘
```

## 📁 Estructura del Proyecto

```
saraianew/
├── .venv/                    # Entorno virtual Python
├── nodejs-portable/          # Node.js local
├── core/                     # Aplicación Django principal
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Lógica de negocio
│   ├── templates/           # Plantillas HTML
│   └── ia_module.py         # Módulo de IA básico
├── sara-monitor/            # Cliente Electron
│   ├── main.js             # Proceso principal
│   ├── renderer.js         # Interfaz de usuario
│   ├── index.html          # UI principal
│   └── package.json        # Dependencias Node.js
├── run_server.bat          # Script de inicio completo
├── install-client.bat       # Instalar cliente
├── run-client.bat          # Ejecutar cliente
└── requirements.txt         # Dependencias Python
```

## 🔒 Privacidad y Seguridad

- **Datos locales**: Toda la información se almacena localmente
- **No envío externo**: Los datos solo van del cliente al servidor local
- **Anonimización**: No se capturan contenidos específicos de aplicaciones
- **Control total**: El usuario puede detener el monitoreo en cualquier momento

## 🎮 Uso del Sistema

### Para Administradores
1. Gestionar usuarios y permisos
2. Ver análisis de productividad de todo el equipo
3. Configurar políticas de monitoreo

### Para Supervisores
1. Monitorear equipos asignados
2. Ver métricas de productividad
3. Recibir alertas de bajo rendimiento

### Para Empleados
1. Ver su propio dashboard de productividad
2. Recibir sugerencias de mejora
3. Gestionar sus registros de trabajo

## 🚀 Próximas Funcionalidades

- [ ] Captura de screenshots para análisis visual
- [ ] Detección avanzada de errores en aplicaciones
- [ ] Machine learning predictivo
- [ ] Integración con calendarios
- [ ] Reportes avanzados de productividad

## 📞 Soporte

Para soporte técnico contactar al equipo de desarrollo de SARA.

---

**Desarrollado con ❤️ para mejorar la productividad humana**