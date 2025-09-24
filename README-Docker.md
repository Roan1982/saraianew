# SARA - Sistema de Asistencia y Registro de Actividad

SARA es un sistema completo de monitoreo de productividad y asistencia IA para equipos de trabajo, desarrollado con Django, PostgreSQL y Electron.

## 🚀 Inicio Rápido con Docker

### Prerrequisitos

- Docker Desktop instalado y corriendo
- Al menos 4GB de RAM disponible
- Puertos 80 y 8000 libres

### Configuración Inicial

1. **Clona el repositorio:**
   ```bash
   git clone <url-del-repo>
   cd saraianew
   ```

2. **Configuración completa automática:**
   ```bash
   # Esto construirá las imágenes, iniciará los servicios,
   # creará un superusuario y poblará la DB con datos de ejemplo
   ./init-docker.sh full-setup
   ```

### Comandos Útiles

```bash
# Iniciar servicios
./init-docker.sh start

# Detener servicios
./init-docker.sh stop

# Ver logs en tiempo real
./init-docker.sh logs

# Acceder al shell del backend
./init-docker.sh shell

# Ejecutar comandos de Django
./init-docker.sh manage migrate
./init-docker.sh manage shell

# Crear superusuario adicional
./init-docker.sh superuser

# Poblar DB con datos de ejemplo
./init-docker.sh populate

# Ver estado de servicios
./init-docker.sh status

# Limpieza completa
./init-docker.sh clean
```

## 🌐 Acceso a la Aplicación

Una vez iniciados los servicios:

- **Aplicación Web:** http://localhost
- **API Backend:** http://localhost:8000
- **Admin Django:** http://localhost:8000/admin/
- **Asistente IA:** http://localhost/asistente/

### Credenciales por Defecto

- **Superusuario:** admin / admin (cambiar después del primer login)
- **Usuario de ejemplo:** empleado1 / password123

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80)    │    │ Backend Django  │    │   PostgreSQL    │
│                 │────│   (8000)        │────│                 │
│  - Proxy        │    │  - REST API     │    │  - Datos        │
│  - Static Files │    │  - Asistente IA │    │  - Usuarios     │
└─────────────────┘    │  - Web App      │    └─────────────────┘
                       └─────────────────┘             │
┌─────────────────┐                           ┌─────────────────┐
│ Electron Client │                           │   Volúmenes     │
│                 │                           │  - staticfiles  │
│  - GUI Desktop  │                           │  - media        │
│  - Monitoreo    │                           │  - postgres_data│
└─────────────────┘                           └─────────────────┘
```

## 📁 Estructura del Proyecto

```
saraianew/
├── core/                    # App principal de Django
│   ├── models.py           # Modelos de datos
│   ├── views.py            # Vistas y APIs
│   ├── templates/          # Plantillas HTML
│   └── static/             # Archivos estáticos
├── sara/                   # Configuración de Django
│   ├── settings.py         # Configuración principal
│   ├── urls.py             # Rutas URL
│   └── wsgi.py             # WSGI
├── asistente-virtual/      # Cliente Electron
│   ├── src/                # Código fuente
│   ├── package.json        # Dependencias Node.js
│   └── docker-entrypoint.sh
├── docker-compose.yml      # Orquestación Docker
├── Dockerfile.backend      # Imagen backend
├── Dockerfile.electron     # Imagen cliente
├── nginx.conf             # Configuración Nginx
├── init-docker.sh         # Script de gestión
└── requirements.txt       # Dependencias Python
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

### Base de Datos

Por defecto usa PostgreSQL. Para desarrollo con SQLite:

```bash
# En .env
DATABASE_URL=sqlite:///db.sqlite3
```

### Desarrollo Local

Para desarrollo sin Docker:

```bash
# Backend
cd saraianew
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Cliente Electron (en otra terminal)
cd asistente-virtual
npm install
npm start
```

## 📊 Características

- ✅ **Monitoreo de Productividad:** Seguimiento de actividad en tiempo real
- ✅ **Asistente IA:** Chat inteligente con recomendaciones personalizadas
- ✅ **Dashboard Administrativo:** Gestión completa de usuarios y estadísticas
- ✅ **API REST:** Endpoints para integración con otros sistemas
- ✅ **Cliente Desktop:** Aplicación Electron para monitoreo local
- ✅ **Base de Datos PostgreSQL:** Almacenamiento robusto y escalable
- ✅ **Nginx Proxy:** Servidor web de alto rendimiento
- ✅ **Docker Ready:** Despliegue simplificado con contenedores

## 🧪 Testing

```bash
# Ejecutar tests
./init-docker.sh manage test

# Ejecutar tests con coverage
./init-docker.sh manage test --verbosity=2
```

## 📝 API Documentation

### Endpoints Principales

- `GET /api/health/` - Health check
- `POST /api/asistente/chat/` - Chat con IA
- `GET /api/dashboard/` - Datos del dashboard
- `GET /api/registros/` - Lista de registros

### Autenticación

La API usa JWT (JSON Web Tokens) para autenticación.

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras problemas:

1. Verifica que Docker esté corriendo
2. Revisa los logs: `./init-docker.sh logs`
3. Verifica el estado: `./init-docker.sh status`
4. Reinicia los servicios: `./init-docker.sh restart`

Para más ayuda, abre un issue en el repositorio.