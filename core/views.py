from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
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
@permission_classes([AllowAny])
def login_api(request):
    """API endpoint para login de usuarios"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'error': 'Usuario y contraseña son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'rol': user.rol,
                    'is_active': user.is_active
                },
                'message': 'Login exitoso'
            })
        else:
            return Response({
                'error': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consejos_proactivos_api(request):
    """API para obtener consejos proactivos basados en la actividad del usuario"""
    try:
        user = request.user

        # Obtener actividad reciente
        actividad_reciente = ActividadUsuario.objects.filter(
            usuario=user
        ).order_by('-timestamp').first()

        # Obtener estadísticas recientes
        estadisticas = Estadistica.objects.filter(usuario=user).last()

        # Generar consejos basados en el contexto
        consejos = []

        # Consejos basados en actividad actual
        if actividad_reciente:
            tiempo_desde_actividad = timezone.now() - actividad_reciente.timestamp
            minutos_inactivo = tiempo_desde_actividad.seconds // 60

            if minutos_inactivo > 60:
                consejos.append("¡Hace tiempo que no detecto actividad! Considera tomar un descanso breve o cambiar de tarea.")
            elif minutos_inactivo > 30:
                consejos.append("Llevas un rato trabajando. ¿Quieres consejos para mantener la concentración?")

            # Consejos basados en aplicación activa
            if actividad_reciente.ventana_activa:
                app = actividad_reciente.ventana_activa.lower()
                if 'excel' in app and actividad_reciente.productividad == 'unproductive':
                    consejos.append("Veo que estás trabajando en Excel pero con baja productividad. ¿Necesitas ayuda con alguna fórmula?")
                elif 'word' in app:
                    consejos.append("Trabajando en documentos. Recuerda guardar automáticamente cada 5 minutos.")

        # Consejos basados en estadísticas
        if estadisticas:
            if estadisticas.puntaje < 50:
                consejos.append("Tu puntuación de productividad es baja. Establece metas diarias realistas para mejorar.")
            elif estadisticas.puntaje > 80:
                consejos.append("¡Excelente rendimiento! Mantén el ritmo y comparte tus mejores prácticas.")

        # Consejos generales si no hay específicos
        if not consejos:
            consejos = [
                "Recuerda la Técnica Pomodoro: 25 minutos de trabajo + 5 minutos de descanso.",
                "Mantén una buena postura para evitar fatiga.",
                "Bebe agua regularmente durante tu jornada laboral.",
                "Toma descansos para estirarte cada hora."
            ]

        # Seleccionar 1-2 consejos aleatorios
        import random
        consejos_seleccionados = random.sample(consejos, min(2, len(consejos)))

        return Response({
            'consejos': ' | '.join(consejos_seleccionados),
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def analizar_intencion_mensaje(mensaje):
    """Analiza la intención del mensaje del usuario"""
    mensaje_lower = mensaje.lower()

    # Patrones de saludo
    saludos = ['hola', 'buenos', 'buenas', 'saludos', 'hey', 'hi', 'hello', 'buen dia', 'buenas tardes', 'buenas noches']
    if any(saludo in mensaje_lower for saludo in saludos):
        return 'saludo'

    # Preguntas personales
    preguntas_personales = ['como te llamas', 'quien eres', 'qué eres', 'que eres', 'tu nombre']
    if any(pregunta in mensaje_lower for pregunta in preguntas_personales):
        return 'pregunta_personal'

    # Peticiones de ayuda
    ayuda_palabras = ['ayuda', 'help', 'ayudame', 'necesito ayuda', 'puedes ayudarme']
    if any(ayuda in mensaje_lower for ayuda in ayuda_palabras):
        return 'ayuda'

    # Temas de productividad
    productividad_palabras = ['productividad', 'productivo', 'eficiencia', 'rendimiento', 'trabajo']
    if any(prod in mensaje_lower for prod in productividad_palabras):
        return 'productividad'

    # Errores y problemas
    error_palabras = ['error', 'problema', 'issue', 'bug', 'falla', 'no funciona']
    if any(error in mensaje_lower for error in error_palabras):
        return 'errores'

    # Excel y hojas de cálculo
    excel_palabras = ['excel', 'formula', 'fórmula', 'hoja', 'spreadsheet', 'calcul']
    if any(excel in mensaje_lower for excel in excel_palabras):
        return 'excel'

    # Gestión del tiempo
    tiempo_palabras = ['tiempo', 'horas', 'trabajo', 'horario', 'agenda', 'calendario']
    if any(tiempo in mensaje_lower for tiempo in tiempo_palabras):
        return 'tiempo'

    # Consejos y recomendaciones
    consejo_palabras = ['consejo', 'tip', 'recomendacion', 'sugerencia', 'mejorar']
    if any(consejo in mensaje_lower for consejo in consejo_palabras):
        return 'consejos'

    # Ortografía y escritura
    ortografia_palabras = ['escribir', 'escribe', 'ortografía', 'ortografia', 'palabra', 'palabras', 'se escribe', 'como se escribe']
    if any(orto in mensaje_lower for orto in ortografia_palabras):
        return 'ortografia'

    # Estado y situación actual
    estado_palabras = ['estado', 'status', 'situación', 'situacion', 'como estas', 'que haces']
    if any(estado in mensaje_lower for estado in estado_palabras):
        return 'estado'

    # Operaciones matemáticas simples
    if any(op in mensaje_lower for op in ['+', '-', '*', '/', '=', 'mas', 'menos', 'por', 'entre']):
        return 'matematicas'

    # Preguntas (contienen signos de interrogación)
    if '?' in mensaje or mensaje_lower.startswith(('como', 'qué', 'que', 'cuando', 'donde', 'por qué', 'porque', 'para qué', 'quién', 'quien')):
        return 'pregunta_general'

    # Preguntas sobre documentación o manuales
    documentacion_palabras = ['manual', 'documentacion', 'documentación', 'guia', 'guía', 'tutorial', 'como usar', 'instrucciones', 'ayuda con']
    if any(doc in mensaje_lower for doc in documentacion_palabras):
        return 'documentacion'

    # Preguntas sobre configuración o setup
    config_palabras = ['configurar', 'configuracion', 'configuración', 'instalar', 'setup', 'set up', 'como configurar']
    if any(config in mensaje_lower for config in config_palabras):
        return 'configuracion'

    # Preguntas sobre reportes o estadísticas
    reporte_palabras = ['reporte', 'estadistica', 'estadística', 'grafico', 'gráfico', 'analisis', 'análisis', 'dashboard']
    if any(rep in mensaje_lower for rep in reporte_palabras):
        return 'reportes'

    # Preguntas sobre equipo o colaboración
    equipo_palabras = ['equipo', 'compañeros', 'compañeros', 'colaboracion', 'colaboración', 'trabajo en equipo']
    if any(equipo in mensaje_lower for equipo in equipo_palabras):
        return 'equipo'

    # Preguntas sobre salud o bienestar
    salud_palabras = ['salud', 'bienestar', 'estres', 'estrés', 'cansado', 'agotado', 'descanso', 'pausa']
    if any(salud in mensaje_lower for salud in salud_palabras):
        return 'salud'

    # Preguntas sobre metas o objetivos
    metas_palabras = ['meta', 'objetivo', 'goal', 'logro', 'progreso', 'avance', 'mejora']
    if any(meta in mensaje_lower for meta in metas_palabras):
        return 'metas'

    return 'general'

def generar_respuesta_asistente(usuario, mensaje, contexto):
    """Genera respuesta inteligente del asistente basada en el contexto del usuario"""
    mensaje_lower = mensaje.lower().strip()

    # Obtener actividad reciente del usuario para contexto
    actividad_reciente = ActividadUsuario.objects.filter(
        usuario=usuario
    ).order_by('-timestamp').first()

    ventana_activa = ""
    if actividad_reciente:
        ventana_activa = actividad_reciente.ventana_activa.lower() if actividad_reciente.ventana_activa else ""

    # Análisis de intención del mensaje con mejor precisión
    intencion = analizar_intencion_mensaje(mensaje_lower)

    # Respuestas específicas basadas en intención detectada
    if intencion == 'saludo':
        return generar_respuesta_saludo(usuario, contexto)

    elif intencion == 'pregunta_personal':
        return generar_respuesta_pregunta_personal(mensaje_lower, usuario)

    elif intencion == 'ayuda':
        return generar_respuesta_ayuda_contextual(usuario, contexto, ventana_activa)

    elif intencion == 'productividad':
        return generar_respuesta_productividad_detallada(usuario, ventana_activa)

    elif intencion == 'errores':
        return generar_respuesta_errores_detallada(usuario)

    elif intencion == 'excel':
        return generar_respuesta_excel_contextual(ventana_activa)

    elif intencion == 'tiempo':
        return generar_respuesta_tiempo_detallada(usuario)

    elif intencion == 'consejos':
        return generar_respuesta_consejos_personalizados(usuario, ventana_activa)

    elif intencion == 'ortografia':
        return generar_respuesta_ortografia_detallada(mensaje_lower, usuario)

    elif intencion == 'estado':
        return generar_respuesta_estado_actual(usuario, actividad_reciente)

    elif intencion == 'matematicas':
        return generar_respuesta_matematicas(mensaje_lower)

    elif intencion == 'documentacion':
        return generar_respuesta_documentacion()

    elif intencion == 'configuracion':
        return generar_respuesta_configuracion()

    elif intencion == 'reportes':
        return generar_respuesta_reportes(usuario)

    elif intencion == 'equipo':
        return generar_respuesta_equipo(usuario)

    elif intencion == 'salud':
        return generar_respuesta_salud()

    elif intencion == 'metas':
        return generar_respuesta_metas(usuario)

    else:
        # Respuesta inteligente basada en contexto de actividad
        return generar_respuesta_contextual_inteligente(mensaje_lower, usuario, ventana_activa, actividad_reciente)

def generar_respuesta_saludo(usuario, contexto):
    """Genera respuesta de saludo personalizada"""
    nombre = usuario.get_full_name() or usuario.username

    # Obtener hora del día para saludo contextual
    hora_actual = timezone.now().hour
    if hora_actual < 12:
        saludo_tiempo = "buenos días"
    elif hora_actual < 18:
        saludo_tiempo = "buenas tardes"
    else:
        saludo_tiempo = "buenas noches"

    # Obtener actividad reciente para contexto
    actividad_reciente = ActividadUsuario.objects.filter(
        usuario=usuario
    ).order_by('-timestamp').first()

    contexto_actividad = ""
    if actividad_reciente and actividad_reciente.ventana_activa:
        app = actividad_reciente.ventana_activa.lower()
        if 'excel' in app:
            contexto_actividad = " Veo que estás trabajando con Excel. ¿Necesitas ayuda con alguna fórmula?"
        elif 'word' in app:
            contexto_actividad = " Parece que estás editando un documento. ¿Necesitas consejos de formato?"
        elif any(ide in app for ide in ['vscode', 'pycharm', 'visual studio']):
            contexto_actividad = " Estás programando. ¿Puedo ayudarte con algún problema de código?"

    respuesta = f"¡{saludo_tiempo}, {nombre}! 👋\n\nSoy SARA, tu asistente personal de IA. Estoy aquí para ayudarte a ser más productivo y eficiente en tu trabajo.{contexto_actividad}\n\n¿En qué puedo ayudarte hoy?"

    return respuesta

def generar_respuesta_pregunta_personal(mensaje, usuario):
    """Responde preguntas personales sobre el asistente"""
    if 'como te llamas' in mensaje.lower() or 'tu nombre' in mensaje.lower():
        return "¡Hola! Me llamo SARA, que significa 'Sistema de Asistencia y Recomendaciones Automatizadas'. Soy tu asistente personal de IA diseñado para ayudarte a mejorar tu productividad laboral. ¿En qué puedo ayudarte?"

    elif 'quien eres' in mensaje.lower() or 'qué eres' in mensaje.lower():
        nombre = usuario.get_full_name() or usuario.username
        return f"Soy SARA, tu asistente personal de IA, {nombre}. Estoy diseñada para:\n\n• 💡 Analizar tu productividad y dar consejos personalizados\n• 📊 Monitorear tu actividad laboral en tiempo real\n• 🔧 Ayudarte con problemas técnicos y herramientas\n• ⏰ Gestionar mejor tu tiempo de trabajo\n• 📈 Mejorar tu rendimiento profesional\n\n¿Te gustaría que te muestre tu estado actual de productividad?"

    return "Soy SARA, tu asistente personal de IA. ¿Qué más te gustaría saber sobre mí?"

def generar_respuesta_ayuda_contextual(usuario, contexto, ventana_activa):
    """Genera ayuda contextual basada en la actividad actual"""
    nombre = usuario.get_full_name() or usuario.username

    # Análisis de actividad actual
    ayuda_especifica = ""
    if ventana_activa:
        if 'excel' in ventana_activa:
            ayuda_especifica = "\n\n📊 Como estás trabajando con Excel, puedo ayudarte con:\n• Fórmulas y funciones avanzadas\n• Consejos de formato y presentación\n• Análisis de datos y gráficos"
        elif 'word' in ventana_activa:
            ayuda_especifica = "\n\n📝 Estás trabajando en un documento. Puedo ayudarte con:\n• Formato y estilos\n• Estructura de documentos\n• Consejos de redacción"
        elif any(ide in ventana_activa for ide in ['vscode', 'pycharm', 'visual studio']):
            ayuda_especifica = "\n\n💻 Veo que estás programando. Puedo ayudarte con:\n• Debugging y resolución de errores\n• Mejores prácticas de código\n• Optimización de rendimiento"

    respuesta = f"¡Claro que sí, {nombre}! Estoy aquí para ayudarte. 😊{ayuda_especifica}\n\nPuedo asistirte con:\n\n🚀 **Productividad**\n• Análisis de tu rendimiento laboral\n• Consejos para mejorar la eficiencia\n• Gestión del tiempo\n\n📊 **Herramientas**\n• Excel: fórmulas, funciones, análisis de datos\n• Programación: debugging, mejores prácticas\n• Documentos: formato, estructura\n\n🔧 **Problemas**\n• Resolución de errores técnicos\n• Solución de problemas\n• Guías paso a paso\n\n💡 **Consejos**\n• Recomendaciones personalizadas\n• Tips basados en tu actividad\n• Mejores prácticas\n\n¿Sobre qué tema específico necesitas ayuda?"

    return respuesta

def generar_respuesta_productividad_detallada(usuario, ventana_activa):
    """Genera consejos de productividad detallados y contextuales"""
    # Obtener estadísticas recientes del usuario
    estadisticas = Estadistica.objects.filter(usuario=usuario).last()

    # Análisis de actividad reciente
    actividades_hoy = ActividadUsuario.objects.filter(
        usuario=usuario,
        timestamp__date=timezone.now().date()
    )

    productiva = actividades_hoy.filter(productividad='productive').count()
    improductiva = actividades_hoy.filter(productividad='unproductive').count()
    gaming = actividades_hoy.filter(productividad='gaming').count()
    total_actividades = actividades_hoy.count()

    # Calcular ratio de productividad
    ratio_productividad = (productiva / total_actividades * 100) if total_actividades > 0 else 0

    # Consejos basados en aplicación activa
    consejos_app = ""
    if ventana_activa:
        if 'excel' in ventana_activa:
            consejos_app = "\n\n📊 Como estás trabajando con Excel, aquí van consejos específicos:\n• Guarda automáticamente cada 5 minutos (Ctrl+S)\n• Usa nombres descriptivos para tus rangos\n• Valida tus fórmulas con datos de prueba"
        elif any(ide in ventana_activa for ide in ['vscode', 'pycharm', 'visual studio']):
            consejos_app = "\n\n💻 Para desarrollo de software:\n• Escribe tests antes de implementar funcionalidades\n• Haz commits pequeños con mensajes descriptivos\n• Revisa tu código antes de hacer push"

    if estadisticas:
        puntaje = estadisticas.puntaje

        if ratio_productividad >= 70:
            nivel = "¡Excelente trabajo! Mantén ese ritmo."
            consejos_especificos = [
                "• Continúa con la técnica que estás usando",
                "• Comparte tus mejores prácticas con el equipo",
                "• Establece metas aún más ambiciosas"
            ]
        elif ratio_productividad >= 50:
            nivel = "Buen progreso, pero hay margen de mejora."
            consejos_especificos = [
                "• Identifica qué aplicaciones te distraen más",
                "• Implementa la Técnica Pomodoro: 25min trabajo + 5min descanso",
                "• Revisa tus notificaciones y silencia las innecesarias"
            ]
        else:
            nivel = "Necesitas enfocarte más en tareas productivas."
            consejos_especificos = [
                "• Crea una lista de tareas prioritarias para hoy",
                "• Elimina distracciones del entorno",
                "• Establece bloques de tiempo dedicados a tareas específicas"
            ]

        respuesta = f"""📊 Análisis de Productividad Detallado:

🎯 Tu puntuación actual: {puntaje}/100 puntos
📈 Productividad hoy: {ratio_productividad:.1f}% ({productiva}/{total_actividades} actividades productivas)
🏆 Nivel: {nivel}

💡 Consejos personalizados:{consejos_app}
{chr(10).join(consejos_especificos)}

🔍 Aplicaciones más usadas hoy:
{generar_resumen_aplicaciones(actividades_hoy)}

¿Quieres que te ayude con alguna técnica específica de productividad?"""
    else:
        respuesta = f"""📊 Análisis de Productividad:

Aún no tengo suficientes datos para analizar tu productividad específica, pero aquí van consejos generales basados en las mejores prácticas:

💡 Estrategias comprobadas:
• Técnica Pomodoro: 25 minutos de trabajo enfocado + 5 minutos de descanso
• Regla 2 minutos: Si algo toma menos de 2 minutos, hazlo ahora
• Método Eisenhower: Prioriza tareas por urgencia e importancia
• Time-blocking: Asigna bloques específicos de tiempo a tareas

📱 Gestión de distracciones:
• Revisa email solo 3 veces al día
• Usa modo 'No molestar' durante trabajo enfocado
• Cierra aplicaciones innecesarias

🎯 Metas diarias:
• Define 3 tareas principales para el día
• Revisa progreso cada 2 horas
• Celebra logros al final del día{consejos_app}

¡Empieza a trabajar y te daré análisis más personalizados basados en tu actividad real!"""

    return respuesta

def generar_resumen_aplicaciones(actividades):
    """Genera un resumen de las aplicaciones más usadas"""
    if not actividades.exists():
        return "No hay datos de actividad aún."

    # Contar aplicaciones más usadas
    apps_mas_usadas = actividades.values('ventana_activa').annotate(
        count=Count('ventana_activa')
    ).order_by('-count')[:5]

    resumen = ""
    for app in apps_mas_usadas:
        nombre_app = app['ventana_activa'] or 'Desconocido'
        count = app['count']
        resumen += f"• {nombre_app}: {count} actividades\n"

    return resumen.strip()

def generar_respuesta_errores_detallada(usuario):
    """Ayuda detallada con resolución de errores"""
    # Buscar errores recientes en registros del usuario
    registros_con_errores = Registro.objects.filter(
        usuario=usuario,
        errores__isnull=False
    ).order_by('-fecha')[:5]

    if registros_con_errores.exists():
        respuesta = "🔍 Análisis de Errores Recientes:\n\n"

        for i, registro in enumerate(registros_con_errores, 1):
            errores = registro.errores
            respuesta += f"{i}. 📝 Registro del {registro.fecha.strftime('%d/%m/%Y')}:\n"

            if isinstance(errores, list):
                for error in errores:
                    if isinstance(error, dict):
                        campo = error.get('campo', 'General')
                        mensaje = error.get('mensaje', 'Error detectado')
                        respuesta += f"   • Campo '{campo}': {mensaje}\n"
                    else:
                        respuesta += f"   • {error}\n"
            else:
                respuesta += f"   • {errores}\n"

            respuesta += "\n"

        respuesta += "💡 ¿Quieres que te ayude a corregir alguno de estos errores específicos?"
    else:
        respuesta = """✅ No encontré errores recientes en tus registros.

🔧 Si tienes algún problema técnico, puedo ayudarte con:

📊 **Excel/Spreadsheets:**
• Errores en fórmulas (#DIV/0!, #VALUE!, #REF!)
• Problemas de formato o validación
• Errores de importación/exportación

💻 **Programación:**
• Errores de sintaxis
• Problemas de lógica
• Errores de dependencias

🖥️ **Sistema/General:**
• Problemas de configuración
• Errores de permisos
• Problemas de conectividad

📝 **Datos:**
• Errores de validación
• Problemas de formato
• Inconsistencias en datos

¿Cuál es el problema específico que estás experimentando? Cuéntame los detalles y te ayudo a solucionarlo."""

    return respuesta

def generar_respuesta_excel_contextual(ventana_activa):
    """Consejos contextuales para Excel"""
    # Verificar si el usuario está trabajando actualmente con Excel
    trabajando_excel = 'excel' in ventana_activa.lower() if ventana_activa else False

    if trabajando_excel:
        consejos = [
            "📊 Excel - Ayuda Contextual:",
            "",
            "Como veo que estás trabajando con Excel ahora mismo, aquí van consejos específicos:",
            "",
            "🔧 Atajos esenciales para trabajar más rápido:",
            "• Ctrl + S: Guardar (úsalo cada 2-3 minutos)",
            "• F2: Editar celda activa",
            "• Ctrl + Z/Y: Deshacer/Rehacer",
            "• Ctrl + C/V: Copiar/Pegar",
            "• Ctrl + Flecha: Ir al final de datos",
            "• Ctrl + Shift + L: Activar filtros",
            "",
            "📈 Funciones más útiles:",
            "• SUMA: =SUMA(rango) o =SUMA(A1:A10)",
            "• PROMEDIO: =PROMEDIO(rango)",
            "• CONTAR: =CONTAR(rango) para contar números",
            "• CONTARA: =CONTARA(rango) para contar todo",
            "• BUSCARV: =BUSCARV(valor, tabla, columna, FALSO)",
            "",
            "⚡ Mejores prácticas:",
            "• Usa referencias absolutas ($A$1) cuando necesites bloquear celdas",
            "• Nombra rangos importantes (Ctrl + F3)",
            "• Usa formato condicional para resaltar datos",
            "• Crea tablas (Ctrl + T) para datos organizados",
            "",
            "¿Qué función específica necesitas ayuda?"
        ]
    else:
        consejos = [
            "📊 Excel - Guía Completa:",
            "",
            "🔧 Atajos esenciales:",
            "• Ctrl + S: Guardar (¡úsalo frecuentemente!)",
            "• F2: Editar celda activa",
            "• Ctrl + Z: Deshacer",
            "• Ctrl + C/V: Copiar/Pegar",
            "• Ctrl + Flecha: Ir al final de datos",
            "",
            "📈 Fórmulas avanzadas:",
            "• SUMA.SI: =SUMA.SI(rango, criterio, rango_suma)",
            "• CONTAR.SI: =CONTAR.SI(rango, criterio)",
            "• SI: =SI(condición, valor_si_verdadero, valor_si_falso)",
            "• Y/O: =Y(cond1, cond2) o =O(cond1, cond2)",
            "• BUSCARV: =BUSCARV(valor, rango, columna, FALSO)",
            "",
            "🎨 Formato y presentación:",
            "• Formato condicional: Resaltar datos automáticamente",
            "• Tablas dinámicas: Análisis avanzado de datos",
            "• Gráficos: Visualización de información",
            "• Validación de datos: Controlar entrada de información",
            "",
            "¿Qué aspecto de Excel te gustaría que te explique?"
        ]

    return "\n".join(consejos)

def generar_respuesta_tiempo_detallada(usuario):
    """Análisis detallado de gestión del tiempo"""
    # Calcular tiempo de actividad hoy
    hoy = timezone.now().date()
    actividades_hoy = ActividadUsuario.objects.filter(
        usuario=usuario,
        timestamp__date=hoy
    )

    tiempo_trabajo_minutos = (actividades_hoy.count() * 30) // 60  # Estimación

    # Análisis por horas
    horas_analisis = []
    for hora in range(9, 18):  # De 9 AM a 5 PM
        actividades_hora = actividades_hoy.filter(
            timestamp__hour=hora
        )
        productiva_hora = actividades_hora.filter(productividad='productive').count()
        total_hora = actividades_hora.count()
        ratio = (productiva_hora / total_hora * 100) if total_hora > 0 else 0
        horas_analisis.append((hora, ratio, total_hora))

    # Encontrar hora más productiva
    hora_mas_productiva = max(horas_analisis, key=lambda x: x[1]) if horas_analisis else None

    # Estado general
    if tiempo_trabajo_minutos > 480:  # Más de 8 horas
        estado = "⚠️ Has trabajado mucho hoy. Es hora de descansar."
        color_estado = "warning"
    elif tiempo_trabajo_minutos > 360:  # Más de 6 horas
        estado = "⏰ Llevas varias horas trabajando. Considera un descanso."
        color_estado = "info"
    elif tiempo_trabajo_minutos > 240:  # Más de 4 horas
        estado = "📈 Buen ritmo de trabajo. ¡Sigue así!"
        color_estado = "success"
    else:
        estado = "🚀 ¡Empieza tu jornada productiva!"
        color_estado = "primary"

    respuesta = f"""⏱️ Análisis Detallado de Gestión del Tiempo:

📊 Tiempo estimado de trabajo hoy: {tiempo_trabajo_minutos} minutos
🎯 Estado actual: {estado}

📈 Análisis por horas de productividad:
"""

    for hora, ratio, total in horas_analisis:
        if total > 0:
            barra = "█" * int(ratio / 10)  # Barra visual
            respuesta += f"• {hora:2d}:00 - {hora+1:2d}:00: {ratio:5.1f}% productivo ({barra})\n"
        else:
            respuesta += f"• {hora:2d}:00 - {hora+1:2d}:00: Sin actividad\n"

    if hora_mas_productiva and hora_mas_productiva[1] > 0:
        respuesta += f"\n🏆 Tu hora más productiva hoy: {hora_mas_productiva[0]:2d}:00 - {hora_mas_productiva[0]+1:2d}:00 ({hora_mas_productiva[1]:.1f}%)\n"

    respuesta += f"""
💡 Estrategias de gestión del tiempo:

1. 📅 Planificación semanal:
   • Define objetivos claros para cada día
   • Prioriza tareas con la matriz Eisenhower
   • Reserva tiempo para imprevistos (20% del día)

2. 🎯 Técnica Pomodoro mejorada:
   • 25 minutos de trabajo enfocado
   • 5 minutos de descanso activo
   • Después de 4 ciclos: descanso de 15-30 min
   • Usa tu hora más productiva para tareas complejas

3. 📊 Seguimiento y ajuste:
   • Revisa logros al final del día
   • Identifica qué te robó tiempo
   • Ajusta tu rutina semanalmente

4. ⚡ Optimización diaria:
   • Agrupa tareas similares para eficiencia
   • Elimina reuniones innecesarias
   • Automatiza tareas repetitivas

5. 🧠 Salud y bienestar:
   • Toma descansos cada 90 minutos
   • Come y bebe agua regularmente
   • Mantén buena postura

¿Quieres que te ayude a crear un plan de tiempo específico para mañana?"""

    return respuesta

def generar_respuesta_consejos_personalizados(usuario, ventana_activa):
    """Genera consejos personalizados basados en actividad actual"""
    # Obtener análisis recientes del agente personal
    consejos_recientes = IAAnalisis.objects.filter(
        usuario=usuario,
        patrones_detectados__tipo="agente_personal"
    ).order_by('-fecha_analisis')[:3]

    # Obtener estadísticas para consejos contextuales
    estadisticas = Estadistica.objects.filter(usuario=usuario).last()

    respuesta = "💡 Consejos Personalizados:\n\n"

    # Consejos basados en aplicación activa
    if ventana_activa:
        if 'excel' in ventana_activa:
            respuesta += "📊 Como estás trabajando con Excel:\n"
            respuesta += "• Guarda automáticamente cada 5 minutos (Ctrl+S)\n"
            respuesta += "• Usa nombres descriptivos para tus rangos\n"
            respuesta += "• Valida tus fórmulas con datos de prueba\n\n"
        elif 'word' in ventana_activa:
            respuesta += "📝 Para trabajo con documentos:\n"
            respuesta += "• Usa estilos consistentes para formato\n"
            respuesta += "• Agrega tabla de contenidos para documentos largos\n"
            respuesta += "• Revisa ortografía antes de finalizar\n\n"
        elif any(ide in ventana_activa for ide in ['vscode', 'pycharm', 'visual studio']):
            respuesta += "💻 Para desarrollo de software:\n"
            respuesta += "• Escribe tests antes de implementar funcionalidades\n"
            respuesta += "• Haz commits pequeños con mensajes descriptivos\n"
            respuesta += "• Revisa tu código antes de hacer push\n\n"

    # Consejos basados en estadísticas
    if estadisticas:
        puntaje = estadisticas.puntaje
        if puntaje < 50:
            respuesta += "📈 Para mejorar tu productividad:\n"
            respuesta += "• Establece metas diarias realistas\n"
            respuesta += "• Elimina distracciones del entorno\n"
            respuesta += "• Usa técnicas de time-blocking\n\n"
        elif puntaje > 80:
            respuesta += "🏆 ¡Excelente rendimiento! Para mantenerlo:\n"
            respuesta += "• Comparte tus mejores prácticas\n"
            respuesta += "• Establece metas aún más desafiantes\n"
            respuesta += "• Ayuda a compañeros con tu experiencia\n\n"

    # Consejos del agente personal
    if consejos_recientes.exists():
        respuesta += "🎯 Consejos recientes de tu agente personal:\n"
        for i, consejo in enumerate(consejos_recientes, 1):
            recomendacion = consejo.recomendacion[:150] + "..." if len(consejo.recomendacion) > 150 else consejo.recomendacion
            respuesta += f"{i}. {recomendacion}\n"
        respuesta += "\n"

    respuesta += """🚀 Consejos generales para el éxito:

🧠 Productividad Mental:
• Practica la atención plena durante 5 minutos diarios
• Mantén una rutina de sueño consistente (7-8 horas)
• Haz ejercicio regular para mejorar concentración

📈 Desarrollo Profesional:
• Aprende una nueva habilidad cada mes
• Busca feedback constructivo regularmente
• Documenta tus logros y aprendizajes

🤝 Trabajo en Equipo:
• Comunica claramente tus ideas y expectativas
• Escucha activamente a tus compañeros
• Ofrece ayuda cuando veas oportunidades

💪 Resiliencia:
• Aprende de los errores, no te desanimes
• Mantén una actitud positiva ante desafíos
• Celebra los pequeños logros diariamente

¿Sobre qué área específica te gustaría recibir más consejos?"""

    return respuesta

def generar_respuesta_ortografia_detallada(mensaje, usuario):
    """Ayuda detallada con ortografía y escritura"""
    mensaje_lower = mensaje.lower()

    # Detectar palabras específicas mencionadas
    palabras_clave = {
        'es': ['es', 'hoy', 'vió', 'vió'],
        'mas': ['mas', 'más', 'mas'],
        'si': ['si', 'sí', 'si'],
        'tu': ['tu', 'tú', 'tu'],
        'el': ['el', 'él', 'el'],
        'aun': ['aun', 'aún', 'aun'],
        'solo': ['solo', 'sólo', 'solo'],
        'este': ['este', 'éste', 'este'],
        'ultimo': ['ultimo', 'último', 'ultimo']
    }

    palabras_encontradas = []
    for palabra_base, variaciones in palabras_clave.items():
        for variacion in variaciones:
            if variacion in mensaje_lower:
                palabras_encontradas.append(palabra_base)
                break

    if palabras_encontradas:
        respuesta = "📝 Análisis de ortografía:\n\n"
        for palabra in palabras_encontradas:
            if palabra == 'es':
                respuesta += "• 'Es' (sin acento): verbo ser/estar\n"
                respuesta += "  ❌ Hoy es un buen día\n"
                respuesta += "  ❌ Él es alto\n\n"
            elif palabra == 'mas':
                respuesta += "• 'Más' (con acento): comparación/superioridad\n"
                respuesta += "  ❌ Quiero mas tiempo\n"
                respuesta += "  ✅ Quiero más tiempo\n\n"
            elif palabra == 'si':
                respuesta += "• 'Sí' (con acento): afirmación\n"
                respuesta += "  ❌ Si, estoy de acuerdo\n"
                respuesta += "  ✅ Sí, estoy de acuerdo\n\n"
        respuesta += "¿Quieres que revise algún texto específico?"
    else:
        respuesta = """📝 Guía Completa de Ortografía y Escritura:

🔤 **Reglas básicas de acentuación:**

1. **Palabras agudas** (acento en última sílaba):
   • Llevan acento si terminan en vocal, n, s: café, también, después
   • No llevan acento si terminan en otras letras: amor, dolor, cantar

2. **Palabras graves** (acento en penúltima sílaba):
   • Llevan acento si NO terminan en vocal, n, s: árbol, ángel, útil
   • No llevan acento si terminan en vocal, n, s: casa, como, pero

3. **Palabras esdrújulas** (acento en antepenúltima sílaba):
   • Siempre llevan acento: teléfono, música, vehículo

📚 **Palabras confusas comunes:**

• 'Es' (verbo) vs 'és' (no existe)
• 'Mas' (conjunción) vs 'más' (comparativo)
• 'Si' (conjunción) vs 'sí' (afirmación)
• 'Tu' (posesivo) vs 'tú' (pronombre)
• 'El' (artículo) vs 'él' (pronombre)
• 'Aun' (concesión) vs 'aún' (todavía)
• 'Solo' (único) vs 'sólo' (solamente)

✍️ **Consejos de escritura profesional:**

• Usa frases activas en lugar de pasivas
• Evita palabras innecesarias
• Sé específico y concreto
• Relee tu texto antes de enviarlo
• Usa herramientas de revisión ortográfica

¿Quieres que revise algún texto específico o tienes alguna duda particular sobre ortografía?"""

    return respuesta

def generar_respuesta_estado_actual(usuario, actividad_reciente):
    """Muestra el estado actual del usuario"""
    nombre = usuario.get_full_name() or usuario.username

    # Obtener estadísticas actuales
    estadisticas = Estadistica.objects.filter(usuario=usuario).last()

    # Análisis de actividad reciente
    ahora = timezone.now()
    actividad_ultima_hora = ActividadUsuario.objects.filter(
        usuario=usuario,
        timestamp__gte=ahora - timezone.timedelta(hours=1)
    )

    productiva = actividad_ultima_hora.filter(productividad='productive').count()
    improductiva = actividad_ultima_hora.filter(productividad='unproductive').count()
    gaming = actividad_ultima_hora.filter(productividad='gaming').count()
    total = actividad_ultima_hora.count()

    # Calcular ratio de productividad
    ratio_productividad = (productiva / total * 100) if total > 0 else 0

    # Estado de actividad actual
    if actividad_reciente:
        tiempo_desde_ultima = ahora - actividad_reciente.timestamp
        minutos_desde_ultima = tiempo_desde_ultima.seconds // 60

        if minutos_desde_ultima < 5:
            estado_actividad = "Activo ahora mismo"
        elif minutos_desde_ultima < 30:
            estado_actividad = f"Activo hace {minutos_desde_ultima} minutos"
        else:
            estado_actividad = f"Inactivo desde hace {minutos_desde_ultima} minutos"
    else:
        estado_actividad = "Sin actividad reciente"

    respuesta = f"""📊 Estado Actual - {nombre}

⏰ Actividad reciente: {estado_actividad}

📈 Productividad (última hora):
• Actividades productivas: {productiva}
• Actividades improductivas: {improductiva}
• Tiempo gaming: {gaming}
• Ratio productividad: {ratio_productividad:.1f}%

"""

    if estadisticas:
        respuesta += f"""🎯 Estadísticas generales:
• Puntuación actual: {estadisticas.puntaje}/100
• Mejoras acumuladas: {estadisticas.mejoras}

"""

    if actividad_reciente and actividad_reciente.ventana_activa:
        respuesta += f"""💻 Aplicación activa: {actividad_reciente.ventana_activa}
📊 Nivel de productividad: {actividad_reciente.productividad.title()}

"""

    # Consejos basados en el estado actual
    consejos = []

    if ratio_productividad < 40:
        consejos.append("💡 Tu productividad está baja. Considera tomar un descanso breve o cambiar de tarea.")

    if minutos_desde_ultima > 30:
        consejos.append("⚠️ Hace tiempo que no detecto actividad. ¿Todo bien?")

    if estadisticas and estadisticas.puntaje < 50:
        consejos.append("📈 Tu puntuación general es baja. ¿Quieres consejos para mejorar?")

    if consejos:
        respuesta += "💡 Sugerencias:\n" + " | ".join(f"• {consejo}" for consejo in consejos)

    respuesta += "\n\n¿Te gustaría que profundice en algún aspecto específico de tu rendimiento?"

    return respuesta

def generar_respuesta_matematicas(mensaje):
    """Resuelve operaciones matemáticas simples"""
    try:
        # Limpiar el mensaje para extraer la operación
        mensaje_limpio = mensaje.lower().replace(' ', '')

        # Buscar patrones de operaciones
        import re

        # Patrones para diferentes operaciones
        patrones = [
            (r'(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)', lambda x, y: float(x) + float(y), '+'),
            (r'(\d+(?:\.\d+)?)\s*\-\s*(\d+(?:\.\d+)?)', lambda x, y: float(x) - float(y), '-'),
            (r'(\d+(?:\.\d+)?)\s*\*\s*(\d+(?:\.\d+)?)', lambda x, y: float(x) * float(y), '×'),
            (r'(\d+(?:\.\d+)?)\s*\/\s*(\d+(?:\.\d+)?)', lambda x, y: float(x) / float(y) if y != 0 else None, '÷'),
            (r'(\d+(?:\.\d+)?)\s*por\s*(\d+(?:\.\d+)?)', lambda x, y: float(x) * float(y), '×'),
            (r'(\d+(?:\.\d+)?)\s*entre\s*(\d+(?:\.\d+)?)', lambda x, y: float(x) / float(y) if y != 0 else None, '÷'),
            (r'(\d+(?:\.\d+)?)\s*mas\s*(\d+(?:\.\d+)?)', lambda x, y: float(x) + float(y), '+'),
            (r'(\d+(?:\.\d+)?)\s*menos\s*(\d+(?:\.\d+)?)', lambda x, y: float(x) - float(y), '-'),
        ]

        for patron, operacion, simbolo in patrones:
            match = re.search(patron, mensaje_limpio)
            if match:
                num1, num2 = match.groups()
                resultado = operacion(num1, num2)

                if resultado is None:
                    return "❌ Error: No se puede dividir por cero."

                # Formatear resultado
                if resultado == int(resultado):
                    resultado = int(resultado)

                return f"🔢 Operación matemática:\n\n{num1} {simbolo} {num2} = {resultado}\n\n¿Necesitas hacer otra operación?"

        # Si no se encontró operación válida
        return "🤔 No pude identificar una operación matemática válida. Puedes escribir operaciones como:\n\n• 2 + 2\n• 10 * 5\n• 15 / 3\n• 8 menos 3\n• 7 por 6\n\n¿Quieres que resuelva alguna operación específica?"

    except Exception as e:
        return f"❌ Error al procesar la operación matemática: {str(e)}\n\n¿Puedes escribir la operación de otra manera?"

def generar_respuesta_contextual_inteligente(mensaje, usuario, ventana_activa, actividad_reciente):
    """Respuesta inteligente basada en contexto de actividad"""
    mensaje_lower = mensaje.lower().strip()

    # Análisis de sentimientos y tono
    palabras_positivas = ['bien', 'excelente', 'genial', 'perfecto', 'gracias', 'ok', 'okey', 'fantastico', 'increible']
    palabras_negativas = ['mal', 'problema', 'dificultad', 'error', 'ayuda', 'no funciona', 'terrible', 'horrible']
    palabras_cansado = ['cansado', 'agotado', 'fatigado', 'tengo sueño', 'aburrido']

    es_positivo = any(palabra in mensaje_lower for palabra in palabras_positivas)
    es_negativo = any(palabra in mensaje_lower for palabra in palabras_negativas)
    esta_cansado = any(palabra in mensaje_lower for palabra in palabras_cansado)

    # Respuestas basadas en sentimiento
    if es_positivo:
        respuesta_base = "¡Me alegra oír eso! 😊"
    elif es_negativo:
        respuesta_base = "Lamento oír que tienes dificultades. ¿Me puedes dar más detalles?"
    elif esta_cansado:
        respuesta_base = "Parece que estás cansado. Un descanso breve puede recargar tu energía. ☕"
    else:
        respuesta_base = "¡Hola! ¿En qué puedo ayudarte?"

    # Agregar contexto de actividad si está disponible
    contexto_adicional = ""

    if ventana_activa:
        if 'excel' in ventana_activa:
            contexto_adicional = " Como veo que estás trabajando con Excel, ¿necesitas ayuda con alguna fórmula o función específica?"
        elif 'word' in ventana_activa:
            contexto_adicional = " Veo que estás trabajando en un documento. ¿Necesitas consejos de formato o redacción?"
        elif any(ide in ventana_activa for ide in ['vscode', 'pycharm', 'visual studio']):
            contexto_adicional = " Estás programando. ¿Puedo ayudarte con algún problema de código?"

    # Agregar sugerencias basadas en actividad reciente
    sugerencias = []

    if actividad_reciente:
        tiempo_actividad = timezone.now() - actividad_reciente.timestamp
        minutos_actividad = tiempo_actividad.seconds // 60

        if minutos_actividad > 60:
            sugerencias.append("Hace un tiempo que no detecto actividad. ¿Todo bien?")
        elif minutos_actividad > 30:
            sugerencias.append("Llevas un rato trabajando. ¿Quieres consejos para mantener la concentración?")

    # Construir respuesta final
    respuesta = respuesta_base

    if contexto_adicional:
        respuesta += contexto_adicional

    if sugerencias:
        respuesta += " | " + " | ".join(sugerencias)

    respuesta += "\n\nPuedo ayudarte con:\n• 💡 Consejos de productividad\n• 📊 Análisis de rendimiento\n• 🔧 Solución de problemas\n• 📈 Recomendaciones personalizadas\n\n¿Qué te gustaría hacer?"

    return respuesta

def generar_respuesta_documentacion():
    """Proporciona documentación y guías de uso"""
    return """📚 Documentación y Guías de SARA

📖 **Guía de Inicio Rápido:**
1. Accede a la aplicación web en http://localhost:8000
2. Inicia sesión con tus credenciales
3. Explora el dashboard principal
4. Configura tus preferencias de monitoreo

📋 **Manuales de Usuario:**

🔧 **Configuración Inicial:**
• Cómo configurar tu perfil de usuario
• Configuración de notificaciones
• Ajustes de privacidad y seguridad

📊 **Uso del Dashboard:**
• Interpretación de métricas de productividad
• Visualización de gráficos y estadísticas
• Filtros y períodos de tiempo

💻 **Monitoreo de Actividad:**
• Qué aplicaciones se monitorean
• Niveles de clasificación (productivo/improductivo)
• Cómo pausar temporalmente el monitoreo

🤖 **Asistente IA:**
• Cómo hacer preguntas al asistente
• Tipos de consultas que puede resolver
• Consejos para obtener mejores respuestas

📝 **Gestión de Registros:**
• Cómo crear y editar registros
• Validación automática de datos
• Corrección de errores detectados

📈 **Reportes y Análisis:**
• Generación de reportes personalizados
• Exportación de datos
• Análisis de tendencias

🔒 **Seguridad y Privacidad:**
• Cómo se protegen tus datos
• Políticas de retención de información
• Derechos de acceso y modificación

¿Sobre qué tema específico necesitas más información?"""

def generar_respuesta_configuracion():
    """Ayuda con configuración del sistema"""
    return """⚙️ Guía de Configuración de SARA

🆕 **Primeros Pasos:**
1. **Registro de Usuario:** Crea tu cuenta con email y contraseña
2. **Verificación:** Confirma tu email para activar la cuenta
3. **Perfil:** Completa tu información personal y rol laboral

🔧 **Configuración de Monitoreo:**
• **Aplicaciones a monitorear:** Selecciona qué programas rastrear
• **Horarios laborales:** Define tus horas de trabajo habituales
• **Niveles de sensibilidad:** Ajusta la clasificación automática
• **Notificaciones:** Configura alertas y recordatorios

📊 **Personalización del Dashboard:**
• **Widgets visibles:** Elige qué métricas mostrar
• **Tema visual:** Claro/oscuro, colores personalizados
• **Idioma:** Español/Inglés
• **Formato de fechas:** DD/MM/AAAA o MM/DD/AAAA

🔔 **Notificaciones:**
• **Frecuencia:** Inmediata, diaria, semanal
• **Canales:** Email, aplicación, mensajería
• **Tipos:** Consejos, alertas, logros, recordatorios

🔒 **Seguridad:**
• **Autenticación de dos factores:** Activar/desactivar
• **Sesiones:** Duración automática de logout
• **Dispositivos:** Gestionar dispositivos conectados

💾 **Backup y Sincronización:**
• **Frecuencia de backup:** Diaria, semanal, manual
• **Almacenamiento:** Local o nube
• **Sincronización:** Entre dispositivos

¿Necesitas ayuda con alguna configuración específica?"""

def generar_respuesta_reportes(usuario):
    """Información sobre reportes y estadísticas disponibles"""
    # Obtener estadísticas del usuario
    estadisticas = Estadistica.objects.filter(usuario=usuario).last()

    respuesta = """📊 Reportes y Estadísticas Disponibles

📈 **Métricas Personales:**
• **Productividad general:** Puntuación de 0-100
• **Tiempo productivo vs improductivo**
• **Aplicaciones más usadas**
• **Patrones horarios de actividad**

📅 **Reportes por Período:**
• **Diario:** Actividad del día actual
• **Semanal:** Tendencias de la semana
• **Mensual:** Análisis completo del mes
• **Personalizado:** Rangos de fecha específicos

📊 **Tipos de Gráficos:**
• **Barras:** Comparación de productividad por día
• **Líneas:** Tendencias a lo largo del tiempo
• **Pastel:** Distribución por tipo de actividad
• **Área:** Acumulación de tiempo productivo

🎯 **Indicadores Clave:**
• **Ratio de productividad:** % de tiempo productivo
• **Mejor hora del día:** Momento de máxima eficiencia
• **Aplicación más productiva:** Herramienta más efectiva
• **Tendencia de mejora:** Evolución en el tiempo

📋 **Reportes Especiales:**
• **Análisis de errores:** Patrones de problemas recurrentes
• **Comparativas:** Antes vs después de mejoras
• **Objetivos cumplidos:** Metas alcanzadas
• **Recomendaciones:** Sugerencias basadas en datos

💾 **Exportación:**
• **PDF:** Reportes formateados para impresión
• **Excel:** Datos crudos para análisis adicional
• **CSV:** Exportación para otras herramientas
• **JSON:** Para integraciones técnicas

"""

    if estadisticas:
        respuesta += f"""📊 **Tu Estado Actual:**
• Puntuación de productividad: {estadisticas.puntaje}/100
• Nivel de mejora: {estadisticas.mejoras} puntos acumulados

¿Te gustaría generar un reporte específico o ver alguna métrica en detalle?"""
    else:
        respuesta += """📊 **Comienza a trabajar para ver tus estadísticas**

Una vez que tengas actividad registrada, podrás acceder a reportes detallados de tu productividad.

¿Quieres que te ayude a configurar el monitoreo para comenzar a generar datos?"""

    return respuesta

def generar_respuesta_equipo(usuario):
    """Información sobre trabajo en equipo y colaboración"""
    # Verificar si el usuario es supervisor/admin
    if usuario.rol in ['admin', 'supervisor']:
        # Obtener métricas del equipo
        equipo_count = Usuario.objects.filter(rol='empleado').count()
        respuesta = f"""👥 Gestión de Equipo - {usuario.get_full_name()}

📊 **Vista de Equipo ({equipo_count} miembros):**

🎯 **Funcionalidades de Supervisión:**
• **Dashboard del equipo:** Métricas agregadas de productividad
• **Monitoreo individual:** Seguimiento de cada miembro
• **Alertas de equipo:** Notificaciones de bajo rendimiento
• **Reportes comparativos:** Análisis entre miembros

📈 **Métricas de Equipo:**
• **Productividad promedio:** Nivel general del equipo
• **Mejores performers:** Miembros más productivos
• **Áreas de mejora:** Aspectos que necesitan atención
• **Tendencias grupales:** Evolución del equipo

🤝 **Colaboración:**
• **Compartición de mejores prácticas**
• **Sesiones de feedback grupal**
• **Metas de equipo**
• **Reconocimientos grupales**

💡 **Herramientas de Liderazgo:**
• **Feedback personalizado** para cada miembro
• **Planes de mejora** individualizados
• **Seguimiento de objetivos** del equipo
• **Análisis de patrones** grupales

¿Quieres ver métricas específicas de algún miembro del equipo?"""
    else:
        respuesta = """👥 Trabajo en Equipo y Colaboración

🤝 **Aspectos de Colaboración:**
• **Comunicación efectiva** con compañeros
• **Compartición de conocimientos** y mejores prácticas
• **Apoyo mutuo** en momentos de dificultad
• **Celebración de logros** grupales

📈 **Beneficios del Trabajo en Equipo:**
• **Aprendizaje continuo** de compañeros
• **Motivación grupal** y apoyo emocional
• **Diversidad de perspectivas** en soluciones
• **Mayor productividad** colectiva

💡 **Consejos para Mejorar la Colaboración:**
• **Reuniones regulares** de alineación
• **Canales de comunicación** claros
• **Reconocimiento público** de contribuciones
• **Feedback constructivo** y respetuoso

🎯 **Metas Grupales:**
• **Objetivos compartidos** que motiven
• **Responsabilidades claras** para cada miembro
• **Seguimiento conjunto** del progreso
• **Celebración colectiva** de hitos

¿Te gustaría consejos específicos para trabajar mejor en equipo?"""

    return respuesta

def generar_respuesta_salud():
    """Consejos sobre salud y bienestar laboral"""
    return """🏥 Salud y Bienestar en el Trabajo

🧠 **Salud Mental:**
• **Pausas activas:** 5-10 minutos cada hora para descansar la mente
• **Técnica Pomodoro:** 25 minutos de trabajo + 5 minutos de descanso
• **Mindfulness:** Ejercicios de atención plena durante pausas
• **Gestión del estrés:** Técnicas de respiración y relajación

💪 **Salud Física:**
• **Postura correcta:** Ajusta silla, escritorio y pantalla
• **Ejercicio regular:** Caminatas cortas o estiramientos
• **Hidratación:** Bebe agua regularmente durante la jornada
• **Vista:** Descansos para los ojos (regla 20-20-20)

⚡ **Prevención de la Fatiga:**
• **Sueño adecuado:** 7-8 horas diarias de calidad
• **Rutinas consistentes:** Horarios regulares de trabajo y descanso
• **Alimentación balanceada:** Comidas que mantengan la energía
• **Límites saludables:** Evita trabajar horas extras excesivas

📊 **Señales de Alerta:**
• **Cansancio crónico** o falta de energía
• **Dificultad para concentrarse** por períodos largos
• **Irritabilidad** o cambios de humor
• **Dolores físicos** recurrentes (cabeza, espalda, ojos)

🚨 **Cuando Pedir Ayuda:**
• **Recursos humanos:** Para apoyo profesional
• **Profesionales de salud:** Médicos o psicólogos
• **Líneas de ayuda:** Servicios de apoyo emocional
• **Tiempo libre:** Permisos por agotamiento

💡 **Estrategias Preventivas:**
• **Planificación semanal:** Evita sobrecargas de trabajo
• **Delegación efectiva:** Distribuye tareas de manera equilibrada
• **Autocuidado diario:** Dedica tiempo a actividades placenteras
• **Límites personales:** Aprende a decir "no" cuando es necesario

¿Te gustaría que te ayude con alguna rutina específica de bienestar?"""

def generar_respuesta_metas(usuario):
    """Ayuda con establecimiento y seguimiento de metas"""
    # Obtener estadísticas actuales para contextualizar
    estadisticas = Estadistica.objects.filter(usuario=usuario).last()

    respuesta = """🎯 Metas y Objetivos Personales

📋 **Tipos de Metas Recomendadas:**

🔥 **Metas Diarias:**
• **Productividad:** Alcanzar X horas de trabajo efectivo
• **Calidad:** Completar tareas sin errores recurrentes
• **Aprendizaje:** Dedicar tiempo a capacitación
• **Salud:** Mantener pausas regulares

📅 **Metas Semanales:**
• **Mejora continua:** Incrementar productividad en 5-10%
• **Habilidades:** Aprender una nueva función o herramienta
• **Eficiencia:** Reducir tiempo en tareas repetitivas
• **Colaboración:** Contribuir activamente al equipo

🎯 **Metas Mensuales:**
• **Objetivos grandes:** Completar proyectos importantes
• **Desarrollo:** Obtener certificaciones o conocimientos
• **Liderazgo:** Mentorear a compañeros
• **Innovación:** Proponer mejoras al proceso

📊 **Cómo Establecer Metas SMART:**
• **Specific (Específicas):** Claramente definidas
• **Measurable (Medibles):** Con indicadores cuantificables
• **Achievable (Alcanzables):** Realistas dentro de tus capacidades
• **Relevant (Relevantes):** Alineadas con tus objetivos
• **Time-bound (Temporal):** Con plazos definidos

"""

    if estadisticas:
        puntaje_actual = estadisticas.puntaje
        mejoras = estadisticas.mejoras

        # Sugerir metas basadas en el rendimiento actual
        if puntaje_actual < 50:
            respuesta += f"""📊 **Tu Estado Actual:** {puntaje_actual}/100 puntos

🎯 **Metas Recomendadas para Ti:**
• **Meta inmediata:** Alcanzar 60 puntos de productividad esta semana
• **Meta semanal:** Mejorar 5 puntos cada día
• **Meta mensual:** Establecer rutinas que eleven tu puntuación base
• **Meta de aprendizaje:** Identificar y corregir patrones de error recurrentes

💪 **Plan de Acción:**
1. **Análisis:** Revisa qué actividades te bajan la productividad
2. **Rutina:** Establece horarios fijos de trabajo
3. **Herramientas:** Usa técnicas de gestión del tiempo
4. **Seguimiento:** Monitorea tu progreso diariamente"""
        elif puntaje_actual < 80:
            respuesta += f"""📊 **Tu Estado Actual:** {puntaje_actual}/100 puntos

🎯 **Metas Recomendadas para Ti:**
• **Meta inmediata:** Alcanzar 85 puntos esta semana
• **Meta semanal:** Mantener consistencia en días laborales
• **Meta mensual:** Convertirte en referente de productividad
• **Meta de crecimiento:** Ayudar a compañeros con tu experiencia

💪 **Plan de Acción:**
1. **Optimización:** Identifica tus horas más productivas
2. **Consistencia:** Mantén rutinas que funcionan
3. **Mentoría:** Comparte tus mejores prácticas
4. **Innovación:** Busca nuevas formas de mejorar"""
        else:
            respuesta += f"""📊 **Tu Estado Actual:** {puntaje_actual}/100 puntos

🎯 **Metas Recomendadas para Ti:**
• **Meta inmediata:** Mantener excelencia (>90 puntos)
• **Meta semanal:** Establecer nuevos desafíos personales
• **Meta mensual:** Convertirte en líder de mejores prácticas
• **Meta de impacto:** Influir positivamente en todo el equipo

💪 **Plan de Acción:**
1. **Excelencia:** Mantén los estándares altos
2. **Liderazgo:** Conduce por el ejemplo
3. **Innovación:** Propón mejoras al sistema
4. **Compartición:** Transmite tu conocimiento"""

    respuesta += """

🔍 **Seguimiento de Metas:**
• **Diario:** Revisa progreso al final del día
• **Semanal:** Evalúa cumplimiento y ajusta estrategias
• **Mensual:** Celebra logros y establece nuevas metas
• **Trimestral:** Revisa objetivos a largo plazo

🎉 **Celebración de Logros:**
• **Pequeños hitos:** Reconoce cada victoria
• **Progreso constante:** Valora la mejora continua
• **Logros grupales:** Comparte éxitos con el equipo
• **Recompensas:** Establece premios por metas cumplidas

¿Quieres que te ayude a definir una meta específica o crear un plan de seguimiento?"""

    return respuesta
