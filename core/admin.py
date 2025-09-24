from django.contrib import admin
from .models import Usuario, Registro, Estadistica, IAAnalisis

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'rol', 'is_active')
    list_filter = ('rol', 'is_active')
    search_fields = ('username', 'first_name', 'last_name')

@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'id')
    list_filter = ('fecha', 'usuario')
    search_fields = ('usuario__username', 'contenido')
    date_hierarchy = 'fecha'

@admin.register(Estadistica)
class EstadisticaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'puntaje', 'mejoras', 'fecha_actualizacion')
    list_filter = ('fecha_actualizacion',)
    search_fields = ('usuario__username',)

@admin.register(IAAnalisis)
class IAAnalisisAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_analisis', 'recomendacion')
    list_filter = ('fecha_analisis',)
    search_fields = ('usuario__username', 'recomendacion')
