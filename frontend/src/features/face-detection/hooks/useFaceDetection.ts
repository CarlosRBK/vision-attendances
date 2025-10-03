import { useState, useCallback, useRef, useEffect } from 'react'
import { detectFaces } from '../api'
import type { FaceDetection } from '../types'
import { toast } from 'sonner'

export type UseFaceDetectionOptions = {
  /** Intervalo en ms entre capturas (default: 1000ms) */
  captureInterval?: number
  /** Auto-iniciar detección cuando se monta el componente */
  autoStart?: boolean
  /** Callback cuando se detecta un rostro conocido */
  onDetection?: (detection: FaceDetection) => void
}

export function useFaceDetection(options: UseFaceDetectionOptions = {}) {
  const {
    captureInterval = 1000,
    autoStart = false,
    onDetection
  } = options

  const [isActive, setIsActive] = useState(false)
  const [detections, setDetections] = useState<FaceDetection[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState({
    totalFrames: 0,
    detectionsCount: 0,
    knownFaces: 0
  })

  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  // Limpiar recursos al desmontar
  useEffect(() => {
    return () => {
      stop()
    }
  }, [])

  // Auto-start si está habilitado
  useEffect(() => {
    if (autoStart) {
      start()
    }
  }, [autoStart])

  /**
   * Captura un frame del video y lo envía a face-services
   */
  const captureAndDetect = useCallback(async () => {
    const video = videoRef.current
    const canvas = canvasRef.current

    if (!video || !canvas || isProcessing) return

    try {
      setIsProcessing(true)

      // Capturar frame
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      ctx.drawImage(video, 0, 0)
      const frameBase64 = canvas.toDataURL('image/jpeg', 0.8)

      // Enviar a face-services
      const response = await detectFaces(frameBase64)

      // Actualizar detecciones
      setDetections(response.detections)
      setStats(prev => ({
        totalFrames: prev.totalFrames + 1,
        detectionsCount: prev.detectionsCount + response.detections.length,
        knownFaces: response.known_faces
      }))

      // Callback para detecciones conocidas
      if (onDetection) {
        response.detections
          .filter(d => d.name !== 'Desconocido')
          .forEach(onDetection)
      }

      setError(null)

    } catch (err: any) {
      console.error('Error en detección facial:', err)
      setError(err.message || 'Error al procesar frame')
    } finally {
      setIsProcessing(false)
    }
  }, [isProcessing, onDetection])

  /**
   * Inicia la cámara y el proceso de detección
   */
  const start = useCallback(async () => {
    try {
      setError(null)

      // Solicitar cámara
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 }
        },
        audio: false
      })

      streamRef.current = stream

      // Asignar al video
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }

      setIsActive(true)

      // Iniciar captura periódica
      intervalRef.current = setInterval(() => {
        captureAndDetect()
      }, captureInterval)

      toast.success('Detección facial iniciada', {
        description: 'La cámara está activa y detectando rostros'
      })

    } catch (err: any) {
      console.error('Error al iniciar cámara:', err)
      
      if (err.name === 'NotAllowedError') {
        setError('Permiso de cámara denegado')
        toast.error('Permiso denegado', {
          description: 'Por favor permite el acceso a la cámara'
        })
      } else if (err.name === 'NotFoundError') {
        setError('No se encontró cámara')
        toast.error('Cámara no encontrada', {
          description: 'No se detectó ninguna cámara en tu dispositivo'
        })
      } else {
        setError('Error al acceder a la cámara')
        toast.error('Error de cámara', {
          description: err.message || 'No se pudo acceder a la cámara'
        })
      }
    }
  }, [captureInterval, captureAndDetect])

  /**
   * Detiene la cámara y el proceso de detección
   */
  const stop = useCallback(() => {
    // Detener intervalo
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    // Detener stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }

    // Limpiar video
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }

    setIsActive(false)
    setDetections([])
    setIsProcessing(false)

    toast.info('Detección detenida', {
      description: 'La cámara ha sido desactivada'
    })
  }, [])

  /**
   * Reinicia las estadísticas
   */
  const resetStats = useCallback(() => {
    setStats({
      totalFrames: 0,
      detectionsCount: 0,
      knownFaces: 0
    })
  }, [])

  return {
    // Estado
    isActive,
    detections,
    isProcessing,
    error,
    stats,

    // Refs para el componente
    videoRef,
    canvasRef,

    // Acciones
    start,
    stop,
    resetStats
  }
}
