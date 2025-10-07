# Vision Attendances 🎓👁️

Sistema de asistencia automatizado con reconocimiento facial en tiempo real, desarrollado con arquitectura de microservicios.

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Tecnologías](#-tecnologías)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Uso](#-instalación-y-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Endpoints API](#-endpoints-api)
- [Desarrollo](#-desarrollo)
- [Comandos Útiles](#-comandos-útiles)
- [Troubleshooting](#-troubleshooting)

## 🎯 Descripción

Vision Attendances es un sistema completo de gestión de asistencias que utiliza visión por computadora y reconocimiento facial para automatizar el registro de asistencia. El sistema captura frames desde la cámara del navegador, los procesa mediante algoritmos de detección facial y registra automáticamente la asistencia en una base de datos.

### Características principales

- ✅ **Reconocimiento facial en tiempo real** desde el navegador
- 📸 **Gestión de personas** con fotografías
- 📊 **Registro automático de asistencias** con prevención de duplicados
- 🔄 **Recarga automática** de rostros al agregar nuevas personas
- 🌐 **Arquitectura de microservicios** escalable y desacoplada
- 🐳 **Completamente dockerizado** para fácil despliegue
- 📱 **Interfaz moderna y responsiva** con React y TailwindCSS

## 🏗️ Arquitectura

El proyecto sigue una arquitectura de microservicios con tres componentes principales que se comunican entre sí:

```
┌─────────────────────────────────────────────────────────────────┐
│                         NAVEGADOR                                │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Frontend (React + TypeScript)                         │     │
│  │  - Captura frames de la cámara                         │     │
│  │  - Gestión de personas                                 │     │
│  │  - Visualización de asistencias                        │     │
│  │  Puerto: 3000                                          │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                    │                        │
                    │ HTTP                   │ HTTP
                    ▼                        ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  Backend (FastAPI + Python)  │  │  Face Services (Flask)       │
│  - API REST                  │  │  - Detección facial          │
│  - Gestión de personas       │◄─┤  - Reconocimiento facial    │
│  - Registro de asistencias   │  │  - Marca asistencias         │
│  - Almacenamiento de fotos   │  │  - Monitor de cambios        │
│  Puerto: 8000                │  │  Puerto: 5001                │
└──────────────────────────────┘  └──────────────────────────────┘
                    │                        │
                    │                        │
                    ▼                        │
┌──────────────────────────────┐            │
│  MongoDB Atlas               │            │
│  - Colección: people         │            │
│  - Colección: attendances    │            │
└──────────────────────────────┘            │
                                            │
                    ┌───────────────────────┘
                    ▼
┌──────────────────────────────┐
│  Volumen Compartido          │
│  - Fotos de personas         │
│  - Archivos de asistencia    │
└──────────────────────────────┘
```

### Flujo de funcionamiento

1. **Captura**: El frontend captura frames de la cámara del navegador usando la API `getUserMedia`
2. **Envío**: Los frames se convierten a base64 y se envían al servicio de detección facial vía HTTP POST
3. **Detección**: Face Services procesa el frame usando OpenCV y face_recognition para detectar rostros
4. **Reconocimiento**: Compara los rostros detectados con los encodings almacenados
5. **Registro**: Si se reconoce una persona, envía los datos al backend para registrar la asistencia
6. **Persistencia**: El backend guarda la asistencia en MongoDB con timestamp y datos del dispositivo
7. **Respuesta**: El frontend recibe y muestra los resultados en tiempo real

### Componentes

#### 1. Backend (FastAPI)
**Responsabilidades:**
- API REST para gestión de personas (CRUD completo)
- API REST para registro y consulta de asistencias
- Almacenamiento y servicio de archivos estáticos (fotos)
- Validación de datos con Pydantic
- Conexión a MongoDB Atlas con Motor (async)
- Health checks y documentación automática (Swagger/ReDoc)

**Arquitectura interna:**
```
backend/app/
├── core/              # Configuración, DB, logs
├── modules/
│   ├── people/        # Gestión de personas
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── storage.py
│   └── attendance/    # Gestión de asistencias
│       ├── router.py
│       ├── schemas.py
│       ├── service.py
│       └── repository.py
├── static/            # Archivos estáticos (fotos)
└── main.py           # Punto de entrada
```

#### 2. Face Services (Flask)
**Responsabilidades:**
- Detección facial con OpenCV (Haar Cascades)
- Reconocimiento facial con face_recognition (dlib)
- Carga y caché de rostros conocidos en memoria
- Monitor de cambios en carpeta de fotos (watchdog)
- Envío automático de asistencias al backend
- Prevención de duplicados en la misma sesión

**Características técnicas:**
- Procesamiento de imágenes en base64
- Umbral de confianza configurable (0.5)
- Recarga automática al detectar cambios en fotos
- Thread-safe con locks para acceso concurrente
- Extracción de nombres limpios (sin UUID)

#### 3. Frontend (React + TypeScript)
**Responsabilidades:**
- Interfaz de usuario moderna y responsiva
- Captura de video desde la cámara del navegador
- Gestión de personas (crear, editar, eliminar)
- Visualización de asistencias en tiempo real
- Carga y captura de fotos
- Manejo de estados con React Query

**Arquitectura interna:**
```
frontend/src/
├── features/          # Módulos por funcionalidad
│   ├── people/        # Gestión de personas
│   ├── attendance/    # Visualización de asistencias
│   └── face-detection/# Detección facial en vivo
├── shared/            # Componentes compartidos
│   ├── api/           # Cliente HTTP (axios)
│   ├── hooks/         # Hooks personalizados
│   ├── layouts/       # Layouts de la app
│   └── ui/            # Componentes UI reutilizables
└── lib/              # Utilidades y configuración
```

## 🛠️ Tecnologías

### Backend
- **FastAPI** 0.111.0 - Framework web moderno y rápido
- **Motor** 3.7+ - Driver async de MongoDB
- **Pydantic** 2.7.1 - Validación de datos
- **Uvicorn** 0.30.0 - Servidor ASGI
- **Python** 3.10+

### Face Services
- **Flask** 2.3+ - Framework web ligero
- **OpenCV** 4.8+ - Procesamiento de imágenes
- **face_recognition** 1.3.0 - Reconocimiento facial
- **dlib** 19.24.0 - Machine learning
- **watchdog** 3.0.0 - Monitor de archivos
- **NumPy** 1.23+ - Operaciones numéricas

### Frontend
- **React** 19.1 - Biblioteca UI
- **TypeScript** 5.8 - Tipado estático
- **Vite** 7.1 - Build tool
- **TanStack Query** 5.84 - Gestión de estado servidor
- **Axios** 1.11 - Cliente HTTP
- **Framer Motion** 12.23 - Animaciones
- **TailwindCSS** 4.1 - Estilos

### Infraestructura
- **Docker** & **Docker Compose** - Contenedorización
- **MongoDB Atlas** - Base de datos NoSQL
- **Nginx** - Servidor web (producción)

## 📦 Requisitos Previos

- **Docker Desktop** instalado y en ejecución
  - [Descargar para Windows](https://www.docker.com/products/docker-desktop)
  - [Descargar para Mac](https://www.docker.com/products/docker-desktop)
  - [Descargar para Linux](https://docs.docker.com/desktop/install/linux-install/)
- **MongoDB Atlas** (cuenta gratuita)
  - [Crear cuenta en MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
  - Crear un cluster gratuito
  - Obtener la URI de conexión
- **Navegador moderno** con soporte para `getUserMedia` (Chrome, Firefox, Edge, Safari)

## 🚀 Instalación y Uso

### Opción 1: Script Automatizado (Recomendado)

#### En Windows (PowerShell)
```powershell
.\docker-start.ps1
```

#### En Mac/Linux (Bash)
```bash
chmod +x docker-start.sh
./docker-start.sh
```

El script automatizado:
1. ✅ Verifica que Docker esté instalado
2. ✅ Detecta la versión de Docker Compose
3. ✅ Configura la plataforma correcta (ARM64 para Mac Silicon)
4. ✅ Crea el archivo `.env` desde `.env.example` si no existe
5. ✅ Te permite editar las credenciales de MongoDB
6. ✅ Construye las imágenes Docker
7. ✅ Inicia todos los servicios
8. ✅ Muestra las URLs de acceso

### Opción 2: Comandos Manuales

#### 1. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp backend/.env.example backend/.env

# Editar con tus credenciales de MongoDB
nano backend/.env  # o usa tu editor favorito
```

Configurar en `backend/.env`:
```env
MONGODB_URI=mongodb+srv://<usuario>:<password>@<cluster>/<db>?retryWrites=true&w=majority
DB_NAME=attendance_db
APP_VERSION=0.1.0
```

#### 2. Construir e iniciar los servicios

```bash
# Construir las imágenes
docker-compose build

# Iniciar los servicios en segundo plano
docker-compose up -d

# Ver los logs
docker-compose logs -f
```

### Opción 3: Usando Makefile

```bash
# Setup completo (copia .env, construye e inicia)
make dev

# O paso por paso:
make setup    # Copia .env.example
make build    # Construye imágenes
make up       # Inicia servicios
make logs     # Ver logs
```

### 🌐 Acceder a la aplicación

Una vez iniciados los servicios, accede a:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Face Services**: http://localhost:5001
- **Health Backend**: http://localhost:8000/health
- **Health Face Services**: http://localhost:5001/health

### 📝 Primer uso

1. **Agregar personas**:
   - Ve a http://localhost:3000
   - Haz clic en "Agregar Persona"
   - Completa el formulario (nombre, email, grado, grupo)
   - Sube una foto o captura desde la cámara
   - Guarda

2. **Iniciar detección**:
   - Ve a la sección de "Detección Facial"
   - Permite el acceso a la cámara cuando el navegador lo solicite
   - El sistema comenzará a detectar rostros automáticamente
   - Cuando reconozca a alguien, marcará la asistencia

3. **Ver asistencias**:
   - Ve a la sección de "Asistencias"
   - Verás el listado de asistencias del día
   - Puedes filtrar por fecha, persona o dispositivo

## 📁 Estructura del Proyecto

```
vision-attendances/
├── backend/                    # Servicio Backend (FastAPI)
│   ├── app/
│   │   ├── core/              # Configuración y utilidades core
│   │   ├── modules/           # Módulos de negocio
│   │   │   ├── people/        # Gestión de personas
│   │   │   └── attendance/    # Gestión de asistencias
│   │   ├── static/            # Archivos estáticos
│   │   │   └── people_photos/ # Fotos de personas
│   │   └── main.py           # Punto de entrada
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── face-services/             # Servicio de Detección Facial (Flask)
│   ├── asistencias/           # Archivos de asistencia (legacy)
│   ├── static/
│   │   └── people_photos/     # Fotos compartidas con backend
│   ├── main.py               # Servidor Flask
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                  # Aplicación Frontend (React)
│   ├── public/
│   ├── src/
│   │   ├── features/         # Módulos por funcionalidad
│   │   │   ├── people/       # Gestión de personas
│   │   │   ├── attendance/   # Visualización de asistencias
│   │   │   └── face-detection/ # Detección facial
│   │   ├── shared/           # Código compartido
│   │   │   ├── api/          # Cliente API
│   │   │   ├── hooks/        # Hooks personalizados
│   │   │   ├── layouts/      # Layouts
│   │   │   └── ui/           # Componentes UI
│   │   ├── lib/              # Utilidades
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── nginx.conf            # Configuración Nginx
│   ├── package.json
│   ├── .env
│   └── README.md
│
├── docker-compose.yml         # Orquestación de servicios
├── docker-start.sh           # Script de inicio (Mac/Linux)
├── docker-start.ps1          # Script de inicio (Windows)
├── Makefile                  # Comandos útiles
├── .env.example              # Variables de entorno globales
└── README.md                 # Este archivo
```

## 🔌 Endpoints API

### Backend (Puerto 8000)

#### Health
- `GET /health` - Estado del servicio

#### People
- `GET /people` - Listar personas (con filtros y paginación)
- `POST /people` - Crear persona (multipart/form-data)
- `GET /people/{id}` - Obtener persona por ID
- `PUT /people/{id}` - Actualizar persona
- `DELETE /people/{id}` - Eliminar persona
- `PUT /people/{id}/photo` - Subir/actualizar foto
- `DELETE /people/{id}/photo` - Eliminar foto

#### Attendances
- `GET /attendances/` - Listar asistencias (con filtros)
- `POST /attendances/` - Registrar asistencia
- `GET /attendances/today/` - Asistencias del día
- `GET /attendances/{id}` - Obtener asistencia por ID

### Face Services (Puerto 5001)

- `GET /health` - Estado del servicio
- `POST /detect` - Detectar y reconocer rostros en un frame
- `POST /reload` - Recargar rostros conocidos manualmente
- `GET /attendance/today` - Obtener asistencias del día (proxy al backend)

## 💻 Desarrollo

### Ejecutar servicios individualmente

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Face Services
```bash
cd face-services
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Hot Reload en Docker

Los servicios están configurados con volúmenes para hot reload en desarrollo:

- **Backend**: Los cambios en `backend/app/` se reflejan automáticamente
- **Face Services**: Los cambios en `face-services/` se reflejan automáticamente
- **Frontend**: Requiere rebuild (`docker-compose build frontend && docker-compose up -d frontend`)

### Variables de entorno

#### Backend (`backend/.env`)
```env
MONGODB_URI=mongodb+srv://...
DB_NAME=attendance_db
APP_VERSION=0.1.0
DEVICE_ID=default
DEBOUNCE_SECONDS=300
```

#### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000
```

#### Face Services (en `docker-compose.yml`)
```yaml
PYTHONUNBUFFERED=1
BACKEND_URL=http://backend:8000
DEVICE_ID=face-service-camera-1
```

## 🔧 Comandos Útiles

### Docker Compose

```bash
# Ver estado de los servicios
docker-compose ps

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f face-services
docker-compose logs -f frontend

# Reiniciar un servicio
docker-compose restart backend

# Reconstruir un servicio
docker-compose build backend
docker-compose up -d backend

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ elimina datos)
docker-compose down -v

# Limpiar todo (imágenes, contenedores, volúmenes)
docker-compose down -v --rmi all
```

### Makefile

```bash
make help              # Muestra todos los comandos disponibles
make setup             # Configuración inicial
make build             # Construir imágenes
make up                # Iniciar servicios
make down              # Detener servicios
make restart           # Reiniciar servicios
make logs              # Ver logs
make logs-backend      # Ver logs del backend
make logs-frontend     # Ver logs del frontend
make ps                # Estado de servicios
make clean             # Limpiar contenedores e imágenes
make clean-volumes     # Limpiar todo incluyendo volúmenes
make exec-backend      # Acceder al shell del backend
make exec-frontend     # Acceder al shell del frontend
make rebuild-backend   # Reconstruir solo backend
make rebuild-frontend  # Reconstruir solo frontend
make health            # Verificar salud de servicios
make dev               # Setup completo y inicio
```

### Acceder a los contenedores

```bash
# Backend
docker-compose exec backend sh

# Face Services
docker-compose exec face-services sh

# Frontend
docker-compose exec frontend sh
```

## 🐛 Troubleshooting

### El backend no se conecta a MongoDB

**Problema**: Error de conexión a MongoDB Atlas

**Solución**:
1. Verifica que la URI en `backend/.env` sea correcta
2. Asegúrate de que tu IP esté en la whitelist de MongoDB Atlas
3. Verifica que el usuario y contraseña sean correctos
4. Prueba la conexión desde MongoDB Compass

```bash
# Ver logs del backend
docker-compose logs backend
```

### Face Services no detecta rostros

**Problema**: El servicio no reconoce ningún rostro

**Solución**:
1. Verifica que haya fotos en `backend/app/static/people_photos/`
2. Recarga manualmente los rostros:
```bash
curl -X POST http://localhost:5001/reload
```
3. Verifica los logs:
```bash
docker-compose logs face-services
```
4. Asegúrate de que las fotos sean claras y muestren el rostro de frente

### El frontend no carga las imágenes

**Problema**: Las fotos de las personas no se muestran

**Solución**:
1. Verifica que `frontend/.env` tenga la variable `VITE_API_BASE_URL`
2. Reconstruye el frontend:
```bash
docker-compose build frontend
docker-compose up -d frontend
```

### Error de permisos en volúmenes (Linux)

**Problema**: Errores de permisos al escribir archivos

**Solución**:
```bash
# Dar permisos a las carpetas
sudo chmod -R 777 backend/app/static
sudo chmod -R 777 face-services/asistencias
```

### Docker Compose no se encuentra

**Problema**: `docker-compose: command not found`

**Solución**:
- En Docker Desktop moderno, usa `docker compose` (sin guión)
- O instala docker-compose v1:
```bash
# Mac
brew install docker-compose

# Linux
sudo apt-get install docker-compose
```

### El servicio de Face Services es lento

**Problema**: La detección facial tarda mucho

**Solución**:
1. Reduce la resolución de los frames enviados desde el frontend
2. Aumenta el intervalo entre frames
3. Considera usar un modelo más ligero (ajustar en `main.py`)
4. En Mac Silicon, asegúrate de usar la plataforma ARM64

### Cámara no funciona en el navegador

**Problema**: El navegador no accede a la cámara

**Solución**:
1. Usa HTTPS o `localhost` (requerido por `getUserMedia`)
2. Verifica los permisos del navegador
3. Prueba con otro navegador (Chrome recomendado)
4. En Mac, verifica los permisos del sistema

### Healthcheck falla constantemente

**Problema**: El backend no pasa el healthcheck

**Solución**:
1. Aumenta los timeouts en `docker-compose.yml`:
```yaml
healthcheck:
  timeout: 30s
  retries: 10
  start_period: 120s
```
2. Verifica que MongoDB esté accesible
3. Revisa los logs del backend

## 📊 Monitoreo y Logs

### Ver métricas de recursos

```bash
# Ver uso de recursos de los contenedores
docker stats

# Ver solo los servicios de este proyecto
docker stats vision-attendance-backend vision-attendance-frontend vision-attendance-face-detector
```

### Logs estructurados

Los servicios generan logs estructurados:

- **Backend**: Logs de FastAPI con timestamps
- **Face Services**: Logs detallados de detección con confianza
- **Frontend**: Logs de Nginx

### Debugging

Para debugging más detallado:

```bash
# Backend con logs de debug
docker-compose exec backend python -m uvicorn app.main:app --reload --log-level debug

# Face Services con debug de Flask
# Editar main.py y cambiar debug=True en app.run()
```

## 🚀 Producción

Para desplegar en producción:

1. **Configurar variables de entorno de producción**
2. **Usar HTTPS** (Nginx con Let's Encrypt)
3. **Configurar CORS** restrictivo en el backend
4. **Usar secrets** para credenciales sensibles
5. **Implementar rate limiting**
6. **Configurar backups** de MongoDB
7. **Monitoreo** con Prometheus/Grafana
8. **Logs centralizados** con ELK Stack

Ver `docker-compose.prod.yml` para configuración de producción.

## 📄 Licencia

MIT

## 👥 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la sección de [Troubleshooting](#-troubleshooting)
2. Busca en los [Issues](https://github.com/tu-usuario/vision-attendances/issues)
3. Crea un nuevo Issue con detalles del problema

---

**Desarrollado usando Python, React y Computer Vision**
