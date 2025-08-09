# Sistema de Asistencias por Reconocimiento Facial

Este documento describe una arquitectura modular monolítica (MVP) para registro de asistencias mediante reconocimiento facial, con Backend (FastAPI), Frontend (React+TS+Vite) y base de datos en MongoDB Atlas. Incluye estructura de carpetas, contratos de API, esquema de datos, configuración y una guía de ejecución local de los scripts existentes.

## Arquitectura (Modular Monolito)

- **Backend (FastAPI)**: API REST y tarea interna de reconocimiento en el mismo proceso. Organización por módulos (features): `auth`, `people`, `faces`, `attendances`, `device`.
- **Frontend (React + TypeScript + Vite)**: dashboard administrativo para login, personas, rostros, asistencias y configuración del dispositivo.
- **Base de datos (MongoDB Atlas)**: colecciones `people`, `faces`, `attendances`, `device` con índices mínimos para consultas frecuentes.
- **Fuente de video**: webcam local inicialmente; extensible a cámara IP (RTSP) vía configuración en `/device`.

### Backend — Estructura modular por carpetas

```
app/
  core/            # config, db (Motor), JWT, logs, errores
  modules/
    auth/          # router, schemas, service, repository
    people/        # router, schemas, service, repository
    faces/         # router, schemas, service, repository
    attendances/   # router, schemas, service, repository
    device/        # router, schemas, service, repository
  recognition/     # runner (tarea), pipeline, cache de embeddings
  shared/          # utils, tipos comunes
  main.py          # crea app, registra routers, startup/shutdown
```

Notas de diseño:
- Repositorios: acceso a Mongo (CRUD/queries) sin lógica de negocio.
- Services: reglas de negocio (debounce, validaciones) y coordinación entre repositorios.
- Routers: validación/parsing de requests y delegación a services.
- Reconocimiento: carga embeddings desde `faces`, procesa frames, hace matching y registra asistencias aplicando debounce configurable.

### Frontend — Estructura modular por features

```
src/
  app/       # routes, providers, store opcional
  shared/    # componentes reutilizables, hooks, api client, utils
  features/
    auth/
    people/
    faces/
    attendances/
    device/
```

## Contratos de API (resumen)

- **Auth**
  - POST `/auth/login` → JWT en `Authorization: Bearer <token>` para rutas protegidas.

- **People**
  - GET `/people` (filtros y paginación)
  - POST `/people` (alta)
  - GET `/people/{id}` (detalle)
  - PUT `/people/{id}` (edición)

- **Faces** (embeddings en backend)
  - POST `/faces` (multipart/form-data: `person_id` + `image`).
  - Política MVP: una sola cara por imagen; 400 si 0 o >1.

- **Attendances**
  - GET `/attendances` (filtros: `from`, `to`, `person_id`, `device_id`; paginación)
  - POST `/attendances` (uso interno del backend para registrar eventos del reconocimiento)

- **Device** (config extensible)
  - GET `/device` → configuración vigente.
  - PUT `/device` → objeto extensible con `type` y `params` (por ejemplo, webcam: `{ index, width, height, fps, debounce_seconds }`; rtsp: `{ url, width, height, fps, debounce_seconds, rtsp_transport?, reconnect_secs? }`).

- **Health**
  - GET `/health` → estado básico (status, version, uptime).

Errores estandarizados:
```json
{ "error": { "code": "STRING_CODE", "message": "Detalle legible", "details": {} } }
```

## Esquema de datos (MongoDB Atlas)

- **people**: `{ _id, full_name, active, external_id?, created_at }`
- **faces**: `{ _id, person_id, embedding[128], source, quality_score?, created_at }`
- **attendances**: `{ _id, person_id, device_id, timestamp, score, snapshot_url?, meta? }`
- **device**: `{ device_id, type, params: { … }, updated_at }`

Índices mínimos:
- `attendances.timestamp`
- `attendances.person_id`
- `faces.person_id`

Consideraciones:
- Los embeddings se almacenan como arreglo de 128 floats y el matching se realiza en el backend.
- Cache de embeddings en memoria para rendimiento y refresco periódico.

## Modelo académico y consultas de asistencia

Objetivo funcional: responder preguntas como “¿quiénes estuvieron presentes en 2° grado hoy?” y “¿cuál es el porcentaje de asistencia de un alumno en una materia durante un período?”. Para esto se incorporan entidades académicas mínimas y endpoints de consulta/reportes.

### Entidades nuevas

- **classes**: definición de curso/materia/sección.
  - Documento: `{ _id, name, grade, section?, subject?, year?, meta? }`

- **enrollments**: inscripción de persona a clase.
  - Documento: `{ _id, person_id, class_id, since: ISODate, until?: ISODate }`

- **sessions**: sesiones/fechas de clase planificadas u ocurridas.
  - Documento: `{ _id, class_id, date: ISODate (solo fecha), start_time?: "HH:MM", end_time?: "HH:MM", status?: "planned"|"done"|"canceled" }`

- **attendances** (existente): se amplía con referencias a clase/sesión si se dispone de contexto al registrar.
  - Extensión opcional del documento: `class_id?`, `session_id?`

Notas de simplicidad (MVP):
- Es suficiente cargar `sessions` manualmente (o por importación) para calcular porcentajes por período.
- Alternativa liviana: sin `sessions`, calcular sobre días hábiles del período; recomendado usar `sessions` por exactitud.

### Asignación de asistencias a clase/sesión

- Opción A (config por dispositivo): `device.params` puede incluir `class_id` y ventana horaria. Las asistencias registradas por ese dispositivo durante la ventana se etiquetan con `class_id` (y `session_id` si existe una `session` para ese día).
- Opción B (resolución por horario): el servicio de reconocimiento busca una `session` activa (por `class_id`, `date`, `start_time`/`end_time`) y etiqueta la asistencia.
- Si no hay contexto, `attendances` queda sin `class_id` y se puede inferir luego por consultas (menos preciso).

### Consultas soportadas

- Presentes por clase y fecha:
  - Input: `class_id`, `date` (ISO, solo fecha) → lista `person_id` presentes (distinct).
  - Procedimiento: `attendances` con `class_id` y rango del día; agrupar por `person_id`.

- Presentes por grado y fecha:
  - Input: `grade`, `date` → resolver `people` por `grade`, obtener sus `person_id` y filtrar `attendances` del día (`distinct`).

- Porcentaje de asistencia por alumno y clase (período):
  - Input: `person_id`, `class_id`, `from`, `to`.
  - Procedimiento: contar `sessions` en período (`status != "canceled"`) y contar días con al menos una `attendance` del `person_id` con ese `class_id` en cada `session.date`.
  - Output: `{ total_sessions, attended_sessions, attendance_rate }`.

### Extensiones de API (reportes)

- `GET /reports/attendance/daily`
  - Query: `class_id` y `date` o `grade` y `date`.
  - Respuesta: `{ date, scope: { class_id? , grade? }, present_person_ids: string[], total_present: number }`.

- `GET /reports/attendance/percentage`
  - Query: `person_id`, `class_id`, `from`, `to`.
  - Respuesta: `{ person_id, class_id, from, to, total_sessions, attended_sessions, attendance_rate }`.

### Cambios menores recomendados

- `people`: agregar `grade` (string/enum) y `group`/`section` (opcional) para filtros rápidos.
- Índices adicionales:
  - `people: { grade: 1, group: 1 }`
  - `enrollments: { class_id: 1, person_id: 1 }`
  - `sessions: { class_id: 1, date: 1 }`
  - `attendances: { class_id: 1, timestamp: 1, person_id: 1 }`

### Consideraciones operativas

- La decisión de usar `sessions` permite cálculo exacto de porcentaje respecto a clases reales (excluye canceladas).
- Si se prefiere simplicidad inicial, se puede comenzar con `class_id` en `device` y agregar `sessions` después; los endpoints de reportes funcionan con ambos enfoques, priorizando precisión cuando hay `sessions`.

## Configuración (.env)

- Backend
  - `MONGODB_URI`, `DB_NAME`, `JWT_SECRET`
  - Defaults de dispositivo opcionales: `DEVICE_TYPE`, `DEVICE_FPS`, `DEVICE_WIDTH`, `DEVICE_HEIGHT`, `DEBOUNCE_SECONDS`
- Frontend
  - `VITE_API_BASE_URL`

## Flujo de desarrollo

1. Ejecutar Backend (uvicorn). Documentación interactiva en `/docs`.
2. Probar conexión a Atlas y endpoints con credenciales.
3. Ejecutar Frontend y consumir la API.

## Roadmap incremental

- MVP: Backend único (API + reconocimiento), Frontend con Login/Personas/Faces/Asistencias/Device, Atlas con índices mínimos.
- Extensiones: Cámara IP (RTSP) desde `/device`, streaming de eventos (WebSocket), reportes/métricas, separación del reconocimiento a servicio independiente.

---

## Backend — Instalación y ejecución (FastAPI)

1) Activar entorno conda

```bash
conda activate face-recognition
```

2) Configurar variables en `backend/.env`

```env
MONGODB_URI=mongodb+srv://<usuario>:<password>@<cluster>/<db>?retryWrites=true&w=majority
DB_NAME=attendance
APP_VERSION=0.1.0
```

3) Instalar dependencias del backend

```bash
python -m pip install -r backend/requirements.txt
```

Notas:
- Usamos `motor>=3.7,<4` y `pymongo>=4.9,<5`.
- Si notas errores por usar el intérprete equivocado, ejecuta con la ruta absoluta del entorno:
  `/Users/carlos/miniconda3/envs/face-recognition/bin/python -m pip install -r backend/requirements.txt`

4) Ejecutar el servidor

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
# con autoreload en desarrollo:
# python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

5) Verificar

- Health: http://localhost:8000/health
- Swagger: http://localhost:8000/docs

6) Probar módulo faces (ejemplo cURL)

```bash
# Crear persona
curl -X POST http://localhost:8000/people/ \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Juan Pérez","email":"juan@escuela.edu","grade":"5to","group":"A"}'

# Subir rostro (reemplaza PERSON_ID e imagen)
curl -X POST "http://localhost:8000/faces/?person_id=PERSON_ID" \
  -F "image=@/ruta/a/imagen.jpg"
```

## Guía de ejecución local (scripts)

Asegúrate de tener **conda** disponible en tu terminal y crea/activa el entorno (igual en macOS y Windows):

```bash
conda env create -f environment.yml
conda activate face-recognition
```

Prepara datos y extrae rostros:

macOS / Linux:
```bash
mkdir -p input_images faces
# Copia imágenes con rostros a input_images/
python extracting_faces.py
```

Windows (PowerShell/CMD):
```powershell
mkdir input_images
mkdir faces
# Copia imágenes con rostros a input_images/
python extracting_faces.py
```

Ejecuta el reconocimiento con la webcam:

```bash
python f_recognition.py
```

## Funcionamiento

- Las imágenes de los rostros a detectar se cargan en la carpeta **input_images**, las imágenes pueden tener varias personas
- **extracting_faces.py**: El algoritmo reconoce un conjunto de rostro enumerándolos de 0 a n según la cantidad de rostros detectados guardándolos en la carpeta **faces**.
- **f_recognition.py** se encarga de correr el algoritmo para detectar rostros y generar un archivo .txt con las coincidencias encontradas.

### Notas multiplataforma

- En macOS: concede permisos de Cámara a Terminal/VS Code en Preferencias del Sistema > Privacidad y seguridad > Cámara.
- En Windows: revisa Configuración > Privacidad > Cámara y que ninguna app esté ocupando la cámara.
- El script selecciona automáticamente el backend de cámara según el sistema operativo.

## Tareas

- [ ] Modularizar el código. Se puede empezar por extraer la configuraciones básicas como las rutas y el target FPS en un archivo de configuración. Luego hay que corregir la documentación.
- [ ] Aumentar los FPS
- [ ] Agregar una interfaz web que no de vergüenza (####)