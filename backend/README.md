
## Arquitectura (Modular Monolito)

API REST y tarea interna de reconocimiento en el mismo proceso. Organización por módulos (features): `people`.

- **Base de datos (MongoDB Atlas)**: colecciones `people`, con índices mínimos para consultas frecuentes.

### Estructura modular por carpetas

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

## Configuración inicial inicial

1. Crear el entorno:
  ```bash
  conda env create -f environment.yml
  ```

1. Configurar variables en `backend/.env`
  ```env
  MONGODB_URI=mongodb+srv://<usuario>:<password>@<cluster>/<db>?retryWrites=true&w=majority
  DB_NAME=attendance
  APP_VERSION=0.1.0
  ```

## Ejecución

```bash
# Activar el entorno
conda activate vission-attendances-backend

# Ejecutar el servidor
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
# con autoreload en desarrollo:
# python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

#### Verifica:
- Health: http://localhost:8000/health
- Swagger: http://localhost:8000/docs

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

