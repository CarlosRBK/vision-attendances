# Face Detection Feature

Feature para detección facial en tiempo real usando el microservicio de face-services.

## Estructura

```
face-detection/
├── api.ts                          # Cliente HTTP para face-services
├── types.ts                        # Tipos TypeScript
├── index.ts                        # Exports centralizados
├── hooks/
│   └── useFaceDetection.ts        # Hook personalizado para detección
├── components/
│   └── FaceDetectionCamera.tsx    # Componente de cámara con detección
└── pages/
    └── FaceDetectionPage.tsx      # Página de ejemplo
```

## Uso Básico

### 1. Usar el Componente

```tsx
import { FaceDetectionCamera } from '@/features/face-detection'

function MyComponent() {
  const handleDetection = (detection) => {
    console.log('Persona detectada:', detection.name)
  }

  return (
    <FaceDetectionCamera
      captureInterval={1000}
      onDetection={handleDetection}
      showStats={true}
    />
  )
}
```

### 2. Usar el Hook Directamente

```tsx
import { useFaceDetection } from '@/features/face-detection'

function MyCustomComponent() {
  const {
    isActive,
    detections,
    videoRef,
    canvasRef,
    start,
    stop
  } = useFaceDetection({
    captureInterval: 1000,
    onDetection: (detection) => {
      console.log('Detectado:', detection)
    }
  })

  return (
    <div>
      <video ref={videoRef} autoPlay playsInline />
      <canvas ref={canvasRef} className="hidden" />
      <button onClick={start}>Iniciar</button>
      <button onClick={stop}>Detener</button>
    </div>
  )
}
```

### 3. Usar la API Directamente

```tsx
import { detectFaces, getHealth, getAttendanceToday } from '@/features/face-detection'

// Detectar rostros en una imagen
const response = await detectFaces(imageBase64)
console.log('Detecciones:', response.detections)

// Verificar estado del servicio
const health = await getHealth()
console.log('Rostros conocidos:', health.known_faces)

// Obtener asistencia del día
const attendance = await getAttendanceToday()
console.log('Asistencias:', attendance.registered)
```

## Props del Componente

### FaceDetectionCamera

| Prop | Tipo | Default | Descripción |
|------|------|---------|-------------|
| `captureInterval` | `number` | `1000` | Intervalo entre capturas en ms |
| `onDetection` | `(detection: FaceDetection) => void` | - | Callback cuando se detecta un rostro conocido |
| `showStats` | `boolean` | `true` | Mostrar estadísticas en la UI |

## Hook Options

### useFaceDetection

| Option | Tipo | Default | Descripción |
|--------|------|---------|-------------|
| `captureInterval` | `number` | `1000` | Intervalo entre capturas en ms |
| `autoStart` | `boolean` | `false` | Auto-iniciar detección al montar |
| `onDetection` | `(detection: FaceDetection) => void` | - | Callback para detecciones |

## Tipos

```typescript
type FaceDetection = {
  name: string              // Nombre de la persona o "Desconocido"
  confidence: number        // Nivel de confianza (0-1)
  box: {
    x: number
    y: number
    width: number
    height: number
  }
}

type DetectResponse = {
  success: boolean
  detections: FaceDetection[]
  timestamp: string
  known_faces: number      // Total de rostros conocidos en BD
}
```

## Configuración

El feature se conecta al microservicio de face-services en:
```
http://localhost:5001
```

Asegúrate de que face-services esté ejecutándose:
```bash
docker-compose up face-services
```

## Ejemplo Completo

Ver `pages/FaceDetectionPage.tsx` para un ejemplo completo de implementación.

## Notas

- El componente captura frames de la cámara y los envía como base64
- Face-services procesa los frames y retorna las detecciones
- Las detecciones se renderizan en tiempo real sobre el video
- Los rostros conocidos aparecen en verde, desconocidos en rojo
- La asistencia se marca automáticamente en face-services
