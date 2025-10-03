# 🎯 Vision Attendances - Sistema de Asistencias por Reconocimiento Facial

Sistema moderno de control de asistencias con reconocimiento facial en tiempo real, desarrollado con React, FastAPI y OpenCV.

## 🚀 Inicio Rápido (2 pasos)

### 1. Configurar MongoDB

```powershell
# Copiar y editar .env
Copy-Item backend\.env.example backend\.env
notepad backend\.env  # Agregar tu MONGODB_URI
```

### 2. Iniciar Todo

```powershell
.\docker-start.ps1
```

Abre **http://localhost:3000** y ¡listo! 🎉

---

## 📦 Stack Tecnológico

- **Frontend**: React 19 + TypeScript + Vite + TailwindCSS
- **Backend**: Python 3.9 + FastAPI + MongoDB
- **Face Detection**: OpenCV + face_recognition + Flask
- **Deployment**: Docker + Docker Compose

---

## 🎨 Características

### 👥 Gestión de Personas
- Registro con captura de foto (cámara o archivo)
- CRUD completo con validaciones
- Almacenamiento de fotos

### 📹 Detección Facial en Tiempo Real
- Detección automática vía cámara web
- Reconocimiento de rostros conocidos
- Registro automático de asistencias
- Feedback visual en tiempo real
- Estadísticas en vivo

---

## 🏗️ Arquitectura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │────▶│   MongoDB   │
│ React :3000 │     │ FastAPI:8000│     │    Atlas    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                        │
       │ HTTP POST (frames)          (fotos)   │
       ▼                                        │
┌─────────────┐                                │
│Face Services│◄───────────────────────────────┘
│ Flask :5001 │    Shared Volume
└─────────────┘
```

**Flujo de Detección:**
1. Frontend captura frames de cámara (navegador)
2. Envía frames a Face Services vía HTTP POST
3. Face Services detecta y reconoce rostros
4. Retorna detecciones en JSON
5. Frontend muestra resultados en tiempo real

---

## 📂 Estructura del Proyecto

```
vision-attendances/
├── backend/              # FastAPI + MongoDB
│   ├── app/
│   │   ├── core/        # Config y utilidades
│   │   └── modules/     # Features (people, etc.)
│   └── media/           # Fotos almacenadas
├── frontend/            # React + TypeScript
│   └── src/
│       └── features/    # Feature-based architecture
│           ├── people/           # Gestión de personas
│           └── face-detection/   # Detección facial
├── face-services/       # Microservicio Flask
│   ├── main.py         # API de detección
│   └── asistencias/    # Logs de asistencia
└── docker-compose.yml   # Orquestación
```

---

## 🛠️ Comandos Útiles

### Desarrollo

```powershell
# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f face-services

# Detener todo
docker-compose down

# Reconstruir imágenes
docker-compose build

# Restart de un servicio
docker-compose restart backend
```

### Endpoints

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Face Services**: http://localhost:5001/health

---

## 📖 Guía de Uso

### Registrar Personas

1. Abre http://localhost:3000
2. Pestaña **"👥 Personas"**
3. Click "Agregar Persona"
4. Completa datos y captura foto
5. Guarda

### Detectar Rostros

1. Pestaña **"📹 Detección Facial"**
2. Click "Iniciar Detección"
3. Permite acceso a cámara
4. ¡El sistema te reconoce automáticamente!

### Ver Asistencias (Por el momento con .txt hasta que guarden en la db)

```powershell
# Ver asistencias del día
curl http://localhost:5001/attendance/today

# O ver el archivo directamente
cat face-services\asistencias\asistencia_*.txt
```

---

## 🐛 Troubleshooting

### "MongoDB connection failed"
- Verifica `MONGODB_URI` en `backend/.env`
- Asegúrate de estar en la whitelist de MongoDB Atlas

### "No se puede acceder a la cámara"
- Da permisos de cámara al navegador
- Verifica que no esté en uso por otra app

### "Network Error" al detectar rostros
- Verifica que face-services esté corriendo: `docker-compose ps`
- Ve los logs: `docker-compose logs face-services`

### Las detecciones no funcionan
- Asegúrate de haber registrado personas con fotos
- Verifica: `curl http://localhost:5001/health`

---

## ⚙️ Configuración Avanzada

### Variables de Entorno

**Backend** (`backend/.env`):
```env
MONGODB_URI=mongodb+srv://...
DB_NAME=attendance_db
APP_VERSION=1.0.0
```

**Frontend** (`frontend/.env`):
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Ajustar Intervalo de Detección

Edita `frontend/src/features/face-detection/pages/FaceDetectionPage.tsx`:

```tsx
<FaceDetectionCamera
  captureInterval={1000}  // milisegundos (default: 1000)
  // ...
/>
```

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -m 'Agrega nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## 📄 Licencia

MIT

---

## 🎉 ¡Listo!

Ejecuta `.\docker-start.ps1` y abre http://localhost:3000


