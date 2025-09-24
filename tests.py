import os
import django
from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
from unittest.mock import patch, MagicMock

# Configurar Django para tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sara.settings')
django.setup()

from core.models import Registro, Estadistica, IAAnalisis, ActividadUsuario, Usuario
from core.views import (
    analizar_intencion_mensaje,
    generar_respuesta_asistente,
    consejos_proactivos_api
)

User = get_user_model()

class TestAnalizarIntencionMensaje(TestCase):
    """Tests para la función de análisis de intención de mensajes"""

    def test_analizar_saludos(self):
        """Test análisis de mensajes de saludo"""
        mensajes_saludo = ['hola', 'buenos días', 'Hola SARA', 'saludos']
        for mensaje in mensajes_saludo:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'saludo')

    def test_analizar_preguntas_personales(self):
        """Test análisis de preguntas personales"""
        mensajes_personales = ['como te llamas', 'quien eres', 'qué eres', 'que eres', 'tu nombre']
        for mensaje in mensajes_personales:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'pregunta_personal')

    def test_analizar_ayuda(self):
        """Test análisis de peticiones de ayuda"""
        mensajes_ayuda = ['ayuda', 'necesito ayuda', 'puedes ayudarme']
        for mensaje in mensajes_ayuda:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'ayuda')

    def test_analizar_productividad(self):
        """Test análisis de temas de productividad"""
        mensajes_productividad = ['productividad', 'productivo', 'eficiencia', 'rendimiento']
        for mensaje in mensajes_productividad:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'productividad')

    def test_analizar_excel(self):
        """Test análisis de consultas sobre Excel"""
        mensajes_excel = ['excel', 'formula', 'fórmula', 'hoja', 'spreadsheet', 'calcul']
        for mensaje in mensajes_excel:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'excel')

    def test_analizar_errores(self):
        """Test análisis de consultas sobre errores"""
        mensajes_errores = ['tengo un error', 'no funciona', 'problema técnico']
        for mensaje in mensajes_errores:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'errores')

    def test_analizar_matematicas(self):
        """Test análisis de operaciones matemáticas"""
        mensajes_matematicas = ['2 + 2', '10 * 5', 'cuanto es 15 / 3']
        for mensaje in mensajes_matematicas:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'matematicas')

    def test_analizar_ortografia(self):
        """Test análisis de consultas sobre ortografía"""
        mensajes_ortografia = ['cómo se escribe', 'ortografía', 'palabra correcta']
        for mensaje in mensajes_ortografia:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'ortografia')

    def test_analizar_documentacion(self):
        """Test análisis de consultas sobre documentación"""
        mensajes_documentacion = ['manual', 'guía de uso', 'documentación']
        for mensaje in mensajes_documentacion:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'documentacion')

    def test_analizar_configuracion(self):
        """Test análisis de consultas sobre configuración"""
        mensajes_configuracion = ['configurar', 'setup', 'cómo instalar']
        for mensaje in mensajes_configuracion:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'configuracion')

    def test_analizar_reportes(self):
        """Test análisis de consultas sobre reportes"""
        mensajes_reportes = ['estadistica', 'estadística', 'grafico', 'gráfico', 'analisis', 'análisis', 'dashboard']
        for mensaje in mensajes_reportes:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'reportes')

    def test_analizar_equipo(self):
        """Test análisis de consultas sobre equipo"""
        mensajes_equipo = ['equipo', 'compañeros', 'colaboracion', 'colaboración']
        for mensaje in mensajes_equipo:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'equipo')

    def test_analizar_salud(self):
        """Test análisis de consultas sobre salud"""
        mensajes_salud = ['salud', 'bienestar', 'cansado', 'estrés']
        for mensaje in mensajes_salud:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'salud')

    def test_analizar_metas(self):
        """Test análisis de consultas sobre metas"""
        mensajes_metas = ['meta', 'objetivo', 'logro', 'progreso']
        for mensaje in mensajes_metas:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'metas')

    def test_analizar_general(self):
        """Test mensajes que no caen en categorías específicas"""
        mensajes_generales = ['mensaje normal', 'consulta general', 'pregunta cualquiera']
        for mensaje in mensajes_generales:
            with self.subTest(mensaje=mensaje):
                resultado = analizar_intencion_mensaje(mensaje)
                self.assertEqual(resultado, 'general')


class TestAsistenteIA(TestCase):
    """Tests para las funcionalidades del asistente IA"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            rol='empleado'
        )
        self.client.force_login(self.user)

    def test_asistente_chat_api_post(self):
        """Test API del chat del asistente con POST"""
        response = self.client.post(
            reverse('asistente_chat_api'),
            {'mensaje': 'hola'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIn('respuesta', data)
        self.assertIn('timestamp', data)

    def test_asistente_chat_api_get_not_allowed(self):
        """Test que GET no está permitido en la API del chat"""
        response = self.client.get(reverse('asistente_chat_api'))
        self.assertEqual(response.status_code, 405)

    def test_consejos_proactivos_api(self):
        """Test API de consejos proactivos"""
        response = self.client.get(reverse('consejos_proactivos_api'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIn('consejos', data)
        self.assertIn('timestamp', data)

    def test_respuesta_saludo(self):
        """Test respuesta de saludo"""
        respuesta = generar_respuesta_asistente(self.user, 'hola', {})
        self.assertIn('buenas tardes', respuesta.lower())
        self.assertIn('SARA', respuesta)

    def test_respuesta_excel(self):
        """Test respuesta sobre Excel"""
        respuesta = generar_respuesta_asistente(self.user, 'ayuda con excel', {})
        self.assertIn('excel', respuesta.lower())
        self.assertIn('fórmula', respuesta.lower() or 'ayuda' in respuesta.lower())

    def test_respuesta_matematicas_suma(self):
        """Test operaciones matemáticas - suma"""
        respuesta = generar_respuesta_asistente(self.user, 'cuanto es 2 + 2', {})
        self.assertIn('4', respuesta)
        self.assertIn('2 + 2 = 4', respuesta)

    def test_respuesta_matematicas_resta(self):
        """Test operaciones matemáticas - resta"""
        respuesta = generar_respuesta_asistente(self.user, '10 menos 3', {})
        self.assertIn('7', respuesta)

    def test_respuesta_matematicas_multiplicacion(self):
        """Test operaciones matemáticas - multiplicación"""
        respuesta = generar_respuesta_asistente(self.user, '5 por 3', {})
        self.assertIn('15', respuesta)

    def test_respuesta_matematicas_division(self):
        """Test operaciones matemáticas - división"""
        respuesta = generar_respuesta_asistente(self.user, '10 entre 2', {})
        self.assertIn('5', respuesta)

    def test_respuesta_matematicas_division_por_cero(self):
        """Test operaciones matemáticas - división por cero"""
        respuesta = generar_respuesta_asistente(self.user, '10 entre 0', {})
        self.assertIn('float division by zero', respuesta.lower())

    def test_respuesta_ortografia(self):
        """Test respuesta sobre ortografía"""
        respuesta = generar_respuesta_asistente(self.user, 'como se escribe mas', {})
        self.assertIn('más', respuesta)
        self.assertIn('acento', respuesta.lower() or 'ortografía' in respuesta.lower())


class TestModelos(TestCase):
    """Tests para los modelos de datos"""

    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            rol='empleado'
        )

    def test_crear_usuario(self):
        """Test creación de usuario"""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            rol='admin'
        )
        self.assertEqual(user.username, 'testuser2')
        self.assertEqual(user.rol, 'admin')
        self.assertTrue(user.check_password('testpass123'))

    def test_crear_registro(self):
        """Test creación de registro"""
        registro = Registro.objects.create(
            usuario=self.user,
            fecha='2025-01-15',
            contenido={'tipo': 'trabajo', 'horas': 8}
        )
        self.assertEqual(registro.usuario, self.user)
        self.assertEqual(registro.fecha, '2025-01-15')
        self.assertEqual(registro.contenido['tipo'], 'trabajo')

    def test_crear_estadistica(self):
        """Test creación de estadística"""
        estadistica = Estadistica.objects.create(
            usuario=self.user,
            puntaje=85,
            mejoras=10
        )
        self.assertEqual(estadistica.usuario, self.user)
        self.assertEqual(estadistica.puntaje, 85)
        self.assertEqual(estadistica.mejoras, 10)

    def test_crear_actividad_usuario(self):
        """Test creación de actividad de usuario"""
        from django.utils import timezone
        actividad = ActividadUsuario.objects.create(
            usuario=self.user,
            ventana_activa='Microsoft Excel',
            productividad='productive',
            timestamp=timezone.now()
        )
        self.assertEqual(actividad.usuario, self.user)
        self.assertEqual(actividad.ventana_activa, 'Microsoft Excel')
        self.assertEqual(actividad.productividad, 'productive')


class TestVistasWeb(TestCase):
    """Tests para las vistas web"""

    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            rol='empleado'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            rol='admin'
        )

    def test_dashboard_sin_autenticacion(self):
        """Test acceso al dashboard sin autenticación"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_con_autenticacion(self):
        """Test acceso al dashboard con autenticación"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SARA')

    def test_asistente_chat_view(self):
        """Test vista del chat del asistente"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('asistente_chat'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'asistente')

    def test_dashboard_admin_acceso_denegado(self):
        """Test acceso denegado al dashboard admin para usuario regular"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard_admin'))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_dashboard_admin_acceso_permitido(self):
        """Test acceso permitido al dashboard admin para admin"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard_admin'))
        self.assertEqual(response.status_code, 200)


class TestIntegracion(TestCase):
    """Tests de integración end-to-end"""

    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            rol='empleado'
        )
        self.client.force_login(self.user)

    def test_flujo_completo_asistente(self):
        """Test flujo completo de interacción con el asistente"""
        # 1. Acceder al chat
        response = self.client.get(reverse('asistente_chat'))
        self.assertEqual(response.status_code, 200)

        # 2. Enviar mensaje al asistente
        response = self.client.post(
            reverse('asistente_chat_api'),
            {'mensaje': 'hola'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content.decode())
        self.assertIn('respuesta', data)
        self.assertIn('SARA', data['respuesta'])

        # 3. Verificar consejos proactivos
        response = self.client.get(reverse('consejos_proactivos_api'))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content.decode())
        self.assertIn('consejos', data)

    def test_flujo_registro_errores(self):
        """Test flujo de registro con errores y análisis IA"""
        from django.utils import timezone

        # 1. Crear registro con errores
        registro = Registro.objects.create(
            usuario=self.user,
            fecha='2025-01-15',
            contenido={'campo1': 'valor1'},
            errores=[{'campo': 'campo1', 'mensaje': 'Error de validación'}]
        )

        # 2. Verificar que se creó correctamente
        self.assertEqual(registro.usuario, self.user)
        self.assertTrue(len(registro.errores) > 0)

        # 3. Crear actividad de usuario
        ActividadUsuario.objects.create(
            usuario=self.user,
            ventana_activa='Error App',
            productividad='unproductive',
            timestamp=timezone.now()
        )

        # 4. Consultar al asistente sobre errores
        response = self.client.post(
            reverse('asistente_chat_api'),
            {'mensaje': 'tengo errores'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content.decode())
        self.assertIn('respuesta', data)


if __name__ == '__main__':
    import unittest
    unittest.main()