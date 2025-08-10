# Sistema de Asistencias por Reconocimiento Facial

Este documento describe una arquitectura modular monolítica (MVP) para registro de asistencias mediante reconocimiento facial, con Backend (FastAPI), Frontend (React+TS+Vite) y base de datos en MongoDB Atlas. Incluye estructura de carpetas, contratos de API, esquema de datos, configuración y una guía de ejecución local de los scripts existentes.

## Arquitectura (Modular Monolito)

- **Backend (FastAPI)**: API REST y tarea interna de reconocimiento en el mismo proceso. Organización por módulos (features): `faces`.
- **Frontend (React + TypeScript + Vite)**: dashboard administrativo para login, personas, rostros, asistencias y configuración del dispositivo.
- **Base de datos (MongoDB Atlas)**: colecciones `faces`, con índices mínimos para consultas frecuentes.
- **Fuente de video**: webcam local inicialmente; extensible a cámara IP (RTSP) vía configuración en `/device`.






[---------------------   ESTO SE PUEDE MUDAR A SUS PROPIOS README DENTRO DE LAS CARPETAS DE BACK Y FRONT---------------------------]


### Backend — Estructura modular por carpetas

```
app/
  core/            # config, db (Motor), JWT, logs, errores
  modules/
    people/        # router, schemas, service, repository
    faces/         # router, schemas, service, repository
  shared/          # utils, tipos comunes
  main.py          # crea app, registra routers, startup/shutdown
```

Notas de diseño:

- Repositorios: acceso a Mongo (CRUD/queries) sin lógica de negocio.
- Services: reglas de negocio (debounce, validaciones) y coordinación entre repositorios.
- Routers: validación/parsing de requests y delegación a services.

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

- **People**

  - GET `/people` (filtros y paginación)
  - POST `/people` (alta)
  - GET `/people/{id}` (detalle)
  - PUT `/people/{id}` (edición)

- **Faces** (embeddings en backend)

- **Health**
  - GET `/health` → estado básico (status, version, uptime).

Errores estandarizados:

```json
{
  "error": {
    "code": "STRING_CODE",
    "message": "Detalle legible",
    "details": {}
  }
}
```

## Face Services — Scripts locales

1. Crear el entorno:
  ```bash
    conda env create -f environment.yml
  ```

1. Activar el entorno:
  ```bash
    conda activate face-recognition
  ```

1. Para ejecutar el extractor de caras (crear la carpeta `input_images` y meter una selfie en .jpeg o .jpg):
  ```bash
    python extracting_faces.py
  ```

  Obs: Esto debería crear una carpeta llamada `faces` que tendrá una imagen 150x150 del rostro de la imagen de `input_images`.

1. Para ejecutar el script de detección y asistencia:
  ```bash
    python f_recognition.py
  ```

---

## Backend — Instalación y ejecución (FastAPI)

1. Activar entorno conda

```bash
conda activate face-recognition
```

1. Configurar variables en `backend/.env`

```env
MONGODB_URI=mongodb+srv://<usuario>:<password>@<cluster>/<db>?retryWrites=true&w=majority
DB_NAME=attendance
APP_VERSION=0.1.0
```

1. Instalar dependencias del backend

```bash
python -m pip install -r backend/requirements.txt
```

Notas:
- Usamos `motor>=3.7,<4` y `pymongo>=4.9,<5`.
- Si notas errores por usar el intérprete equivocado, ejecuta con la ruta absoluta del entorno:
  `/Users/user/miniconda3/envs/face-recognition/bin/python -m pip install -r backend/requirements.txt`

1. Ejecutar el servidor

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
# con autoreload en desarrollo:
# python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

1. Verificar

- Health: http://localhost:8000/health
- Swagger: http://localhost:8000/docs
