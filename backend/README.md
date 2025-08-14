
## Arquitectura (Modular Monolito)

API REST y tarea interna de reconocimiento en el mismo proceso. Organización por módulos (features): `people`.

- **Base de datos (MongoDB Atlas)**: colecciones `people`, con índices mínimos para consultas frecuentes.
 - **Media/Static**: archivos subidos (fotos) se guardan en disco bajo `MEDIA_ROOT` (por defecto `backend/app/static`) y se sirven vía `/static`.

### Estructura modular por carpetas

```
app/
  core/            # config, db (Motor), JWT, logs, errores
  modules/
    people/        # router, schemas, service, repository, storage
    attendances/   # router, schemas, service, repository, video_capture and face_detection
  shared/          # utils, tipos comunes
  main.py          # crea app, registra routers, startup/shutdown
```

Notas de diseño:

- Repositorios: acceso a Mongo (CRUD/queries) sin lógica de negocio.
- Services: reglas de negocio (debounce, validaciones) y coordinación entre repositorios.
- Routers: validación/parsing de requests y delegación a services.
- Storage: utilidades para I/O de archivos en disco (p. ej. `modules/people/storage.py`).

## Contratos de API (resumen)

- **People**

  - GET `/people` (filtros y paginación)
  - POST `/people` (alta)
  - GET `/people/{id}` (detalle)
  - PUT `/people/{id}` (edición)
  - PUT `/people/{id}/photo` (subir/reemplazar foto; multipart/form-data con `photo`)
  - DELETE `/people/{id}/photo` (eliminar foto)

- **Attendances**

  - GET `/attendances` (filtros y paginación)
  - POST `/attendances/start` (comienza detección facial para agregar asistencias)
  - POST `/attendances/stop` (finaliza el proceso de registro de asistencia)
  - DELETE `/attendances/{id}` (eliminar asistencia)

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

## Configuración inicial

1. Crear el entorno:
  ```bash
  # usa environment_mac.yml o environment_windows.yml dependiendo de tu sistema
  conda env create -f environment.yml
  ```

1. Configurar variables en `backend/.env`
  ```env
  MONGODB_URI=mongodb+srv://<usuario>:<password>@<cluster>/<db>?retryWrites=true&w=majority
  DB_NAME=attendance
  APP_VERSION=0.1.0
  # Opcional: raíz de media; por defecto `backend/app/static`
  # MEDIA_ROOT=c:/ruta/absoluta/a/static
  ```

## Ejecución

```bash
# Activar el entorno
conda activate vision-attendances-backend

# Ejecutar el servidor
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
# con autoreload en desarrollo:
# python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend

# En caso de obtener el sisguiente error:
# Please install `face_recognition_models` with this command before using # `face_recognition`:

# pip install git+https://github.com/ageitgey/face_recognition_models
pip install --upgrade setuptools
```

#### Verifica:
- Health: http://localhost:8000/health
- Swagger: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
- Media estática: http://localhost:8000/static (fotos bajo `/static/people_photos/...`)

### Subida de fotos (People)

- `POST /people`
  - Content-Type: `multipart/form-data`
  - Campos: `full_name` (requerido), `email?`, `grade?`, `group?`, `photo?` (archivo PNG/JPEG)
- `PUT /people/{id}/photo`
  - Content-Type: `multipart/form-data`
  - Campo: `photo` (archivo requerido)
- `DELETE /people/{id}/photo`
  - Elimina el archivo en disco y limpia el registro en BD.

Respuestas de People incluyen:
- `has_photo: boolean`
- `photo_url: string | null` → concatenar con el origen del backend en el frontend (ej.: `http://localhost:8000` + `photo_url`).

Notas:
- En Swagger UI (`/docs`) los campos de archivo se ven como selector de archivo.
- En ReDoc (`/redoc`) los campos de archivo pueden renderizarse como texto (comportamiento esperado del viewer), usar `/docs` para probar uploads.

## Face Services — Scripts locales (sección temporal)

1. Para ejecutar el extractor de caras (crear la carpeta `input_images` y meter una selfie en .jpeg o .jpg):
    ```bash
    python extracting_faces.py
    ```
    Obs: Esto debería crear una carpeta llamada `faces` que tendrá una imagen 150x150 del rostro de la imagen de `input_images`.

1. Para ejecutar el script de detección y asistencia:
    ```bash
    python f_recognition.py
    ```

