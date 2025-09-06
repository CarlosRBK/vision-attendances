# Documentación Técnica del Backend Vision-Attendance

## Índice
1. [Introducción](#introducción)
2. [Visión General de la Arquitectura](#visión-general-de-la-arquitectura)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Configuración del Sistema](#configuración-del-sistema)
6. [Módulos Principales](#módulos-principales)
   - [Módulo de Personas](#módulo-de-personas)
   - [Módulo de Asistencias](#módulo-de-asistencias)
   - [Sistema de Detección Facial](#sistema-de-detección-facial)
7. [Flujos de Trabajo](#flujos-de-trabajo)
8. [Gestión de Archivos y Medios](#gestión-de-archivos-y-medios)
9. [API y Endpoints](#api-y-endpoints)
10. [Base de Datos](#base-de-datos)
11. [Guía de Integración con Frontend](#guía-de-integración-con-frontend)

## Introducción

**Vision-Attendance** es un sistema de control de asistencia basado en reconocimiento facial. Esta aplicación permite automatizar el registro de asistencia mediante la identificación de personas utilizando una cámara y algoritmos de reconocimiento facial, eliminando la necesidad de métodos tradicionales como listas en papel o tarjetas de identificación.

**Propósito del Sistema**: Proveer un método eficiente, preciso y moderno para registrar la asistencia en entornos educativos o laborales mediante tecnología de reconocimiento facial.

**Componentes Principales**:
- **Backend**: Servidor que gestiona la lógica de negocio, procesa las imágenes, realiza el reconocimiento facial y almacena los datos.
- **Frontend**: Interfaz de usuario para administrar personas, visualizar asistencias y controlar el sistema.

## Visión General de la Arquitectura

El backend de Vision-Attendance está construido siguiendo una **arquitectura modular** que separa las responsabilidades en componentes claramente definidos. Este diseño facilita el mantenimiento, escalabilidad y comprensión del sistema.

**Diagrama de Alto Nivel**:

```
┌───────────────────┐     ┌───────────────────────────┐     ┌───────────────────┐
│                   │     │                           │     │                   │
│     Frontend      │◄────┤       Backend API         │◄────┤   Base de Datos   │
│     (React)       │     │       (FastAPI)           │     │    (MongoDB)      │
│                   │     │                           │     │                   │
└───────────────────┘     └───────────────────────────┘     └───────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                          │   Sistema de Visión   │
                          │      Computacional    │
                          │                       │
                          └───────────────────────┘
```

**Flujo de Datos**:
1. La cámara captura imágenes de las personas.
2. El sistema de visión computacional detecta y reconoce rostros.
3. La API backend procesa esta información y la almacena en la base de datos.
4. El frontend consulta la API para mostrar información y permitir la gestión del sistema.

## Tecnologías Utilizadas

El backend de Vision-Attendance está construido sobre un stack tecnológico moderno y potente:

- **FastAPI**: Framework web de Python que facilita la creación de APIs RESTful de alto rendimiento.
- **MongoDB**: Base de datos NoSQL orientada a documentos para almacenamiento flexible de datos.
- **Motor**: Cliente asincrónico para MongoDB diseñado para trabajar con FastAPI.
- **OpenCV**: Biblioteca de visión por computadora utilizada para procesamiento de imágenes y detección facial.
- **Pydantic**: Biblioteca para validación de datos y configuración basada en tipos de Python.
- **Python-Multipart**: Para manejo de formularios multipart (subida de archivos).

## Estructura del Proyecto

El backend sigue una estructura organizada por módulos funcionales:

```
backend/
├── app/
│   ├── core/               # Configuraciones centrales del sistema
│   │   └── config.py       # Configuración y variables de entorno
│   ├── modules/            # Módulos funcionales
│   │   ├── people/         # Gestión de personas
│   │   └── attendances/    # Gestión de asistencias y detección facial
│   ├── static/             # Archivos estáticos (fotos de personas)
│   ├── utils/              # Utilidades varias
│   ├── main.py             # Punto de entrada de la aplicación
│   └── __init__.py
├── .env.example            # Plantilla de variables de entorno
└── environment_*.yml       # Configuración de entorno para diferentes SO
```

## Configuración del Sistema

El sistema utiliza variables de entorno para su configuración, lo que permite modificar el comportamiento sin cambiar el código.

**Variables de entorno principales**:

| Variable | Descripción | Valor por defecto |
|----------|-------------|------------------|
| MONGODB_URI | URL de conexión a MongoDB | mongodb://localhost:27017 |
| DB_NAME | Nombre de la base de datos | attendance_db |
| MEDIA_ROOT | Directorio para almacenar archivos estáticos | app/static |
| DEVICE_ID | Identificador del dispositivo de captura | default |
| DEVICE_TYPE | Tipo de dispositivo (webcam/rtsp) | webcam |
| DEVICE_WIDTH | Ancho de captura de la cámara | 640 |
| DEVICE_HEIGHT | Alto de captura de la cámara | 480 |
| DEVICE_FPS | Fotogramas por segundo | 30 |
| DEBOUNCE_SECONDS | Tiempo mínimo entre registros de asistencia | 300 |

Para configurar el sistema, copia `.env.example` a `.env` y modifica los valores según necesites.

## Módulos Principales

### Módulo de Personas

Este módulo gestiona la información de todas las personas que serán reconocidas por el sistema.

**Funcionalidades principales**:

- **Registro de personas**: Almacena datos básicos como nombre, email, grado y grupo.
- **Gestión de fotografías**: Permite asociar una imagen facial a cada persona para su posterior reconocimiento.
- **CRUD completo**: Crear, leer, actualizar y eliminar registros de personas.

**Estructura del módulo**:
```
people/
├── __init__.py
├── repository.py    # Acceso a datos en MongoDB
├── router.py        # Endpoints de API
├── schemas.py       # Modelos de datos y validación
├── service.py       # Lógica de negocio
└── storage.py       # Gestión de almacenamiento de fotos
```

**Modelo de datos de una Persona**:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | string | Identificador único |
| full_name | string | Nombre completo |
| email | string (opcional) | Correo electrónico |
| grade | string (opcional) | Grado o curso |
| group | string (opcional) | Grupo o división |
| has_photo | boolean | Indica si tiene foto asociada |
| photo_url | string (opcional) | URL relativa de la foto |
| created_at | datetime | Fecha de creación |
| updated_at | datetime | Fecha de última actualización |

### Módulo de Asistencias

Este módulo maneja el proceso de detección facial y registro de asistencias.

**Funcionalidades principales**:

- **Detección facial**: Identifica rostros en tiempo real mediante la cámara.
- **Reconocimiento facial**: Compara los rostros detectados con la base de datos de personas.
- **Registro de asistencias**: Almacena automáticamente la fecha y hora cuando una persona es reconocida.
- **Consulta de asistencias**: Permite filtrar y visualizar los registros de asistencia.

**Estructura del módulo**:
```
attendances/
├── __init__.py
├── extract_face.py     # Extracción de características faciales
├── face_detector.py    # Detección y reconocimiento facial
├── loop_manager.py     # Gestión del bucle de captura
├── repository.py       # Acceso a datos en MongoDB
├── router.py           # Endpoints de API
├── schema.py           # Modelos de datos y validación
├── service.py          # Lógica de negocio
└── video_capture.py    # Gestión de captura de video
```

**Modelo de datos de una Asistencia**:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | string | Identificador único |
| person_id | string | ID de la persona reconocida |
| attendance_time | datetime | Momento exacto del registro |

### Sistema de Detección Facial

El corazón del sistema Vision-Attendance es su capacidad de detectar y reconocer rostros automáticamente.

**Componentes clave**:

- **Captura de video**: Gestiona la conexión con la cámara y obtiene fotogramas en tiempo real.
- **Detector facial**: Identifica la presencia y ubicación de rostros humanos en las imágenes.
- **Extractor de características**: Obtiene información distintiva de cada rostro detectado.
- **Comparador facial**: Compara los rostros detectados con la base de datos de personas registradas.
- **Gestor de debounce**: Evita registros múltiples de la misma persona en un corto período de tiempo.

**Flujo del proceso de detección**:

1. Captura continua de imágenes desde la cámara.
2. Análisis de cada fotograma para detectar rostros.
3. Para cada rostro detectado, extracción de características faciales.
4. Comparación de estas características con las almacenadas en la base de datos.
5. Si hay coincidencia con confianza suficiente, se registra la asistencia.
6. Se aplica un "debounce" para evitar registros duplicados en corto tiempo.

## Flujos de Trabajo

### 1. Registro de Personas

**Descripción**: Proceso para añadir nuevas personas al sistema.

**Pasos**:
1. Acceder al endpoint `/people/` con método POST.
2. Enviar datos personales (nombre, email, etc.) y opcionalmente una fotografía.
3. El sistema valida los datos y la imagen (si se proporciona).
4. Se almacenan los datos personales en MongoDB.
5. Si hay foto, se guarda en el sistema de archivos y se asocia a la persona.

**Ejemplo de uso**:
```
POST /people/
Content-Type: multipart/form-data

full_name: "Juan Pérez"
email: "juan@example.com"
grade: "5to"
group: "A"
photo: [archivo binario]
```

### 2. Actualización de Personas

**Descripción**: Modificación de los datos de una persona existente.

**Pasos**:
1. Acceder al endpoint `/people/{person_id}` con método PUT.
2. Enviar los nuevos datos que se desean actualizar.
3. El sistema verifica que la persona exista.
4. Se actualizan los campos necesarios.

### 3. Gestión de Fotografías

**Descripción**: Agregar, actualizar o eliminar la foto de una persona.

**Pasos para agregar/actualizar**:
1. Acceder al endpoint `/people/{person_id}/photo` con método PUT.
2. Enviar la nueva fotografía en formato multipart/form-data.
3. El sistema valida el formato y calidad de la imagen.
4. Si la persona ya tenía foto, se elimina la anterior.
5. Se guarda la nueva imagen y se actualiza la referencia.

**Pasos para eliminar**:
1. Acceder al endpoint `/people/{person_id}/photo` con método DELETE.
2. El sistema elimina el archivo físico.
3. Se actualiza el registro para reflejar que ya no tiene foto.

### 4. Iniciar Detección de Asistencias

**Descripción**: Activa el sistema de reconocimiento facial para registrar asistencias.

**Pasos**:
1. Acceder al endpoint `/attendances/start` con método POST.
2. El sistema inicia la captura de video y el proceso de detección.
3. Por cada rostro reconocido, se registra una asistencia en la base de datos.
4. El proceso continúa hasta que se detiene explícitamente.

### 5. Consulta de Asistencias

**Descripción**: Obtener el historial de asistencias con posibilidad de filtrado.

**Pasos**:
1. Acceder al endpoint `/attendances/` con método GET.
2. Opcionalmente, añadir filtros como rango de fechas o ID de persona.
3. El sistema consulta la base de datos y devuelve los registros que cumplen los criterios.

**Ejemplo de uso**:
```
GET /attendances/?person_id=507f1f77bcf86cd799439011&start_time=2023-05-01:00:00:00&end_time=2023-05-31:23:59:59
```

## Gestión de Archivos y Medios

El sistema almacena y gestiona fotografías de las personas para el reconocimiento facial.

**Almacenamiento de imágenes**:
- Las fotos se guardan en el directorio especificado por `MEDIA_ROOT` (por defecto: `app/static`).
- Cada imagen recibe un nombre único basado en el ID de la persona y un timestamp.
- Las imágenes se sirven a través del endpoint `/static/` para acceso desde el frontend.

**Formatos soportados**:
- JPEG (.jpg, .jpeg)
- PNG (.png)

**Proceso de manipulación de imágenes**:
1. Al recibir una imagen, se valida su formato y tamaño.
2. Se procesa para optimizar su uso en reconocimiento facial (redimensionado, normalización).
3. Se almacena en el sistema de archivos.
4. Se genera una URL relativa que se asocia a la persona en la base de datos.

## API y Endpoints

### Endpoints del Módulo de Personas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/people/` | Lista todas las personas registradas |
| POST | `/people/` | Crea una nueva persona |
| GET | `/people/{person_id}` | Obtiene una persona específica |
| PUT | `/people/{person_id}` | Actualiza los datos de una persona |
| PUT | `/people/{person_id}/photo` | Establece o actualiza la foto |
| DELETE | `/people/{person_id}/photo` | Elimina la foto de una persona |
| DELETE | `/people/{person_id}` | Elimina una persona y su foto |

### Endpoints del Módulo de Asistencias

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/attendances/` | Lista las asistencias registradas |
| POST | `/attendances/start` | Inicia el proceso de detección facial |
| POST | `/attendances/stop` | Detiene el proceso de detección facial |
| DELETE | `/attendances/{attendance_id}` | Elimina un registro de asistencia |

### Endpoint de Estado

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Verifica el estado del sistema y su tiempo de actividad |

## Base de Datos

Vision-Attendance utiliza MongoDB como sistema de base de datos, lo que permite un almacenamiento flexible y eficiente.

**Colecciones principales**:

1. **people**: Almacena la información de las personas registradas.

   Ejemplo de documento:
   ```json
   {
     "_id": "507f1f77bcf86cd799439011",
     "full_name": "Juan Pérez",
     "email": "juan@example.com",
     "grade": "5to",
     "group": "A",
     "has_photo": true,
     "photo_url": "/static/507f1f77bcf86cd799439011.jpg",
     "created_at": "2023-05-01T12:00:00Z",
     "updated_at": "2023-05-02T15:30:00Z"
   }
   ```

2. **attendances**: Registra las asistencias detectadas.

   Ejemplo de documento:
   ```json
   {
     "_id": "60a6c52e9f3779e8b51d0f7c",
     "person_id": "507f1f77bcf86cd799439011",
     "attendance_time": "2023-05-03T08:15:27Z"
   }
   ```

**Índices optimizados**:
- `people.full_name`: Para búsquedas por nombre.
- `attendances.timestamp`: Para filtrado por fecha/hora.
- `attendances.person_id`: Para consultas de asistencia por persona.

## Guía de Integración con Frontend

El backend proporciona una API RESTful completa que el frontend puede consumir. Aspectos clave para la integración:

### 1. Autenticación
Actualmente el sistema no implementa autenticación, lo que significa que todos los endpoints son accesibles públicamente. En un entorno de producción, se recomienda implementar algún mecanismo de autenticación.

### 2. Formato de Respuestas
Todas las respuestas exitosas siguen un formato JSON estándar. Los errores incluyen un código HTTP apropiado y un mensaje descriptivo.

### 3. Carga de Archivos
Para subir imágenes, el frontend debe enviar solicitudes como `multipart/form-data` con el campo `photo` conteniendo el archivo de imagen.

### 4. URLs de Medios
Las URLs de fotos devueltas por la API (campo `photo_url`) son relativas al backend. El frontend debe concatenar la URL base del backend para construir la URL completa.

### 5. Manejo de Errores
El backend devuelve códigos HTTP adecuados para diferentes situaciones:
- `200/201`: Operación exitosa
- `400`: Datos inválidos o error de validación
- `404`: Recurso no encontrado
- `500`: Error interno del servidor

### 6. Monitoreo del Estado
El endpoint `/health` puede utilizarse para verificar si el servicio está funcionando correctamente.
