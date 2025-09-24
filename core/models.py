
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('empleado', 'Empleado'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='empleado')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

class Registro(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateField()
    contenido = models.JSONField()
    errores = models.JSONField(default=list)

    def __str__(self):
        return f'Registro de {self.usuario} - {self.fecha}'

class Estadistica(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    puntaje = models.IntegerField(default=0)
    mejoras = models.IntegerField(default=0)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Estadísticas de {self.usuario}'

class IAAnalisis(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    recomendacion = models.TextField()
    patrones_detectados = models.JSONField(default=list)
    fecha_analisis = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Análisis IA para {self.usuario}'

class ActividadUsuario(models.Model):
    """Modelo para almacenar la actividad monitoreada del usuario"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    machine_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    ventana_activa = models.CharField(max_length=200)
    procesos_activos = models.JSONField(default=list)
    carga_sistema = models.JSONField(default=dict)
    productividad = models.CharField(max_length=20, choices=[
        ('productive', 'Productivo'),
        ('unproductive', 'No Productivo'),
        ('gaming', 'Jugando'),
        ('neutral', 'Neutral'),
    ])
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Actividad de Usuario'
        verbose_name_plural = 'Actividades de Usuarios'
        ordering = ['-timestamp']

    def __str__(self):
        return f'Actividad de {self.machine_id} - {self.timestamp}'
