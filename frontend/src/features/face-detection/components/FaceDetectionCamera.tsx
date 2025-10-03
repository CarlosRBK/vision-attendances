import { Button } from '@/shared/ui/Button'
import { useFaceDetection } from '../hooks/useFaceDetection'
import type { FaceDetection } from '../types'
import { motion, AnimatePresence } from 'framer-motion'

export type FaceDetectionCameraProps = {
  /** Intervalo de captura en ms (default: 1000) */
  captureInterval?: number
  /** Callback cuando se detecta un rostro conocido */
  onDetection?: (detection: FaceDetection) => void
  /** Mostrar estadísticas en la UI */
  showStats?: boolean
}

export default function FaceDetectionCamera({
  captureInterval = 1000,
  onDetection,
  showStats = true
}: FaceDetectionCameraProps) {
  const {
    isActive,
    detections,
    isProcessing,
    error,
    stats,
    videoRef,
    canvasRef,
    start,
    stop
  } = useFaceDetection({
    captureInterval,
    onDetection
  })

  return (
    <div className="flex flex-col gap-4">
      {/* Video Container */}
      <div className="relative overflow-hidden rounded-xl border border-gray-200 bg-black">
        <div className="relative aspect-video">
          <video
            ref={videoRef}
            className="w-full h-full object-cover"
            playsInline
            muted
            autoPlay
            style={{ transform: 'scaleX(-1)' }} // Mirror effect
          />

          {/* Canvas oculto para capturar frames */}
          <canvas ref={canvasRef} className="hidden" />

          {/* Overlay con detecciones */}
          {isActive && detections.length > 0 && (
            <svg
              className="absolute inset-0 w-full h-full pointer-events-none"
              style={{ transform: 'scaleX(-1)' }} // Mirror para coincidir con video
            >
              {detections.map((detection, index) => {
                const isKnown = detection.name !== 'Desconocido'
                const color = isKnown ? '#10b981' : '#ef4444' // green-500 : red-500
                
                return (
                  <g key={index}>
                    {/* Rectángulo alrededor del rostro */}
                    <rect
                      x={`${(detection.box.x / 640) * 100}%`}
                      y={`${(detection.box.y / 480) * 100}%`}
                      width={`${(detection.box.width / 640) * 100}%`}
                      height={`${(detection.box.height / 480) * 100}%`}
                      fill="none"
                      stroke={color}
                      strokeWidth="3"
                      rx="4"
                    />
                    
                    {/* Label con el nombre */}
                    <text
                      x={`${(detection.box.x / 640) * 100}%`}
                      y={`${((detection.box.y - 10) / 480) * 100}%`}
                      fill={color}
                      fontSize="14"
                      fontWeight="bold"
                      style={{ textShadow: '0 0 4px rgba(0,0,0,0.8)' }}
                    >
                      {detection.name}
                    </text>
                  </g>
                )
              })}
            </svg>
          )}

          {/* Estado: Procesando */}
          {isActive && isProcessing && (
            <div className="absolute top-4 right-4 bg-blue-500 text-white px-3 py-1.5 rounded-full text-sm font-medium flex items-center gap-2">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
              Procesando...
            </div>
          )}

          {/* Estado: Inactivo */}
          {!isActive && (
            <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
              <div className="text-center text-white">
                <CameraIcon />
                <p className="mt-2 text-lg font-medium">Detección Facial</p>
                <p className="text-sm text-gray-300 mt-1">
                  Inicia la cámara para detectar rostros en tiempo real
                </p>
              </div>
            </div>
          )}

          {/* Error overlay */}
          {error && (
            <div className="absolute top-4 left-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg text-sm">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Controles */}
      <div className="flex flex-wrap gap-2 justify-center">
        {!isActive ? (
          <Button
            onClick={start}
            variant="primary"
            leftIcon={<PlayIcon />}
          >
            Iniciar Detección
          </Button>
        ) : (
          <Button
            onClick={stop}
            variant="outline"
            leftIcon={<StopIcon />}
          >
            Detener
          </Button>
        )}
      </div>

      {/* Estadísticas */}
      {showStats && isActive && (
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-gray-900">{stats.totalFrames}</div>
            <div className="text-xs text-gray-500 mt-1">Frames procesados</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-gray-900">{detections.length}</div>
            <div className="text-xs text-gray-500 mt-1">Rostros detectados</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-gray-900">{stats.knownFaces}</div>
            <div className="text-xs text-gray-500 mt-1">Personas conocidas</div>
          </div>
        </div>
      )}

      {/* Lista de detecciones */}
      {isActive && detections.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700">Detecciones actuales:</h3>
          <AnimatePresence mode="popLayout">
            {detections.map((detection, index) => (
              <motion.div
                key={`${detection.name}-${index}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className={`
                  flex items-center justify-between p-3 rounded-lg
                  ${detection.name === 'Desconocido' 
                    ? 'bg-red-50 border border-red-200' 
                    : 'bg-green-50 border border-green-200'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <div className={`
                    w-2 h-2 rounded-full
                    ${detection.name === 'Desconocido' ? 'bg-red-500' : 'bg-green-500'}
                  `} />
                  <span className={`font-medium ${
                    detection.name === 'Desconocido' ? 'text-red-900' : 'text-green-900'
                  }`}>
                    {detection.name}
                  </span>
                </div>
                {detection.name !== 'Desconocido' && (
                  <span className="text-xs text-green-600 font-medium">
                    {Math.round(detection.confidence * 100)}% confianza
                  </span>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  )
}

// Icons
function CameraIcon() {
  return (
    <svg className="w-16 h-16 mx-auto text-gray-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M23 19C23 19.5304 22.7893 20.0391 22.4142 20.4142C22.0391 20.7893 21.5304 21 21 21H3C2.46957 21 1.96086 20.7893 1.58579 20.4142C1.21071 20.0391 1 19.5304 1 19V8C1 7.46957 1.21071 6.96086 1.58579 6.58579C1.96086 6.21071 2.46957 6 3 6H7L9 3H15L17 6H21C21.5304 6 22.0391 6.21071 22.4142 6.58579C22.7893 6.96086 23 7.46957 23 8V19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M12 17C14.2091 17 16 15.2091 16 13C16 10.7909 14.2091 9 12 9C9.79086 9 8 10.7909 8 13C8 15.2091 9.79086 17 12 17Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function PlayIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M5 3L19 12L5 21V3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function StopIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="6" width="12" height="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
