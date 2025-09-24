
from rest_framework import serializers
from .models import Registro, Estadistica, IAAnalisis, ActividadUsuario

class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro
        fields = '__all__'

class EstadisticaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estadistica
        fields = '__all__'

class IAAnalisisSerializer(serializers.ModelSerializer):
    class Meta:
        model = IAAnalisis
        fields = '__all__'

class ActividadUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActividadUsuario
        fields = '__all__'
