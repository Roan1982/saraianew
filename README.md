# SARA - Sistema de Asistencia y Registro Administrativo# SARA - Sistema de Productividad Proactiva



## 🚀 Descripción GeneralSARA es un sistema avanzado de monitoreo y análisis de productividad que combina un servidor web Django con un cliente de escritorio Electron para monitoreo proactivo de la actividad del usuario.



SARA es un sistema integral de asistencia administrativa inteligente que combina monitoreo de productividad, análisis de datos y un asistente IA avanzado. Diseñado para mejorar la eficiencia laboral mediante el seguimiento inteligente de actividades, análisis de rendimiento y recomendaciones personalizadas.## 🚀 Inicio Rápido



### ✨ Características Principales### Opción 1: Script Automático (Recomendado)

```batch

- 🤖 **Asistente IA Avanzado**: Respuestas inteligentes en 15+ categorías especializadas# Ejecuta todo: servidor + cliente

- 📊 **Monitoreo de Productividad**: Seguimiento automático de aplicaciones y tiempo productivorun_server.bat

- 📈 **Análisis de Rendimiento**: Métricas detalladas y reportes personalizados```

- 🔧 **Gestión de Errores**: Detección y corrección automática de problemas

- 👥 **Colaboración en Equipo**: Herramientas para trabajo grupal efectivo### Opción 2: Manual

- 🏥 **Bienestar Laboral**: Consejos de salud y prevención del burnout```batch

- 🎯 **Metas y Objetivos**: Seguimiento de logros y establecimiento de objetivos# 1. Instalar dependencias del servidor

pip install -r requirements.txt

## 🏗️ Arquitectura del Sistemapython manage.py migrate



### Tecnologías Utilizadas# 2. Instalar dependencias del cliente

install-client.bat

- **Backend**: Django REST Framework (Python)

- **Base de Datos**: PostgreSQL / SQLite# 3. Ejecutar servidor

- **Frontend**: HTML5, CSS3, JavaScriptpython manage.py runserver

- **Contenedorización**: Docker & Docker Compose

- **Autenticación**: JWT (JSON Web Tokens)# 4. Ejecutar cliente (en otra terminal)

- **API**: RESTful con documentación automáticarun-client.bat

```

### Componentes del Sistema

## 📊 Características

```

SARA/### Servidor Web (Django)

├── core/                    # Aplicación principal- **Dashboard administrativo** con métricas en tiempo real

│   ├── models.py           # Modelos de datos- **Gestión completa de usuarios** (admin/supervisor/empleado)

│   ├── views.py            # Lógica de negocio y APIs- **Análisis IA automático** de patrones de error

│   ├── serializers.py      # Serialización de datos- **API REST** para comunicación con cliente de escritorio

│   ├── urls.py            # Configuración de rutas- **Estadísticas detalladas** de productividad

│   └── templates/         # Plantillas HTML

├── sara/                   # Configuración del proyecto### Cliente de Escritorio (Electron)

│   ├── settings.py        # Configuración de Django- **Monitoreo en tiempo real** cada 5 segundos

│   ├── urls.py            # Rutas principales- **Clasificación automática** de aplicaciones (productivo/no productivo/juegos)

│   └── wsgi.py            # Configuración WSGI- **Análisis proactivo** con sugerencias inteligentes

├── tests.py               # Suite completa de tests- **Dashboard visual** con gráficos y métricas

├── docker-compose.yml     # Orquestación de contenedores- **Bandeja del sistema** para control discreto

├── Dockerfile.backend     # Configuración del contenedor backend

└── requirements.txt       # Dependencias Python## 🎯 Funcionalidades de IA Proactiva

```

### Análisis Automático

## 🚀 Instalación y Configuración- Detección de patrones de improductividad

- Alertas de tiempo excesivo en aplicaciones distractivas

### Prerrequisitos- Recordatorios de pausas durante horas laborales

- Análisis de fatiga basado en patrones de uso

- Docker y Docker Compose

- Python 3.8+ (opcional, para desarrollo local)### Sugerencias Inteligentes

- PostgreSQL (opcional, para producción)- Recomendaciones personalizadas basadas en comportamiento

- Consejos para mejorar la concentración

### Instalación con Docker (Recomendado)- Alertas de horarios de trabajo vs ocio



1. **Clonar el repositorio**## 🔧 Arquitectura Técnica

   ```bash

   git clone <url-del-repositorio>```

   cd sara┌─────────────────┐    HTTP/JSON    ┌─────────────────┐

   ```│   Cliente       │◄──────────────►│   Servidor      │

│   Electron      │                 │   Django        │

2. **Configurar variables de entorno**│                 │                 │                 │

   ```bash│ • Monitoreo     │                 │ • API REST      │

   cp .env.example .env│ • UI/UX         │                 │ • Base de datos │

   # Editar .env con tus configuraciones│ • Gráficos      │                 │ • IA            │

   ```└─────────────────┘                 └─────────────────┘

         │                                   │

3. **Levantar los servicios**         ▼                                   ▼

   ```bash┌─────────────────┐                 ┌─────────────────┐

   docker-compose up -d│   Sistema       │                 │   Base de       │

   ```│   Operativo     │                 │   Datos         │

│                 │                 │   SQLite        │

4. **Verificar instalación**│ • Procesos      │                 │                 │

   ```bash│ • Ventanas      │                 │ • Actividad     │

   docker-compose ps│ • CPU/Memoria   │                 │ • Usuarios      │

   ```└─────────────────┘                 └─────────────────┘

```

5. **Acceder a la aplicación**

   - Web: http://localhost:8000## 📁 Estructura del Proyecto

   - API: http://localhost:8000/api/

```

### Instalación para Desarrollo Localsaraianew/

├── .venv/                    # Entorno virtual Python

1. **Crear entorno virtual**├── nodejs-portable/          # Node.js local

   ```bash├── core/                     # Aplicación Django principal

   python -m venv venv│   ├── models.py            # Modelos de datos

   source venv/bin/activate  # Linux/Mac│   ├── views.py             # Lógica de negocio

   # o│   ├── templates/           # Plantillas HTML

   venv\Scripts\activate     # Windows│   └── ia_module.py         # Módulo de IA básico

   ```├── sara-monitor/            # Cliente Electron

│   ├── main.js             # Proceso principal

2. **Instalar dependencias**│   ├── renderer.js         # Interfaz de usuario

   ```bash│   ├── index.html          # UI principal

   pip install -r requirements.txt│   └── package.json        # Dependencias Node.js

   ```├── run_server.bat          # Script de inicio completo

├── install-client.bat       # Instalar cliente

3. **Configurar base de datos**├── run-client.bat          # Ejecutar cliente

   ```bash└── requirements.txt         # Dependencias Python

   python manage.py migrate```

   ```

## 🔒 Privacidad y Seguridad

4. **Crear superusuario**

   ```bash- **Datos locales**: Toda la información se almacena localmente

   python manage.py createsuperuser- **No envío externo**: Los datos solo van del cliente al servidor local

   ```- **Anonimización**: No se capturan contenidos específicos de aplicaciones

- **Control total**: El usuario puede detener el monitoreo en cualquier momento

5. **Ejecutar servidor**

   ```bash## 🎮 Uso del Sistema

   python manage.py runserver

   ```### Para Administradores

1. Gestionar usuarios y permisos

## 📖 Uso del Sistema2. Ver análisis de productividad de todo el equipo

3. Configurar políticas de monitoreo

### Primeros Pasos

### Para Supervisores

1. **Registro/Inicio de Sesión**1. Monitorear equipos asignados

   - Accede a http://localhost:80002. Ver métricas de productividad

   - Crea una cuenta o inicia sesión3. Recibir alertas de bajo rendimiento



2. **Configuración Inicial**### Para Empleados

   - Completa tu perfil de usuario1. Ver su propio dashboard de productividad

   - Configura preferencias de monitoreo2. Recibir sugerencias de mejora

   - Define tus objetivos laborales3. Gestionar sus registros de trabajo



3. **Exploración del Dashboard**## 🚀 Próximas Funcionalidades

   - Revisa métricas de productividad

   - Explora consejos del asistente IA- [ ] Captura de screenshots para análisis visual

   - Configura notificaciones- [ ] Detección avanzada de errores en aplicaciones

- [ ] Machine learning predictivo

### Funcionalidades Principales- [ ] Integración con calendarios

- [ ] Reportes avanzados de productividad

#### 🤖 Asistente IA

## 📞 Soporte

El asistente IA de SARA puede ayudarte con:

Para soporte técnico contactar al equipo de desarrollo de SARA.

- **Saludos y Presentación**: Interacciones naturales

- **Preguntas Personales**: Información sobre SARA---

- **Ayuda General**: Guía contextual

- **Productividad**: Consejos y técnicas**Desarrollado con ❤️ para mejorar la productividad humana**
- **Excel**: Fórmulas, funciones, mejores prácticas
- **Errores**: Diagnóstico y solución de problemas
- **Matemáticas**: Cálculos básicos
- **Ortografía**: Corrección y reglas
- **Documentación**: Manuales y guías
- **Configuración**: Setup y personalización
- **Reportes**: Análisis y estadísticas
- **Equipo**: Colaboración y trabajo grupal
- **Salud**: Bienestar y prevención
- **Metas**: Objetivos y seguimiento

**Ejemplos de uso:**
- "Hola SARA, ¿cómo estás?"
- "¿Cuáles son mis estadísticas de hoy?"
- "Ayuda con fórmulas de Excel"
- "¿Cómo mejorar mi productividad?"

#### 📊 Dashboard de Productividad

- **Métricas en Tiempo Real**: Seguimiento continuo de actividades
- **Análisis de Tendencias**: Gráficos de rendimiento por período
- **Alertas Inteligentes**: Notificaciones de bajo rendimiento
- **Consejos Proactivos**: Recomendaciones automáticas

#### 👥 Gestión de Equipo (Vista Admin)

- **Vista de Equipo**: Métricas agregadas de productividad
- **Monitoreo Individual**: Seguimiento de cada miembro
- **Reportes Grupales**: Análisis comparativo
- **Feedback Colectivo**: Sesiones de mejora grupal

## 🔧 API REST

### Endpoints Principales

#### Autenticación
```
POST /api/auth/login/          # Inicio de sesión
POST /api/auth/register/       # Registro de usuario
POST /api/auth/logout/         # Cierre de sesión
```

#### Asistente IA
```
GET  /api/asistente/chat/              # Vista del chat
POST /api/asistente/chat/              # Enviar mensaje al asistente
GET  /api/consejos-proactivos/        # Consejos automáticos
```

#### Dashboard
```
GET  /api/dashboard/                  # Dashboard principal
GET  /api/dashboard/admin/            # Dashboard administrativo
```

#### Registros y Datos
```
GET    /api/registros/                # Listar registros
POST   /api/registros/                # Crear registro
GET    /api/estadisticas/             # Estadísticas de usuario
GET    /api/actividad-usuario/        # Actividad del usuario
```

### Ejemplo de Uso de la API

```python
import requests

# Inicio de sesión
response = requests.post('http://localhost:8000/api/auth/login/', {
    'username': 'tu_usuario',
    'password': 'tu_password'
})

token = response.json()['token']

# Consulta al asistente IA
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:8000/api/asistente/chat/', {
    'mensaje': '¿Cómo mejorar mi productividad?'
}, headers=headers)

print(response.json()['respuesta'])
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Con Docker
docker-compose exec backend python manage.py test

# Desarrollo local
python manage.py test tests
```

### Cobertura de Tests

- ✅ **37 tests** implementados
- 🧠 **Análisis de Intención**: Tests para todas las categorías del asistente IA
- 🤖 **Funcionalidades IA**: Respuestas del asistente en diferentes contextos
- 📊 **Modelos de Datos**: Validación de creación y relaciones
- 🌐 **Vistas Web**: Acceso y permisos de usuarios
- 🔗 **Integración**: Flujos completos end-to-end

### Categorías de Tests

1. **TestAnalizarIntencionMensaje**: Análisis de intención de mensajes
2. **TestAsistenteIA**: Funcionalidades del asistente IA
3. **TestModelos**: Modelos de datos y relaciones
4. **TestVistasWeb**: Vistas y permisos web
5. **TestIntegracion**: Flujos completos de integración

## 🔒 Seguridad

### Autenticación y Autorización

- **JWT Tokens**: Autenticación stateless segura
- **Roles de Usuario**: empleado, supervisor, admin
- **Permisos Granulares**: Control de acceso por funcionalidad
- **Sesiones Seguras**: Manejo adecuado de sesiones

### Protección de Datos

- **Encriptación**: Datos sensibles encriptados
- **Validación**: Entrada de datos sanitizada
- **Auditoría**: Registro de actividades importantes
- **Backup**: Estrategias de respaldo automático

## 📈 Monitoreo y Métricas

### Métricas de Sistema

- **Productividad**: Ratio tiempo productivo vs improductivo
- **Actividad**: Seguimiento de aplicaciones usadas
- **Errores**: Detección y análisis de problemas
- **Rendimiento**: Métricas de respuesta del sistema

### Dashboard de Métricas

- **Tiempo Real**: Actualización continua de datos
- **Históricos**: Tendencias a lo largo del tiempo
- **Comparativos**: Análisis entre períodos
- **Personalizados**: Filtros y vistas específicas

## 🚀 Despliegue en Producción

### Configuración de Producción

1. **Variables de Entorno**
   ```env
   DEBUG=False
   SECRET_KEY=tu_clave_secreta_segura
   DATABASE_URL=postgresql://user:pass@host:port/db
   ALLOWED_HOSTS=tu-dominio.com
   ```

2. **Configuración de Nginx**
   ```nginx
   server {
       listen 80;
       server_name tu-dominio.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **SSL con Let's Encrypt**
   ```bash
   certbot --nginx -d tu-dominio.com
   ```

### Escalabilidad

- **Contenedores**: Fácil escalado horizontal
- **Base de Datos**: Configuración para alta disponibilidad
- **Caché**: Redis para optimización de rendimiento
- **CDN**: Distribución de assets estáticos

## 🤝 Contribución

### Guías para Contribuidores

1. **Fork** el proyecto
2. **Crea** una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crea** un Pull Request

### Estándares de Código

- **PEP 8**: Estilo de código Python
- **Django Best Practices**: Patrones recomendados
- **Tests**: Cobertura mínima del 80%
- **Documentación**: Docstrings completos

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

### Canales de Soporte

- **Documentación**: [Wiki del proyecto]
- **Issues**: [Sistema de tickets]
- **Email**: soporte@sara-system.com
- **Chat**: [Discord/Slack del proyecto]

### Preguntas Frecuentes

#### ¿Cómo funciona el monitoreo de productividad?
SARA monitorea automáticamente las aplicaciones que usas y clasifica tu actividad como productiva o improductiva basada en reglas configurables.

#### ¿Es seguro el sistema?
Sí, SARA utiliza encriptación de datos, autenticación JWT y cumple con estándares de seguridad modernos.

#### ¿Puedo personalizar las reglas de productividad?
Sí, cada usuario puede configurar qué aplicaciones considera productivas y ajustar la sensibilidad del monitoreo.

#### ¿Funciona en diferentes sistemas operativos?
Actualmente soportamos Windows, macOS y Linux a través de Docker.

## 🎯 Roadmap

### Próximas Funcionalidades

- [ ] **Aplicación Móvil**: App nativa para iOS y Android
- [ ] **Integración con Slack/Microsoft Teams**: Notificaciones en tiempo real
- [ ] **Machine Learning Avanzado**: Predicciones de productividad
- [ ] **Gamificación**: Sistema de recompensas y logros
- [ ] **API Pública**: Acceso programático para integraciones
- [ ] **Multi-tenancy**: Soporte para múltiples organizaciones

### Versiones Recientes

#### v1.0.0 (Actual)
- ✅ Asistente IA completo con 15 categorías
- ✅ Monitoreo de productividad en tiempo real
- ✅ Dashboard responsive
- ✅ API REST completa
- ✅ Tests comprehensivos
- ✅ Contenedorización con Docker

---

**Desarrollado con ❤️ para mejorar la productividad laboral**