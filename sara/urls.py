from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from rest_framework.routers import DefaultRouter
from core import views

router = DefaultRouter()
router.register(r'registros', views.RegistroViewSet)

urlpatterns = [
    path('', views.dashboard_view, name='home'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Gestión de Usuarios (solo admin)
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/crear/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.usuario_edit, name='usuario_edit'),
    path('usuarios/<int:pk>/eliminar/', views.usuario_delete, name='usuario_delete'),

    # Gestión de Registros
    path('registros/', views.registros_list, name='registros_list'),
    path('registros/crear/', views.registro_create, name='registro_create'),
    path('registros/<int:pk>/editar/', views.registro_edit, name='registro_edit'),
    path('registros/<int:pk>/eliminar/', views.registro_delete, name='registro_delete'),

    # Gestión de Estadísticas
    path('estadisticas/', views.estadisticas_list, name='estadisticas_list'),
    path('estadisticas/<int:pk>/', views.estadistica_detail, name='estadistica_detail'),

    # Gestión de Análisis IA
    path('analisis/', views.analisis_list, name='analisis_list'),
    path('analisis/<int:pk>/', views.analisis_detail, name='analisis_detail'),

    # Gestión de Actividad de Usuario (Monitoreo)
    path('actividad/', views.actividad_list, name='actividad_list'),
    path('actividad/usuario/<int:usuario_id>/', views.actividad_usuario_detail, name='actividad_usuario_detail'),

    # Dashboard Administrativo
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),

    # Vista completa de empleados
    path('empleados/overview/', views.empleados_overview, name='empleados_overview'),

    # Asistente IA Interactivo (Interfaz Web Completa)
    path('asistente/', views.asistente_web_interface, name='asistente_chat'),
    path('asistente/web/', views.asistente_web_interface, name='asistente_web'),

    # API endpoints adicionales
    path('api/asistente/chat/', views.asistente_chat_api, name='asistente_chat_api'),
    path('api/consejos-proactivos/', views.consejos_proactivos_api, name='consejos_proactivos_api'),

    path('api/', include(router.urls)),
    path('api/dashboard/', views.dashboard_api, name='dashboard'),
    path('api/activity/', views.actividad_usuario_api, name='actividad_usuario_api'),
    path('api/login/', views.login_api, name='login_api'),
    path('api/health/', views.health_check, name='health_check'),
]
