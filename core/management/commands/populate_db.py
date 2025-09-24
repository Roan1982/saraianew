from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Usuario, Registro, Estadistica, IAAnalisis, ActividadUsuario
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Starting database population...')

        # Crear usuarios sugeridos
        usuarios_data = [
            {
                'username': 'admin',
                'email': 'admin@sara.com',
                'password': 'admin123',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'rol': 'admin'
            },
            {
                'username': 'supervisor1',
                'email': 'supervisor1@sara.com',
                'password': 'password123',
                'first_name': 'Supervisor',
                'last_name': 'Uno',
                'rol': 'supervisor'
            },
            {
                'username': 'empleado1',
                'email': 'empleado1@sara.com',
                'password': 'password123',
                'first_name': 'Empleado',
                'last_name': 'Uno',
                'rol': 'empleado'
            },
            {
                'username': 'empleado2',
                'email': 'empleado2@sara.com',
                'password': 'password123',
                'first_name': 'Empleado',
                'last_name': 'Dos',
                'rol': 'empleado'
            }
        ]

        usuarios_creados = []
        for user_data in usuarios_data:
            if not Usuario.objects.filter(username=user_data['username']).exists():
                usuario = Usuario.objects.create_user(**user_data)
                usuarios_creados.append(usuario)
                self.stdout.write(f'Created user: {usuario.username}')
            else:
                usuario = Usuario.objects.get(username=user_data['username'])
                usuarios_creados.append(usuario)
                self.stdout.write(f'User already exists: {usuario.username}')

        # Crear datos de ejemplo para cada usuario
        for usuario in usuarios_creados:
            self.crear_datos_usuario(usuario)

        self.stdout.write(self.style.SUCCESS('Database population completed!'))

    def crear_datos_usuario(self, usuario):
        """Crear datos de ejemplo para un usuario"""
        # Crear registros diarios (últimos 30 días)
        for i in range(30):
            fecha = timezone.now().date() - timedelta(days=i)
            contenido = {
                'campo1': f'valor_{i}',
                'campo2': f'dato_{i}',
                'campo3': random.randint(1, 100)
            }

            # Algunos registros con errores
            errores = []
            if random.random() < 0.3:  # 30% de probabilidad de errores
                errores = [
                    {
                        'campo': 'campo1',
                        'mensaje': f'Error de validación en campo {random.randint(1,3)}'
                    }
                ]

            Registro.objects.get_or_create(
                usuario=usuario,
                fecha=fecha,
                defaults={
                    'contenido': contenido,
                    'errores': errores
                }
            )

        # Crear estadísticas
        Estadistica.objects.get_or_create(
            usuario=usuario,
            defaults={
                'puntaje': random.randint(60, 95),
                'mejoras': random.randint(10, 50),
                'fecha_actualizacion': timezone.now()
            }
        )

        # Crear análisis IA
        for i in range(5):
            IAAnalisis.objects.get_or_create(
                usuario=usuario,
                fecha_analisis=timezone.now() - timedelta(days=i*2),
                defaults={
                    'patrones_detectados': {
                        'tipo': 'productividad',
                        'nivel': random.choice(['bajo', 'medio', 'alto']),
                        'descripcion': f'Análisis de productividad día {i}'
                    },
                    'recomendacion': f'Recomendación personalizada {i} para {usuario.username}',
                    'severidad': random.choice(['baja', 'media', 'alta'])
                }
            )

        # Crear actividad de usuario (últimas 24 horas)
        aplicaciones = [
            'Microsoft Excel', 'Microsoft Word', 'Google Chrome', 'Visual Studio Code',
            'Outlook', 'PowerPoint', 'Notepad', 'File Explorer', 'Teams'
        ]

        for i in range(50):  # 50 actividades en las últimas 24 horas
            timestamp = timezone.now() - timedelta(minutes=random.randint(1, 1440))

            ActividadUsuario.objects.get_or_create(
                usuario=usuario,
                timestamp=timestamp,
                defaults={
                    'ventana_activa': random.choice(aplicaciones),
                    'productividad': random.choice(['productive', 'unproductive', 'neutral', 'gaming']),
                    'tiempo_activo': random.randint(30, 300)  # 30 segundos a 5 minutos
                }
            )