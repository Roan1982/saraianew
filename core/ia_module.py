
import joblib
from sklearn.linear_model import LogisticRegression
import pandas as pd
import os

_modelo = None

def obtener_modelo():
    global _modelo
    if _modelo is None:
        datos_entrenamiento = pd.DataFrame({
            'tipo_error': ['fecha', 'monto', 'duplicado', 'formato', 'fecha', 'monto'],
            'frecuencia': [10, 5, 3, 2, 8, 4],
            'severidad': [3, 2, 1, 2, 3, 2]
        })
        X = datos_entrenamiento[['frecuencia', 'severidad']]
        y = datos_entrenamiento['tipo_error']
        _modelo = LogisticRegression()
        _modelo.fit(X, y)
    return _modelo

def analizar_errores(usuario):
    from .models import Registro
    errores_recientes = Registro.objects.filter(usuario=usuario).values_list('errores', flat=True)
    if errores_recientes:
        modelo = obtener_modelo()
        recomendacion = 'Revisar formatos de fecha'
        from .models import IAAnalisis
        IAAnalisis.objects.create(
            usuario=usuario,
            recomendacion=recomendacion,
            patrones_detectados={'tipo': 'fecha'}
        )
        from .models import Estadistica
        stat, created = Estadistica.objects.get_or_create(usuario=usuario)
        stat.mejoras += 1
        stat.save()
