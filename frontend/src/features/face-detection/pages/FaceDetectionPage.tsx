import { FaceDetectionCamera } from '../'
import type { FaceDetection } from '../types'
import { toast } from 'sonner'

export default function FaceDetectionPage() {
  const handleDetection = (detection: FaceDetection) => {
    // Callback cuando se detecta un rostro conocido
    console.log('Rostro detectado:', detection)
    
    // Opcional: mostrar notificación
    toast.success(`¡${detection.name} detectado!`, {
      description: `Confianza: ${Math.round(detection.confidence * 100)}%`
    })
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Detección Facial en Tiempo Real
        </h1>
        <p className="text-gray-600 mt-2">
          El sistema detecta y reconoce rostros automáticamente usando tu cámara web
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-6">
        <FaceDetectionCamera
          captureInterval={1000}
          onDetection={handleDetection}
          showStats={true}
        />
      </div>

      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h2 className="font-semibold text-blue-900 mb-2">
          💡 Cómo funciona
        </h2>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• La cámara captura frames cada segundo</li>
          <li>• Los frames se envían al microservicio de detección facial</li>
          <li>• El sistema compara rostros con la base de datos</li>
          <li>• Las detecciones aparecen en tiempo real sobre el video</li>
        </ul>
      </div>
    </div>
  )
}
