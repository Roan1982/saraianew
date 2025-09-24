import requests
import json

# Probar el asistente con una sesión autenticada
session = requests.Session()

# Login
login_response = session.post('http://localhost:8000/api/login/', json={'username': 'admin', 'password': 'admin123'})
print(f'Login Status: {login_response.status_code}')

if login_response.status_code == 200:
    # Probar el chat del asistente
    chat_response = session.post('http://localhost:8000/api/asistente/chat/', json={'mensaje': 'Hola, ¿cómo estás?'})
    print(f'Chat Status: {chat_response.status_code}')

    if chat_response.status_code == 200:
        data = chat_response.json()
        print(f'Respuesta: {data["respuesta"][:100]}...')
    else:
        print(f'Error en chat: {chat_response.text}')
else:
    print(f'Error en login: {login_response.text}')