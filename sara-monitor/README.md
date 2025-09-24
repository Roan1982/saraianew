# SARA Monitor - Sistema de Productividad Proactiva

SARA Monitor es una aplicación de escritorio que monitorea la actividad del usuario en tiempo real, analiza patrones de productividad y proporciona sugerencias proactivas usando IA.

## Características

- **Monitoreo en Tiempo Real**: Captura actividad cada 5 segundos
- **Análisis de Productividad**: Clasifica aplicaciones como productivas, no productivas, juegos o neutrales
- **IA Proactiva**: Genera sugerencias basadas en patrones de uso
- **Dashboard Visual**: Gráficos y métricas de tiempo y productividad
- **Integración con SARA**: Envía datos al servidor Django para análisis avanzado

## Instalación

1. **Instalar dependencias**:
   ```bash
   cd sara-monitor
   npm install
   ```

2. **Configurar servidor Django**:
   - Asegurarse de que el servidor Django esté corriendo en `http://localhost:8000`
   - La API de actividad estará disponible en `/api/activity/`

3. **Ejecutar la aplicación**:
   ```bash
   npm start
   ```

## Arquitectura

### Componentes Principales

- **main.js**: Proceso principal de Electron - maneja monitoreo del sistema
- **preload.js**: Puente seguro entre procesos
- **renderer.js**: Interfaz de usuario y gráficos
- **index.html**: Estructura de la aplicación

### API de Comunicación

La aplicación envía datos al servidor Django cada 30 segundos:

```json
{
  "machineId": "unique-machine-identifier",
  "activities": [
    {
      "timestamp": "2025-09-23T09:00:00.000Z",
      "activeWindow": "Visual Studio Code",
      "topProcesses": [...],
      "systemLoad": {...},
      "productivity": "productive"
    }
  ]
}
```

## Funcionalidades de IA

### Análisis de Productividad

- **Productivo**: VS Code, Excel, Word, navegadores para trabajo
- **No Productivo**: WhatsApp, redes sociales, Netflix
- **Juegos**: Steam, Epic Games, aplicaciones de gaming
- **Neutral**: Sistema operativo, exploradores de archivos

### Sugerencias Proactivas

- Alertas de tiempo excesivo en aplicaciones no productivas
- Recordatorios de pausas durante horas laborales
- Sugerencias de horarios de trabajo
- Análisis de patrones de fatiga

## Privacidad y Seguridad

- Los datos se envían solo al servidor local Django
- No se captura contenido específico de aplicaciones
- Solo metadatos de procesos y ventanas activas
- Los datos se pueden eliminar localmente en cualquier momento

## Desarrollo

### Comandos Disponibles

- `npm start`: Ejecutar en modo desarrollo
- `npm run build`: Construir aplicación para distribución
- `npm run dist`: Crear instalador

### Tecnologías Utilizadas

- **Electron**: Framework para aplicaciones de escritorio
- **Chart.js**: Gráficos y visualizaciones
- **Bootstrap**: Framework CSS
- **System Information**: Monitoreo del sistema
- **Axios**: Comunicación HTTP

## Próximas Funcionalidades

- Captura de screenshots para análisis visual
- Detección de errores en aplicaciones externas
- Machine learning avanzado para predicciones
- Integración con calendarios y recordatorios
- Análisis de patrones de escritura y navegación

## Requisitos del Sistema

- Windows 10/11
- Node.js 16+
- 4GB RAM mínimo
- Espacio en disco: 200MB

## Soporte

Para soporte técnico o reportar problemas, contactar al equipo de desarrollo de SARA.