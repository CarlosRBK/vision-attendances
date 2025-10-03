# Face Services — Microservicio HTTP de Detección Facial

Servicio HTTP para detección y reconocimiento facial. Diseñado para funcionar de forma desacoplada del hardware de cámara: el frontend captura frames desde el navegador y los envía al servicio vía HTTP.

## Arquitectura

* Sin acceso directo a cámaras: el frontend captura frames y los envía como base64.
* Ventajas:
	+ Funciona 100% en Docker (Windows, Linux, Mac).
	+ No necesita dispositivos USB compartidos.
	+ Escalable y portable.
	+ Fácil de depurar.
	+ Sin limitaciones de Docker Desktop.

## Inicio rápido

* Arranque:

```powershell
./docker-start.ps1
```

* Disponible en: http://localhost:5001

## API Endpoints

* GET `/health`:
	+ Verifica el estado del servicio.
* POST `/detect`:
	+ Detecta y reconoce rostros en un frame.
* POST `/reload`:
	+ Recarga manualmente los rostros conocidos.
* GET `/attendance/today`:
	+ Obtiene la lista de asistencia del día.

## Estructura del proyecto

```
face-services/
main.py
requirements.txt
Dockerfile
.dockerignore
asistencias/
static/
people_photos/
```

## Flujo de funcionamiento

1. El frontend captura un frame de la cámara (navegador).
2. Convierte el frame a base64.
3. Envía `POST /detect` con el payload.
4. Face Services procesa la imagen.
5. Devuelve respuesta en JSON.
6. El frontend muestra los resultados.

## Dependencias principales

* Flask
* flask-cors
* OpenCV
* face_recognition
* dlib
* watchdog
* numpy

## Registro de asistencias

* Se generan en: `asistencias/asistencia_DD-MM-YYYY.txt`

## Integración con Backend

* Volúmenes compartidos: `backend_media:/app/static/people_photos`

## Variables de entorno

```
PYTHONUNBUFFERED=1
```

## Pruebas manuales

* **Health check**:

```bash
curl http://localhost:5001/health
```

* **Recargar rostros**:

```bash
curl -X POST http://localhost:5001/reload
```

## Logs

```bash
docker-compose logs -f face-services
```

## Troubleshooting

* Verificar servicio: `docker-compose ps`
* Revisar logs: `docker-compose logs face-services`

## Comandos útiles

```bash
docker-compose restart face-services
docker-compose build face-services
```

## Producción

* Recomendaciones: Nginx, HTTPS, Rate Limiting, Monitoring, Escalado.

## Licencia

MIT