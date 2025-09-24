import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sara.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
import json

client = Client()
User = get_user_model()
user = User.objects.get(username='admin')
client.force_login(user)

# Probar diferentes tipos de mensajes
test_messages = [
    'Necesito ayuda con Excel',
    '¿Cómo mejorar mi productividad?',
    'Tengo un error en mi código',
    'Ayuda con ortografía'
]

for msg in test_messages:
    response = client.post('/api/asistente/chat/', {'mensaje': msg}, content_type='application/json')
    if response.status_code == 200:
        data = json.loads(response.content.decode())
        print(f'Pregunta: {msg}')
        print(f'Respuesta: {data["respuesta"][:100]}...')
        print('---')
    else:
        print(f'Error con "{msg}": {response.status_code}')