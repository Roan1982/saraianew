from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Registro, Estadistica, IAAnalisis, ActividadUsuario, Usuario
from .serializers import RegistroSerializer, EstadisticaSerializer, IAAnalisisSerializer, ActividadUsuarioSerializer
from django.db.models import Count

try:
    from .ia_module import analizar_errores
except ImportError:
    analizar_errores = None

def dashboard_view(request):
    """Vista principal del dashboard - redirige según rol del usuario"""
    if not request.user.is_authenticated:
        return redirect('login')

    # Admin y supervisor van al dashboard administrativo
    if request.user.rol in ['admin', 'supervisor']:
        return redirect('dashboard_admin')

    # Empleados van al dashboard personal
    return dashboard_authenticated(request)

@login_required
def dashboard_authenticated(request):
    """Vista del dashboard para usuarios autenticados"""
    user = request.user
    estadisticas = Estadistica.objects.filter(usuario=user).last()
    analisis = IAAnalisis.objects.filter(usuario=user).last()

    # Consejos recientes del agente personal
    consejos_recientes = IAAnalisis.objects.filter(
        usuario=user,
        patrones_detectados__tipo="agente_personal"
    ).order_by('-fecha_analisis')[:3]

    return render(request, 'core/dashboard.html', {
        'user': user,
        'estadisticas': estadisticas,
        'analisis': analisis,
        'consejos_recientes': consejos_recientes,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = request.user
    estadisticas = Estadistica.objects.filter(usuario=user).last()
    analisis = IAAnalisis.objects.filter(usuario=user).last()

    # Si es una petición AJAX o API, devolver JSON
    if request.META.get('HTTP_ACCEPT', '').find('application/json') != -1 or request.GET.get('format') == 'json':
        data = {
            'estadisticas': EstadisticaSerializer(estadisticas).data if estadisticas else None,
            'analisis': IAAnalisisSerializer(analisis).data if analisis else None,
        }
        return Response(data)
    else:
        # Renderizar template HTML
        return render(request, 'core/dashboard.html', {
            'user': user,
            'estadisticas': estadisticas,
            'analisis': analisis,
        })

class RegistroViewSet(viewsets.ModelViewSet):
    queryset = Registro.objects.all()
    serializer_class = RegistroSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        registro = serializer.save(usuario=self.request.user)
        errores = self.validar_registro(registro.contenido)
        registro.errores = errores
        registro.save()
        if analizar_errores and errores:
            analizar_errores(self.request.user)

    def validar_registro(self, contenido):
        errores = []
        if 'fecha' in contenido and not self.es_fecha_valida(contenido['fecha']):
            errores.append({'campo': 'fecha', 'mensaje': 'Formato de fecha incorrecto (DD/MM/AAAA)'})
        return errores

    def es_fecha_valida(self, fecha_str):
        try:
            from datetime import datetime
            datetime.strptime(fecha_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_api(request):
    """API endpoint del dashboard - solo JSON"""
    user = request.user
    estadisticas = Estadistica.objects.filter(usuario=user).last()
    analisis = IAAnalisis.objects.filter(usuario=user).last()

    data = {
        'estadisticas': EstadisticaSerializer(estadisticas).data if estadisticas else None,
        'analisis': IAAnalisisSerializer(analisis).data if analisis else None,
    }
    return Response(data)

# Gestión de Usuarios
@login_required
def usuarios_list(request):
    """Lista todos los usuarios - solo para administradores"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    usuarios = Usuario.objects.all().order_by('username')
    return render(request, 'core/usuarios_list.html', {'usuarios': usuarios})

@login_required
def usuario_create(request):
    """Crear nuevo usuario - solo para administradores"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        rol = request.POST.get('rol')

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return redirect('usuario_create')

        try:
            usuario = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                rol=rol
            )
            messages.success(request, f'Usuario {username} creado exitosamente.')
            return redirect('usuarios_list')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            return redirect('usuario_create')

    return render(request, 'core/usuario_form.html', {'action': 'create'})

@login_required
def usuario_edit(request, pk):
    """Editar usuario - solo para administradores"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        usuario.email = request.POST.get('email')
        usuario.first_name = request.POST.get('first_name')
        usuario.last_name = request.POST.get('last_name')
        usuario.rol = request.POST.get('rol')
        usuario.is_active = request.POST.get('is_active') == 'on'

        # Cambiar contraseña solo si se proporciona
        password = request.POST.get('password')
        if password:
            usuario.set_password(password)

        try:
            usuario.save()
            messages.success(request, f'Usuario {usuario.username} actualizado exitosamente.')
            return redirect('usuarios_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
            return redirect('usuario_edit', pk=pk)

    return render(request, 'core/usuario_form.html', {
        'usuario': usuario,
        'action': 'edit'
    })

@login_required
def usuario_delete(request, pk):
    """Eliminar usuario - solo para administradores"""
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        try:
            username = usuario.username
            usuario.delete()
            messages.success(request, f'Usuario {username} eliminado exitosamente.')
            return redirect('usuarios_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')
            return redirect('usuarios_list')

    return render(request, 'core/usuario_confirm_delete.html', {'usuario': usuario})

# Gestión de Registros
@login_required
def registros_list(request):
    """Lista todos los registros - según permisos del usuario"""
    if request.user.rol == 'admin':
        registros = Registro.objects.all().order_by('-fecha')
    elif request.user.rol == 'supervisor':
        registros = Registro.objects.all().order_by('-fecha')
    else:  # empleado
        registros = Registro.objects.filter(usuario=request.user).order_by('-fecha')

    return render(request, 'core/registros_list.html', {'registros': registros})

@login_required
def registro_create(request):
    """Crear nuevo registro"""
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        contenido = request.POST.get('contenido')

        try:
            # Parsear contenido JSON
            import json
            contenido_data = json.loads(contenido) if contenido else {}

            registro = Registro.objects.create(
                usuario=request.user,
                fecha=fecha,
                contenido=contenido_data
            )

            # Validar y analizar errores
            errores = RegistroViewSet.validar_registro(None, contenido_data)
            registro.errores = errores
            registro.save()

            if analizar_errores and errores:
                analizar_errores(request.user)

            messages.success(request, 'Registro creado exitosamente.')
            return redirect('registros_list')
        except json.JSONDecodeError:
            messages.error(request, 'El contenido debe ser un JSON válido.')
            return redirect('registro_create')
        except Exception as e:
            messages.error(request, f'Error al crear registro: {str(e)}')
            return redirect('registro_create')

    return render(request, 'core/registro_form.html', {'action': 'create'})

@login_required
def registro_edit(request, pk):
    """Editar registro - solo el propietario o admin/supervisor"""
    registro = get_object_or_404(Registro, pk=pk)

    if not (request.user.rol in ['admin', 'supervisor'] or registro.usuario == request.user):
        messages.error(request, 'No tienes permisos para editar este registro.')
        return redirect('registros_list')

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        contenido = request.POST.get('contenido')

        try:
            # Parsear contenido JSON
            import json
            contenido_data = json.loads(contenido) if contenido else {}

            registro.fecha = fecha
            registro.contenido = contenido_data

            # Revalidar errores
            errores = RegistroViewSet.validar_registro(None, contenido_data)
            registro.errores = errores
            registro.save()

            messages.success(request, 'Registro actualizado exitosamente.')
            return redirect('registros_list')
        except json.JSONDecodeError:
            messages.error(request, 'El contenido debe ser un JSON válido.')
            return redirect('registro_edit', pk=pk)
        except Exception as e:
            messages.error(request, f'Error al actualizar registro: {str(e)}')
            return redirect('registro_edit', pk=pk)

    return render(request, 'core/registro_form.html', {
        'registro': registro,
        'action': 'edit'
    })

@login_required
def registro_delete(request, pk):
    """Eliminar registro - solo el propietario o admin/supervisor"""
    registro = get_object_or_404(Registro, pk=pk)

    if not (request.user.rol in ['admin', 'supervisor'] or registro.usuario == request.user):
        messages.error(request, 'No tienes permisos para eliminar este registro.')
        return redirect('registros_list')

    if request.method == 'POST':
        try:
            registro.delete()
            messages.success(request, 'Registro eliminado exitosamente.')
            return redirect('registros_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar registro: {str(e)}')
            return redirect('registros_list')

    return render(request, 'core/registro_confirm_delete.html', {'registro': registro})

# Gestión de Estadísticas
@login_required
def estadisticas_list(request):
    """Lista estadísticas - según permisos del usuario"""
    if request.user.rol == 'admin':
        estadisticas = Estadistica.objects.all().order_by('-fecha_actualizacion')
    elif request.user.rol == 'supervisor':
        estadisticas = Estadistica.objects.all().order_by('-fecha_actualizacion')
    else:  # empleado
        estadisticas = Estadistica.objects.filter(usuario=request.user).order_by('-fecha_actualizacion')

    return render(request, 'core/estadisticas_list.html', {'estadisticas': estadisticas})

@login_required
def estadistica_detail(request, pk):
    """Ver detalle de estadística"""
    estadistica = get_object_or_404(Estadistica, pk=pk)

    if not (request.user.rol in ['admin', 'supervisor'] or estadistica.usuario == request.user):
        messages.error(request, 'No tienes permisos para ver esta estadística.')
        return redirect('estadisticas_list')

    return render(request, 'core/estadistica_detail.html', {'estadistica': estadistica})

# Gestión de Análisis IA
@login_required
def analisis_list(request):
    """Lista análisis IA - según permisos del usuario"""
    if request.user.rol == 'admin':
        analisis = IAAnalisis.objects.all().order_by('-fecha_analisis')
    elif request.user.rol == 'supervisor':
        analisis = IAAnalisis.objects.all().order_by('-fecha_analisis')
    else:  # empleado
        analisis = IAAnalisis.objects.filter(usuario=request.user).order_by('-fecha_analisis')

    return render(request, 'core/analisis_list.html', {'analisis_list': analisis})

@login_required
def analisis_detail(request, pk):
    """Ver detalle de análisis IA"""
    analisis = get_object_or_404(IAAnalisis, pk=pk)

    if not (request.user.rol in ['admin', 'supervisor'] or analisis.usuario == request.user):
        messages.error(request, 'No tienes permisos para ver este análisis.')
        return redirect('analisis_list')

    # Calcular estadísticas adicionales
    registros_con_errores = analisis.usuario.registro_set.filter(errores__isnull=False).count()

    context = {
        'analisis': analisis,
        'registros_con_errores': registros_con_errores,
    }

    return render(request, 'core/analisis_detail.html', context)

# Gestión de Actividad de Usuario (Monitoreo en tiempo real)
@login_required
def actividad_list(request):
    """Lista actividad de usuarios - según permisos del usuario"""
    # Inicializar variables
    usuario_id = request.GET.get('usuario')

    if request.user.rol in ['admin', 'supervisor']:
        # Admin y supervisor ven actividad de todos los usuarios
        actividades = ActividadUsuario.objects.select_related('usuario').all().order_by('-timestamp')
        # Filtrar por usuario si se especifica
        if usuario_id:
            actividades = actividades.filter(usuario_id=usuario_id)
    else:
        # Empleados solo ven su propia actividad
        actividades = ActividadUsuario.objects.filter(usuario=request.user).order_by('-timestamp')

    # Filtrar por fecha si se especifica
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if fecha_desde:
        actividades = actividades.filter(timestamp__date__gte=fecha_desde)
    if fecha_hasta:
        actividades = actividades.filter(timestamp__date__lte=fecha_hasta)

    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(actividades, 50)  # 50 actividades por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Obtener lista de usuarios para el filtro (solo para admin/supervisor)
    usuarios = []
    if request.user.rol in ['admin', 'supervisor']:
        usuarios = Usuario.objects.all().order_by('username')

    context = {
        'page_obj': page_obj,
        'usuarios': usuarios,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'usuario_filtro': usuario_id,
    }

    return render(request, 'core/actividad_list.html', context)

@login_required
def actividad_usuario_detail(request, usuario_id):
    """Ver actividad detallada de un usuario específico - solo admin/supervisor"""
    if request.user.rol not in ['admin', 'supervisor']:
        messages.error(request, 'No tienes permisos para acceder a esta información.')
        return redirect('home')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Estadísticas de actividad del usuario
    actividades_recientes = ActividadUsuario.objects.filter(
        usuario=usuario,
        timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
    )

    # Contar tipos de actividad
    productiva = actividades_recientes.filter(productividad='productive').count()
    improductiva = actividades_recientes.filter(productividad='unproductive').count()
    gaming = actividades_recientes.filter(productividad='gaming').count()
    neutral = actividades_recientes.filter(productividad='neutral').count()

    total_actividades = actividades_recientes.count()

    # Aplicaciones más usadas
    from django.db.models import Count
    aplicaciones_mas_usadas = actividades_recientes.values('ventana_activa').annotate(
        count=Count('ventana_activa')
    ).order_by('-count')[:10]

    # Calcular porcentajes para las aplicaciones más usadas
    aplicaciones_con_porcentaje = []
    if aplicaciones_mas_usadas:
        max_count = aplicaciones_mas_usadas[0]['count']
        for app in aplicaciones_mas_usadas:
            porcentaje = round((app['count'] / max_count) * 100, 1) if max_count > 0 else 0
            aplicaciones_con_porcentaje.append({
                'ventana_activa': app['ventana_activa'],
                'count': app['count'],
                'porcentaje': porcentaje
            })

    # Estadísticas del usuario
    estadisticas = Estadistica.objects.filter(usuario=usuario).last()
    analisis_reciente = IAAnalisis.objects.filter(usuario=usuario).last()

    context = {
        'usuario': usuario,
        'actividades_recientes': actividades_recientes.order_by('-timestamp')[:20],
        'estadisticas': {
            'productiva': productiva,
            'improductiva': improductiva,
            'gaming': gaming,
            'neutral': neutral,
            'total': total_actividades,
        },
        'aplicaciones_mas_usadas': aplicaciones_con_porcentaje,
        'estadistica_usuario': estadisticas,
        'analisis_reciente': analisis_reciente,
    }

    return render(request, 'core/actividad_usuario_detail.html', context)

@login_required
def dashboard_admin(request):
    """Dashboard administrativo para admin/supervisor"""
    if request.user.rol not in ['admin', 'supervisor']:
        messages.error(request, 'No tienes permisos para acceder al dashboard administrativo.')
        return redirect('home')

    # Estadísticas generales
    total_usuarios = Usuario.objects.count()
    usuarios_activos = Usuario.objects.filter(is_active=True).count()

    # Actividad en las últimas 24 horas
    actividades_24h = ActividadUsuario.objects.filter(
        timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
    )

    # Estadísticas de productividad
    productiva_total = actividades_24h.filter(productividad='productive').count()
    improductiva_total = actividades_24h.filter(productividad='unproductive').count()
    gaming_total = actividades_24h.filter(productividad='gaming').count()

    total_actividades_24h = actividades_24h.count()

    # Usuarios con más actividad
    usuarios_mas_activos = actividades_24h.values('usuario__id', 'usuario__username', 'usuario__first_name', 'usuario__last_name').annotate(
        count=Count('usuario')
    ).order_by('-count')[:10]

    # Alertas recientes (análisis IA de las últimas horas)
    alertas_recientes = IAAnalisis.objects.filter(
        fecha_analisis__gte=timezone.now() - timezone.timedelta(hours=24)
    ).select_related('usuario').order_by('-fecha_analisis')[:10]

    context = {
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'estadisticas_24h': {
            'productiva': productiva_total,
            'improductiva': improductiva_total,
            'gaming': gaming_total,
            'total': total_actividades_24h,
        },
        'usuarios_mas_activos': usuarios_mas_activos,
        'alertas_recientes': alertas_recientes,
    }

    return render(request, 'core/dashboard_admin.html', context)

@login_required
def empleados_overview(request):
    """Vista completa de todos los empleados para admin/supervisor"""
    if request.user.rol not in ['admin', 'supervisor']:
        messages.error(request, 'No tienes permisos para acceder a esta información.')
        return redirect('home')

    # Obtener todos los empleados
    empleados = Usuario.objects.filter(rol='empleado').order_by('username')

    empleados_data = []

    for empleado in empleados:
        # Actividad en las últimas 24 horas
        actividades_24h = ActividadUsuario.objects.filter(
            usuario=empleado,
            timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
        )

        # Calcular productividad
        productiva = actividades_24h.filter(productividad='productive').count()
        improductiva = actividades_24h.filter(productividad='unproductive').count()
        gaming = actividades_24h.filter(productividad='gaming').count()
        neutral = actividades_24h.filter(productividad='neutral').count()
        total_actividades = actividades_24h.count()

        # Calcular porcentaje de productividad
        if total_actividades > 0:
            productividad_porcentaje = round((productiva / total_actividades) * 100, 1)
        else:
            productividad_porcentaje = 0

        # Última actividad
        ultima_actividad = actividades_24h.order_by('-timestamp').first()

        # Análisis IA más reciente
        analisis_reciente = IAAnalisis.objects.filter(
            usuario=empleado
        ).order_by('-fecha_analisis').first()

        # Estadísticas del empleado
        estadistica = Estadistica.objects.filter(usuario=empleado).last()

        # Estado actual (basado en actividad reciente)
        if ultima_actividad and (timezone.now() - ultima_actividad.timestamp).seconds < 300:  # 5 minutos
            estado = 'activo'
        elif actividades_24h.exists():
            estado = 'inactivo_hoy'
        else:
            estado = 'sin_actividad'

        empleados_data.append({
            'usuario': empleado,
            'estado': estado,
            'ultima_actividad': ultima_actividad,
            'estadisticas_24h': {
                'productiva': productiva,
                'improductiva': improductiva,
                'gaming': gaming,
                'neutral': neutral,
                'total': total_actividades,
                'productividad_porcentaje': productividad_porcentaje,
            },
            'analisis_reciente': analisis_reciente,
            'estadistica': estadistica,
        })

    context = {
        'empleados_data': empleados_data,
    }

    return render(request, 'core/empleados_overview.html', context)

# Asistente IA Interactivo
@login_required
def asistente_chat(request):
    """Interfaz de chat con el asistente IA"""
    return render(request, 'core/asistente_chat.html')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asistente_chat_api(request):
    """API para interactuar con el asistente IA"""
    try:
        mensaje_usuario = request.data.get('mensaje', '').strip()
        contexto = request.data.get('contexto', {})

        if not mensaje_usuario:
            return Response({'error': 'Mensaje requerido'}, status=status.HTTP_400_BAD_REQUEST)

        # Generar respuesta del asistente
        respuesta_asistente = generar_respuesta_asistente(request.user, mensaje_usuario, contexto)

        return Response({
            'respuesta': respuesta_asistente,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def generar_respuesta_asistente(usuario, mensaje, contexto):
    """Genera respuesta inteligente del asistente basada en el contexto del usuario"""
    mensaje_lower = mensaje.lower()

    # Análisis de intención del mensaje
    if any(palabra in mensaje_lower for palabra in ['ayuda', 'help', 'ayudame']):
        return generar_respuesta_ayuda(usuario, contexto)

    elif any(palabra in mensaje_lower for palabra in ['productividad', 'productivo', 'eficiencia']):
        return generar_respuesta_productividad(usuario)

    elif any(palabra in mensaje_lower for palabra in ['error', 'problema', 'issue', 'bug']):
        return generar_respuesta_errores(usuario)

    elif any(palabra in mensaje_lower for palabra in ['excel', 'formula', 'fórmula']):
        return generar_respuesta_excel()

    elif any(palabra in mensaje_lower for palabra in ['tiempo', 'horas', 'trabajo']):
        return generar_respuesta_tiempo(usuario)

    elif any(palabra in mensaje_lower for palabra in ['consejo', 'tip', 'recomendacion']):
        return generar_respuesta_consejos(usuario)

    elif any(palabra in mensaje_lower for palabra in ['escribir', 'escribe', 'ortografía', 'ortografia', 'palabra', 'palabras', 'se escribe', 'como se escribe']):
        return generar_respuesta_ortografia(mensaje, usuario)

    else:
        # Respuesta general inteligente
        return generar_respuesta_general(mensaje, usuario)

def generar_respuesta_ayuda(usuario, contexto):
    """Genera respuesta de ayuda contextual"""
    respuestas = [
        f"¡Hola {usuario.get_full_name() or usuario.username}! Soy tu asistente personal de IA. ¿En qué puedo ayudarte hoy?",
        "Estoy aquí para ayudarte con:",
        "• 💡 Consejos de productividad y mejores prácticas",
        "• 📊 Análisis de tu rendimiento laboral",
        "• 🔧 Soluciones para problemas técnicos",
        "• ⏰ Gestión del tiempo y organización",
        "• 📈 Recomendaciones personalizadas",
        "",
        "¿Qué tipo de ayuda necesitas específicamente?"
    ]
    return "\n".join(respuestas)

def generar_respuesta_productividad(usuario):
    """Genera consejos de productividad"""
    # Obtener estadísticas recientes del usuario
    estadisticas = Estadistica.objects.filter(usuario=usuario).last()

    if estadisticas:
        puntaje = estadisticas.puntaje
        mejoras = estadisticas.mejoras

        if puntaje >= 80:
            nivel = "¡Excelente! Mantén ese ritmo."
        elif puntaje >= 60:
            nivel = "Buen trabajo, pero puedes mejorar."
        else:
            nivel = "Necesitas enfocarte más en tareas productivas."

        respuesta = f"""📊 Tu productividad actual: {puntaje}/100 puntos
🎯 Nivel: {nivel}
📈 Mejoras acumuladas: {mejoras}

💡 Consejos para mejorar:
• Técnica Pomodoro: 25 min trabajo + 5 min descanso
• Identifica y elimina distracciones
• Prioriza tareas importantes
• Toma descansos regulares cada 2 horas

¿Quieres que te ayude con alguna técnica específica?"""
    else:
        respuesta = """📊 No tengo suficientes datos de tu productividad aún.

💡 Consejos generales para mejorar:
• Establece metas diarias claras
• Usa la regla 80/20 (Pareto)
• Evita multitasking
• Revisa y ajusta tu rutina semanalmente

¡Empieza a trabajar y te daré consejos más personalizados!"""

    return respuesta

def generar_respuesta_errores(usuario):
    """Ayuda con resolución de errores"""
    # Buscar errores recientes en registros del usuario
    registros_con_errores = Registro.objects.filter(
        usuario=usuario,
        errores__isnull=False
    ).order_by('-fecha')[:3]

    if registros_con_errores.exists():
        respuesta = "🔍 He encontrado algunos errores recientes en tus registros:\n\n"

        for registro in registros_con_errores:
            errores = registro.errores
            respuesta += f"📝 Registro del {registro.fecha.strftime('%d/%m/%Y')}:\n"
            for error in errores:
                respuesta += f"  • {error.get('mensaje', 'Error detectado')}\n"
            respuesta += "\n"

        respuesta += "💡 ¿Quieres que te ayude a corregir alguno de estos errores?"
    else:
        respuesta = """✅ No encontré errores recientes en tus registros.

🔧 Si tienes algún problema técnico, puedo ayudarte con:
• Configuración de aplicaciones
• Solución de errores comunes
• Mejores prácticas
• Guías paso a paso

¿Cuál es el problema específico que estás experimentando?"""

    return respuesta

def generar_respuesta_excel():
    """Consejos específicos para Excel"""
    consejos = [
        "📊 Excel - Consejos profesionales:",
        "",
        "🔧 Atajos esenciales:",
        "• Ctrl + S: Guardar (¡úsalo frecuentemente!)",
        "• F2: Editar celda activa",
        "• Ctrl + Z: Deshacer",
        "• Ctrl + C/V: Copiar/Pegar",
        "• Ctrl + Flecha: Ir al final de datos",
        "",
        "📈 Fórmulas avanzadas:",
        "• Usa $ para referencias absolutas: =SUMA($A$1:$A$10)",
        "• BUSCARV para buscar datos: =BUSCARV(valor, rango, columna, FALSO)",
        "• SI con condiciones: =SI(A1>10, 'Alto', 'Bajo')",
        "• CONTAR.SI para contar con condiciones",
        "",
        "⚡ Mejores prácticas:",
        "• Nombres descriptivos para rangos",
        "• Validación de datos en celdas",
        "• Formato condicional para resaltar información",
        "• Tablas dinámicas para análisis",
        "",
        "¿Qué función específica necesitas ayuda?"
    ]
    return "\n".join(consejos)

def generar_respuesta_tiempo(usuario):
    """Análisis y consejos sobre gestión del tiempo"""
    # Calcular tiempo de actividad hoy
    hoy = timezone.now().date()
    actividades_hoy = ActividadUsuario.objects.filter(
        usuario=usuario,
        timestamp__date=hoy
    ).count()

    tiempo_trabajo_minutos = (actividades_hoy * 30) // 60  # Estimación

    if tiempo_trabajo_minutos > 480:  # Más de 8 horas
        estado = "⚠️ Has trabajado mucho hoy. Es hora de descansar."
    elif tiempo_trabajo_minutos > 360:  # Más de 6 horas
        estado = "⏰ Llevas varias horas trabajando. Considera un descanso."
    elif tiempo_trabajo_minutos > 240:  # Más de 4 horas
        estado = "📈 Buen ritmo de trabajo. ¡Sigue así!"
    else:
        estado = "🚀 ¡Empieza tu jornada productiva!"

    respuesta = f"""⏱️ Gestión del Tiempo - Análisis actual:

📊 Tiempo estimado de trabajo hoy: {tiempo_trabajo_minutos} minutos
🎯 Estado: {estado}

💡 Estrategias de gestión del tiempo:

1. 📅 Planificación semanal:
   • Define objetivos claros para cada día
   • Prioriza tareas con la matriz Eisenhower
   • Reserva tiempo para imprevistos

2. 🎯 Técnica Pomodoro:
   • 25 minutos de trabajo enfocado
   • 5 minutos de descanso
   • Después de 4 ciclos: descanso de 15-30 min

3. 📊 Seguimiento diario:
   • Revisa logros al final del día
   • Identifica qué te robó tiempo
   • Ajusta para mañana

4. ⚡ Optimización:
   • Agrupa tareas similares
   • Elimina reuniones innecesarias
   • Usa herramientas de automatización

¿Quieres que te ayude a crear un plan específico?"""

    return respuesta

def generar_respuesta_consejos(usuario):
    """Genera consejos personalizados basados en el perfil del usuario"""
    # Obtener análisis recientes del agente personal
    consejos_recientes = IAAnalisis.objects.filter(
        usuario=usuario,
        patrones_detectados__tipo="agente_personal"
    ).order_by('-fecha_analisis')[:3]

    if consejos_recientes.exists():
        respuesta = "💡 Consejos recientes de tu agente personal:\n\n"

        for i, consejo in enumerate(consejos_recientes, 1):
            respuesta += f"{i}. {consejo.recomendacion[:100]}{'...' if len(consejo.recomendacion) > 100 else ''}\n"

        respuesta += "\n🎯 ¿Quieres más detalles sobre alguno de estos consejos?"
    else:
        respuesta = """💡 Consejos personalizados:

🚀 Productividad:
• Establece metas SMART (Específicas, Medibles, Alcanzables, Relevantes, Temporales)
• Usa la regla 2 minutos: si algo toma menos de 2 min, hazlo ahora
• Revisa tu email solo 3 veces al día

🧠 Salud mental:
• Toma descansos cada 90 minutos
• Practica la atención plena durante 5 minutos diarios
• Mantén una rutina de sueño consistente

📈 Desarrollo profesional:
• Aprende una nueva habilidad cada mes
• Busca feedback regularmente
• Documenta tus logros semanalmente

¿Sobre qué área te gustaría consejos más específicos?"""

    return respuesta

def generar_respuesta_general(mensaje, usuario):
    """Respuesta general inteligente basada en el contexto"""
    mensaje_lower = mensaje.lower().strip()

    # Detectar saludos
    saludos = ['hola', 'buenos', 'buenas', 'saludos', 'hey', 'hi', 'hello']
    if any(saludo in mensaje_lower for saludo in saludos):
        return f"¡Hola {usuario.get_full_name() or usuario.username}! 👋 ¿En qué puedo ayudarte hoy?"

    # Detectar preguntas
    indicadores_pregunta = ['?', 'como', 'qué', 'que', 'cual', 'cuales', 'cuando', 'donde', 'por qué', 'porque', 'para qué', 'quién', 'quien']
    es_pregunta = any(indicador in mensaje_lower for indicador in indicadores_pregunta) or mensaje.endswith('?')

    if es_pregunta:
        # Intentar responder preguntas específicas
        if any(palabra in mensaje_lower for palabra in ['escribir', 'escribe', 'ortografía', 'ortografia', 'palabra', 'palabras']):
            return "📝 ¡Claro! Puedo ayudarte con ortografía y escritura. ¿Qué palabra o texto específico quieres que revise?"

        elif any(palabra in mensaje_lower for palabra in ['excel', 'fórmula', 'formula', 'hoja', 'spreadsheet']):
            return "📊 Para Excel, puedo ayudarte con fórmulas, funciones y mejores prácticas. ¿Qué necesitas exactamente?"

        elif any(palabra in mensaje_lower for palabra in ['tiempo', 'horas', 'productividad', 'trabajo']):
            return "⏰ Puedo analizar tu tiempo de trabajo y darte consejos de productividad. ¿Quieres que revise tus estadísticas?"

        elif any(palabra in mensaje_lower for palabra in ['error', 'problema', 'ayuda']):
            return "🔧 ¿Tienes algún problema técnico o error? Cuéntame los detalles y te ayudo a solucionarlo."

        else:
            # Pregunta general - dar respuesta general sin contexto de actividad
            return "¡Claro! ¿En qué tema específico necesitas ayuda? Puedo asesorarte sobre productividad, Excel, programación, gestión del tiempo, o cualquier otro tema laboral."

    # Análisis de sentimiento para respuestas no preguntas
    palabras_positivas = ['bien', 'excelente', 'genial', 'perfecto', 'gracias', 'ok', 'okey']
    palabras_negativas = ['mal', 'problema', 'dificultad', 'error', 'ayuda', 'no funciona']

    if any(palabra in mensaje_lower for palabra in palabras_positivas):
        return "¡Me alegra oír eso! 😊 ¿En qué más puedo ayudarte?"

    elif any(palabra in mensaje_lower for palabra in palabras_negativas):
        return "Lamento oír que tienes dificultades. ¿Me puedes dar más detalles para ayudarte mejor?"

    # Mensajes informativos o comandos
    elif any(palabra in mensaje_lower for palabra in ['estado', 'status', 'situación', 'situacion']):
        return "📊 Puedo mostrarte tu estado actual de productividad y actividad. ¿Quieres que genere un resumen?"

    elif any(palabra in mensaje_lower for palabra in ['consejo', 'tip', 'recomendación', 'recomendacion']):
        return "💡 ¡Excelente! Tengo muchos consejos útiles. ¿Sobre qué tema te gustaría recibir consejos?"

    else:
        # Respuesta por defecto más inteligente
        return "¡Hola! Soy SARA, tu asistente personal de IA. Puedo ayudarte con:\n\n• 💡 Consejos de productividad y mejores prácticas\n• 📊 Análisis de tu rendimiento laboral\n• 🔧 Solución de problemas técnicos\n• ⏰ Gestión del tiempo y organización\n• 📈 Recomendaciones personalizadas\n\n¿Sobre qué tema te gustaría conversar?"

# API para Actividad de Usuario (desde cliente de escritorio)
@api_view(['POST'])
def actividad_usuario_api(request):
    """API para recibir datos de actividad desde el cliente de monitoreo"""
    try:
        machine_id = request.data.get('machineId')
        user_id = request.data.get('userId')
        activities = request.data.get('activities', [])

        if not machine_id or not activities:
            return Response(
                {'error': 'machineId y activities son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar usuario por ID
        try:
            usuario = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        actividades_creadas = []
        for activity_data in activities:
            actividad = ActividadUsuario.objects.create(
                usuario=usuario,
                machine_id=machine_id,
                timestamp=activity_data.get('timestamp'),
                ventana_activa=activity_data.get('activeWindow', 'Desconocido'),
                procesos_activos=activity_data.get('topProcesses', []),
                carga_sistema=activity_data.get('systemLoad', {}),
                productividad=activity_data.get('productivity', 'neutral')
            )
            actividades_creadas.append(actividad)

        # Análisis proactivo de IA
        analizar_actividad_proactiva(actividad)

        return Response({
            'message': f'{len(actividades_creadas)} actividades registradas',
            'actividades': len(actividades_creadas)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def analizar_actividad_proactiva(actividad):
    """Agente personal de IA que analiza actividad en tiempo real y da consejos contextuales"""
    try:
        usuario = actividad.usuario
        ventana_activa = actividad.ventana_activa.lower() if actividad.ventana_activa else ""
        timestamp = actividad.timestamp

        # Asegurar que timestamp sea un objeto datetime
        if isinstance(timestamp, str):
            try:
                timestamp = timezone.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                timestamp = timezone.now()

        # Análisis contextual basado en la aplicación activa
        consejos_contextuales = analizar_aplicacion_contextual(ventana_activa, usuario)

        # Análisis de patrones de productividad
        consejos_productividad = analizar_patron_productividad(usuario, timestamp)

        # Análisis de tiempo y fatiga
        consejos_tiempo = analizar_tiempo_trabajo(usuario, timestamp)

        # Combinar todos los consejos
        todos_consejos = consejos_contextuales + consejos_productividad + consejos_tiempo

        if todos_consejos:
            # Crear análisis con consejos específicos
            recomendacion_texto = ". ".join(todos_consejos)

            IAAnalisis.objects.create(
                usuario=usuario,
                recomendacion=recomendacion_texto,
                patrones_detectados={
                    'tipo': 'agente_personal',
                    'ventana_activa': actividad.ventana_activa,
                    'consejos_contextuales': len(consejos_contextuales),
                    'consejos_productividad': len(consejos_productividad),
                    'consejos_tiempo': len(consejos_tiempo),
                    'timestamp': timestamp.isoformat()
                }
            )

            # Actualizar estadísticas basadas en la actividad
            actualizar_estadisticas_inteligentes(actividad)

    except Exception as e:
        print(f"Error en agente personal de IA: {e}")
        import traceback
        traceback.print_exc()

def analizar_aplicacion_contextual(ventana_activa, usuario):
    """Analiza la aplicación activa y da consejos contextuales"""
    consejos = []

    # Detectar aplicaciones de escritura y documentación
    if any(app in ventana_activa for app in ['word', 'excel', 'powerpoint', 'notepad', 'wordpad', 'libreoffice', 'google docs', 'notion', 'evernote']):
        consejos.extend(analizar_escritura_documentacion(ventana_activa, usuario))

    # Detectar Excel específicamente
    elif 'excel' in ventana_activa or 'spreadsheet' in ventana_activa:
        consejos.extend(analizar_excel_formulas(ventana_activa, usuario))

    # Detectar navegadores web
    elif any(browser in ventana_activa for browser in ['chrome', 'firefox', 'edge', 'safari', 'opera']):
        consejos.extend(analizar_navegacion_web(ventana_activa, usuario))

    # Detectar IDEs de desarrollo
    elif any(ide in ventana_activa for ide in ['vscode', 'visual studio', 'pycharm', 'intellij', 'eclipse', 'sublime', 'atom']):
        consejos.extend(analizar_desarrollo_codigo(ventana_activa, usuario))

    # Detectar aplicaciones de comunicación
    elif any(comm in ventana_activa for comm in ['outlook', 'gmail', 'teams', 'slack', 'discord', 'whatsapp', 'telegram']):
        consejos.extend(analizar_comunicacion(ventana_activa, usuario))

    return consejos

def analizar_escritura_documentacion(ventana_activa, usuario):
    """Consejos para escritura y documentación"""
    consejos = []

    # Analizar tiempo dedicado a documentación
    actividades_escritura = ActividadUsuario.objects.filter(
        usuario=usuario,
        ventana_activa__icontains='word',
        timestamp__gte=timezone.now() - timezone.timedelta(hours=2)
    ).count()

    if actividades_escritura > 20:
        consejos.append("Has estado mucho tiempo escribiendo. Considera hacer una pausa de 5 minutos para descansar la vista")

    # Verificar si es hora pico de productividad
    hora_actual = timezone.now().hour
    if 9 <= hora_actual <= 12:
        consejos.append("Excelente momento para trabajar en documentación - tu concentración está en su punto máximo")

    return consejos

def analizar_excel_formulas(ventana_activa, usuario):
    """Consejos específicos para trabajo con Excel"""
    consejos = []

    # Analizar tiempo en Excel
    tiempo_excel = ActividadUsuario.objects.filter(
        usuario=usuario,
        ventana_activa__icontains='excel',
        timestamp__gte=timezone.now() - timezone.timedelta(hours=1)
    ).count()

    if tiempo_excel > 30:
        consejos.append("Llevas tiempo considerable en Excel. Recuerda guardar frecuentemente tu trabajo")
        consejos.append("Considera usar atajos de teclado: Ctrl+S (guardar), F2 (editar celda), Ctrl+Z (deshacer)")

    # Consejos de mejores prácticas
    consejos.append("Tip: Usa referencias absolutas ($) en fórmulas cuando necesites bloquear filas/columnas")
    consejos.append("Recuerda validar tus fórmulas con datos de prueba antes de aplicar a toda la hoja")

    return consejos

def analizar_navegacion_web(ventana_activa, usuario):
    """Consejos para navegación web productiva"""
    consejos = []

    # Verificar si hay muchas pestañas abiertas (basado en tiempo de actividad)
    actividad_web = ActividadUsuario.objects.filter(
        usuario=usuario,
        ventana_activa__icontains='chrome',
        timestamp__gte=timezone.now() - timezone.timedelta(minutes=30)
    )

    if actividad_web.count() > 15:
        consejos.append("Tienes muchas pestañas abiertas. Considera organizarlas o cerrar las que no necesitas")

    # Consejos de productividad web
    hora_actual = timezone.now().hour
    if hora_actual >= 14 and hora_actual <= 16:
        consejos.append("Hora de la siesta mental. Si sientes fatiga, toma un descanso breve")

    return consejos

def analizar_desarrollo_codigo(ventana_activa, usuario):
    """Consejos para desarrollo de software"""
    consejos = []

    # Analizar tiempo de codificación
    tiempo_codificando = ActividadUsuario.objects.filter(
        usuario=usuario,
        ventana_activa__icontains__in=['vscode', 'pycharm', 'visual studio'],
        timestamp__gte=timezone.now() - timezone.timedelta(hours=2)
    ).count()

    if tiempo_codificando > 40:
        consejos.append("Has estado codificando intensamente. Recuerda hacer commits frecuentes y descansar la vista")
        consejos.append("Tip: Usa Ctrl+K Ctrl+C para comentar líneas, Ctrl+K Ctrl+U para descomentrar")

    # Consejos de mejores prácticas
    consejos.append("Recuerda escribir tests para tu código - mejora la calidad y mantenibilidad")
    consejos.append("Usa nombres descriptivos para variables y funciones - tu yo futuro te lo agradecerá")

    return consejos

def analizar_comunicacion(ventana_activa, usuario):
    """Consejos para comunicación digital"""
    consejos = []

    # Analizar tiempo en comunicación
    tiempo_comunicacion = ActividadUsuario.objects.filter(
        usuario=usuario,
        ventana_activa__icontains__in=['outlook', 'teams', 'slack'],
        timestamp__gte=timezone.now() - timezone.timedelta(hours=1)
    ).count()

    if tiempo_comunicacion > 25:
        consejos.append("Has dedicado mucho tiempo a comunicación. Asegúrate de equilibrar con trabajo productivo")

    # Consejos de comunicación efectiva
    consejos.append("Recuerda ser claro y conciso en tus mensajes - la brevedad aumenta la efectividad")

    return consejos

def analizar_patron_productividad(usuario, timestamp):
    """Analiza patrones de productividad y da consejos"""
    consejos = []

    # Asegurar que timestamp sea datetime
    if isinstance(timestamp, str):
        try:
            timestamp = timezone.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            timestamp = timezone.now()

    # Análisis de la última hora
    actividades_recientes = ActividadUsuario.objects.filter(
        usuario=usuario,
        timestamp__gte=timestamp - timezone.timedelta(hours=1)
    )

    productiva = actividades_recientes.filter(productividad='productive').count()
    improductiva = actividades_recientes.filter(productividad='unproductive').count()
    gaming = actividades_recientes.filter(productividad='gaming').count()
    neutral = actividades_recientes.filter(productividad='neutral').count()

    total = actividades_recientes.count()

    if total > 5:
        ratio_productividad = productiva / total if total > 0 else 0

        if ratio_productividad < 0.3:
            consejos.append("Tu productividad está baja. Considera identificar y eliminar distracciones")
            consejos.append("Técnica Pomodoro: 25 minutos de trabajo enfocado, 5 minutos de descanso")

        if improductiva > productiva:
            consejos.append("Estás dedicando más tiempo a actividades no productivas. Revisa tus prioridades")

        if gaming > 0 and timestamp.hour < 18:
            consejos.append("Detección de juegos durante horario laboral. Considera posponer el entretenimiento")

    return consejos

def analizar_tiempo_trabajo(usuario, timestamp):
    """Analiza patrones de tiempo y fatiga"""
    consejos = []

    # Calcular tiempo total de actividad hoy
    hoy = timestamp.date()
    actividades_hoy = ActividadUsuario.objects.filter(
        usuario=usuario,
        timestamp__date=hoy
    ).count()

    # Estimar tiempo real (cada actividad representa ~30 segundos)
    tiempo_trabajo_minutos = (actividades_hoy * 30) / 60

    if tiempo_trabajo_minutos > 480:  # Más de 8 horas
        consejos.append("Has trabajado más de 8 horas hoy. Es importante descansar para mantener la productividad")

    elif tiempo_trabajo_minutos > 360:  # Más de 6 horas
        consejos.append("Llevas varias horas trabajando. Considera un descanso de 10-15 minutos")

    # Análisis de hora del día
    hora = timestamp.hour

    if hora >= 22 or hora <= 6:
        consejos.append("Estás trabajando fuera del horario habitual. Asegúrate de descansar adecuadamente")

    elif 12 <= hora <= 14:
        consejos.append("Hora del almuerzo. Una comida balanceada mejora la concentración de la tarde")

    elif 17 <= hora <= 19:
        consejos.append("Finalizando la jornada. Revisa tus logros del día y planifica el siguiente")

    return consejos

def generar_consejos_proactivos(usuario):
    """Genera consejos proactivos basados en la actividad actual del usuario"""
    try:
        # Obtener actividad más reciente
        actividad_reciente = ActividadUsuario.objects.filter(
            usuario=usuario
        ).order_by('-timestamp').first()

        if not actividad_reciente:
            return None

        consejos = []
        ventana_activa = actividad_reciente.ventana_activa.lower() if actividad_reciente.ventana_activa else ""
        timestamp = actividad_reciente.timestamp

        # Asegurar que timestamp sea datetime
        if isinstance(timestamp, str):
            try:
                timestamp = timezone.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                timestamp = timezone.now()

        # Consejos basados en tiempo continuado en la misma aplicación
        tiempo_en_app = ActividadUsuario.objects.filter(
            usuario=usuario,
            ventana_activa__iexact=actividad_reciente.ventana_activa,
            timestamp__gte=timezone.now() - timezone.timedelta(minutes=30)
        ).count()

        if tiempo_en_app > 20:  # Más de 10 minutos continuados
            if 'excel' in ventana_activa:
                consejos.append("⏰ Llevas tiempo considerable en Excel. ¿Necesitas ayuda con alguna fórmula específica?")
            elif 'word' in ventana_activa:
                consejos.append("⏰ Estás trabajando intensamente en el documento. ¿Quieres consejos de formato o estructura?")
            elif any(ide in ventana_activa for ide in ['vscode', 'pycharm', 'visual studio']):
                consejos.append("⏰ Sesión de codificación prolongada. ¿Necesitas ayuda con debugging o mejores prácticas?")
            elif any(browser in ventana_activa for browser in ['chrome', 'firefox', 'edge']):
                consejos.append("⏰ Mucho tiempo navegando. ¿Estás investigando algo específico o necesitas organizar mejor tus pestañas?")

        # Consejos basados en patrones de productividad
        actividades_ultima_hora = ActividadUsuario.objects.filter(
            usuario=usuario,
            timestamp__gte=timezone.now() - timezone.timedelta(hours=1)
        )

        productiva = actividades_ultima_hora.filter(productividad='productive').count()
        improductiva = actividades_ultima_hora.filter(productividad='unproductive').count()
        total = actividades_ultima_hora.count()

        if total > 10:
            ratio_productividad = productiva / total
            if ratio_productividad < 0.4:
                consejos.append("📊 Tu productividad ha bajado. ¿Hay alguna distracción que pueda ayudarte a eliminar?")
                consejos.append("💡 Prueba la Técnica Pomodoro: 25 min trabajo + 5 min descanso")

        # Consejos basados en hora del día
        hora = timezone.now().hour
        if hora == 11:
            consejos.append("🌅 Hora del café matutino. Un descanso breve puede recargar tu energía")
        elif hora == 14:
            consejos.append("🍽️ Hora del almuerzo. Una comida balanceada mejora la concentración de la tarde")
        elif hora == 17:
            consejos.append("🌅 Finalizando la jornada. ¿Has revisado tus objetivos del día?")
        elif hora >= 18:
            consejos.append("🏠 Considera finalizar tus tareas pendientes. Mañana será otro día productivo")

        # Consejos basados en estadísticas personales
        try:
            estadistica = Estadistica.objects.get(usuario=usuario)
            if estadistica.puntaje < 50:
                consejos.append("📈 Tu puntuación de productividad es baja. ¿Quieres que te ayude a mejorar?")
        except Estadistica.DoesNotExist:
            consejos.append("📊 ¡Bienvenido! Te ayudaré a mejorar tu productividad. Empecemos con algunos consejos básicos")

        # Si hay consejos, crear análisis proactivo
        if consejos:
            recomendacion_texto = " | ".join(consejos)

            # Evitar consejos duplicados recientes (últimos 5 minutos)
            consejo_reciente = IAAnalisis.objects.filter(
                usuario=usuario,
                fecha_analisis__gte=timezone.now() - timezone.timedelta(minutes=5),
                patrones_detectados__tipo='proactivo'
            ).exists()

            if not consejo_reciente:
                IAAnalisis.objects.create(
                    usuario=usuario,
                    recomendacion=recomendacion_texto,
                    patrones_detectados={
                        'tipo': 'proactivo',
                        'ventana_activa': actividad_reciente.ventana_activa,
                        'hora_actual': hora,
                        'tiempo_en_app': tiempo_en_app,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                return recomendacion_texto

    except Exception as e:
        print(f"Error generando consejos proactivos: {e}")

    return None

def actualizar_estadisticas_inteligentes(actividad):
    """Actualiza estadísticas de manera inteligente basada en la actividad"""
    try:
        stat, created = Estadistica.objects.get_or_create(usuario=actividad.usuario)

        # Puntuación basada en productividad
        if actividad.productividad == 'productive':
            stat.puntaje = min(100, stat.puntaje + 1)
        elif actividad.productividad == 'unproductive':
            stat.puntaje = max(0, stat.puntaje - 2)
        elif actividad.productividad == 'gaming':
            stat.puntaje = max(0, stat.puntaje - 3)

        # Actualizar mejoras basadas en consistencia
        actividades_hoy = ActividadUsuario.objects.filter(
            usuario=actividad.usuario,
            timestamp__date=timezone.now().date(),
            productividad='productive'
        ).count()

        if actividades_hoy > 50:  # Buena jornada productiva
            stat.mejoras += 1

        stat.save()

    except Exception as e:
        print(f"Error actualizando estadísticas: {e}")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consejos_proactivos_api(request):
    """API para obtener consejos proactivos del asistente IA"""
    try:
        usuario = request.user

        # Generar consejos proactivos
        consejos = generar_consejos_proactivos(usuario)

        if consejos:
            return Response({
                'consejos': consejos,
                'timestamp': timezone.now().isoformat(),
                'tipo': 'proactivo'
            })
        else:
            return Response({
                'consejos': None,
                'mensaje': 'No hay consejos disponibles en este momento'
            })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# API de login para cliente Electron con auto-inicio
@api_view(['GET'])
def health_check(request):
    """Endpoint simple de health check para Docker"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'sara-backend'
    })

# API de login para cliente Electron con auto-inicio
@api_view(['POST'])
def login_api(request):
    """API de login para el cliente de monitoreo - inicia automáticamente"""
    username = request.data.get('username')
    password = request.data.get('password')
    auto_start = request.data.get('auto_start', True)  # Por defecto auto-inicia

    if not username or not password:
        return Response(
            {'error': 'Usuario y contraseña son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)

        # Crear registro de inicio de sesión para monitoreo automático
        Registro.objects.create(
            usuario=user,
            contenido={
                "tipo": "login_auto",
                "descripcion": "Inicio de sesión automático - Cliente activado",
                "auto_start": auto_start,
                "timestamp": timezone.now().isoformat()
            },
            fecha=timezone.now().date()
        )

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'rol': getattr(user, 'rol', 'empleado')
            },
            'auto_start': auto_start,
            'monitoring_enabled': True,  # Siempre habilitado, no se puede pausar
            'message': 'Monitoreo iniciado automáticamente. Solo puedes detenerlo con logout.'
        })
    else:
        return Response(
            {'error': 'Credenciales inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )

# Interfaz Web del Asistente Virtual (sin instalar nada local)
@login_required
def asistente_web_interface(request):
    """Interfaz web del asistente virtual - no requiere instalación local"""
    return render(request, 'core/asistente_web.html', {
        'user': request.user,
        'api_url': '/api',
    })

def generar_respuesta_ortografia(mensaje, usuario):
    """Ayuda con ortografía y escritura"""
    mensaje_lower = mensaje.lower()

    # Detectar preguntas sobre ortografía específica
    if 'se escribe' in mensaje_lower or 'como se escribe' in mensaje_lower:
        return "📝 ¡Claro! Puedo ayudarte con ortografía. ¿Qué palabra o frase específica quieres que revise?"

    # Detectar palabras específicas mencionadas
    palabras = ['es', 'oyo', 'hoyo', 'hoy', 'oy', 'vez', 'aves', 'aves', 'b', 'v', 's', 'z', 'c', 'g', 'j', 'll', 'y', 'rr']

    for palabra in palabras:
        if palabra in mensaje_lower:
            if palabra in ['es', 'oyo', 'hoyo']:
                return f"📝 Sobre la palabra '{palabra}':\n\n• 'Es' = verbo ser/estar (Ej: Él es alto)\n• 'Es' nunca lleva acento\n• 'Oyo' = forma del verbo oír (Ej: Yo oyo música)\n• 'Hoyo' = agujero o depresión (Ej: Hay un hoyo en la calle)\n\n¿Quieres que te ayude con alguna palabra específica?"

    # Respuesta general sobre ortografía
    return """📝 ¡Claro! Puedo ayudarte con ortografía y escritura. Algunos consejos importantes:

🔤 **Reglas básicas de ortografía:**
• B/V: Usa 'b' antes de consonantes y 'v' antes de vocales
• S/Z: 'S' para sonidos suaves, 'Z' para sonidos fuertes
• C/G/J: 'C' antes de a/o/u, 'G' antes de e/i, 'J' para sonido fuerte
• LL/Y: 'LL' para sonido palatal, 'Y' para conjunción
• RR: Para sonido fuerte de 'r'

📚 **Palabras confusas comunes:**
• 'Es' (verbo) vs 'és' (no existe)
• 'Oyo' (verbo oír) vs 'hoyo' (agujero)
• 'Aver' (verbo) vs 'haber' (verbo auxiliar)
• 'Valla' (cerca) vs 'baya' (fruto)

¿Sobre qué palabra o regla específica necesitas ayuda?"""
