import { Button } from '@/shared/ui/Button'
import { useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import { motion, AnimatePresence } from 'framer-motion'

export type WebcamCaptureProps = {
  value?: string | null
  onChange?: (base64: string | null) => void
  aspectRatio?: number // width / height
}

type CameraErrorType = 'permission' | 'notFound' | 'notReadable' | 'other' | null

export default function WebcamCapture({ value, onChange, aspectRatio = 1 }: WebcamCaptureProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [captured, setCaptured] = useState<string | null>(value ?? null)
  const [active, setActive] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [cameraError, setCameraError] = useState<CameraErrorType>(null)
  const [countdown, setCountdown] = useState<number | null>(null)

  useEffect(() => {
    return () => {
      stop()
    }
  }, [])

  // Efecto para el contador de captura automática
  useEffect(() => {
    if (countdown === null || countdown <= 0) return

    const timer = setTimeout(() => {
      if (countdown === 1) {
        capture()
        setCountdown(null)
      } else {
        setCountdown(countdown - 1)
      }
    }, 1000)

    return () => clearTimeout(timer)
  }, [countdown])

  const start = async () => {
    try {
      setIsLoading(true)
      setCameraError(null)

      const media = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      })

      setStream(media)
      if (videoRef.current) {
        videoRef.current.srcObject = media
        await videoRef.current.play()
      }
      setActive(true)
    } catch (e: any) {
      console.error('Error al iniciar la cámara:', e)

      // Determinar el tipo de error
      if (e.name === 'NotAllowedError') {
        setCameraError('permission')
        toast.error('Permiso denegado', {
          description: 'No se pudo acceder a la cámara porque se denegó el permiso.'
        })
      } else if (e.name === 'NotFoundError') {
        setCameraError('notFound')
        toast.error('Cámara no encontrada', {
          description: 'No se detectó ninguna cámara en tu dispositivo.'
        })
      } else if (e.name === 'NotReadableError') {
        setCameraError('notReadable')
        toast.error('Cámara no disponible', {
          description: 'La cámara está siendo usada por otra aplicación.'
        })
      } else {
        setCameraError('other')
        toast.error('Error de cámara', {
          description: 'Ocurrió un error al intentar acceder a la cámara.'
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  const stop = () => {
    stream?.getTracks().forEach((t) => t.stop())
    setStream(null)
    setActive(false)
    setCountdown(null)
  }

  const startCountdown = () => {
    setCountdown(3)
  }

  const capture = () => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return

    const vw = video.videoWidth
    const vh = video.videoHeight
    // Crop to desired aspect ratio
    const targetAR = aspectRatio
    let sw = vw
    let sh = vw / targetAR
    if (sh > vh) {
      sh = vh
      sw = vh * targetAR
    }
    const sx = (vw - sw) / 2
    const sy = (vh - sh) / 2

    canvas.width = sw
    canvas.height = sh
    const ctx = canvas.getContext('2d')!
    ctx.drawImage(video, sx, sy, sw, sh, 0, 0, sw, sh)
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9)
    setCaptured(dataUrl)
    onChange?.(dataUrl)
    stop()

    toast.success('Foto capturada', {
      description: 'La imagen se ha guardado correctamente.'
    })
  }

  const clear = () => {
    setCaptured(null)
    onChange?.(null)
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validar tipo de archivo
    if (!file.type.startsWith('image/')) {
      toast.error('Formato no soportado', {
        description: 'Por favor selecciona una imagen (JPG, PNG, etc).'
      })
      return
    }

    // Validar tamaño (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Imagen demasiado grande', {
        description: 'El tamaño máximo permitido es 5MB.'
      })
      return
    }

    const reader = new FileReader()
    reader.onload = (event) => {
      const dataUrl = event.target?.result as string
      setCaptured(dataUrl)
      onChange?.(dataUrl)

      toast.success('Imagen cargada', {
        description: 'La imagen se ha cargado correctamente.'
      })
    }
    reader.readAsDataURL(file)
  }

  const triggerFileInput = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="relative overflow-hidden rounded-xl border border-gray-100 bg-gray-50">
        {captured ? (
          <div className="relative">
            <img src={captured} alt="Foto capturada" className="block w-full h-auto" />
            <div className="absolute top-2 right-2 bg-black/50 rounded-full p-1.5 cursor-pointer hover:bg-black/70 transition-colors"
              onClick={clear}
              title="Eliminar foto">
              <TrashIcon />
            </div>
          </div>
        ) : (
          <div className="relative">
            <div className="aspect-square w-full bg-black/10 grid place-items-center">
              {active ? (
                <div className="relative w-full h-full">
                  <video ref={videoRef} className="h-full w-full object-cover" playsInline muted />

                  {/* Overlay para el contador */}
                  <AnimatePresence>
                    {countdown !== null && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-black/40 grid place-items-center">
                        <motion.div
                          key={countdown}
                          initial={{ scale: 1.5, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          exit={{ scale: 0.5, opacity: 0 }}
                          className="text-6xl font-bold text-white">
                          {countdown}
                        </motion.div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ) : cameraError ? (
                <div className="text-center p-6 flex flex-col items-center gap-3">
                  <div className="rounded-full bg-red-100 p-3 mb-2">
                    <CameraOffIcon />
                  </div>
                  <h3 className="text-base font-medium">
                    {cameraError === 'permission' && 'Permiso de cámara denegado'}
                    {cameraError === 'notFound' && 'No se encontró ninguna cámara'}
                    {cameraError === 'notReadable' && 'Cámara no disponible'}
                    {cameraError === 'other' && 'Error al acceder a la cámara'}
                  </h3>
                  <p className="text-sm text-[--muted-foreground]">
                    {cameraError === 'permission' && 'Por favor, permite el acceso a la cámara en la configuración de tu navegador.'}
                    {cameraError === 'notFound' && 'No se detectó ninguna cámara en tu dispositivo. Puedes subir una imagen en su lugar.'}
                    {cameraError === 'notReadable' && 'La cámara está siendo usada por otra aplicación. Ciérrala e intenta nuevamente.'}
                    {cameraError === 'other' && 'Ocurrió un error al intentar acceder a la cámara. Puedes subir una imagen en su lugar.'}
                  </p>
                </div>
              ) : (
                <div className="text-center p-6 flex flex-col items-center gap-3">
                  <div className="rounded-full bg-blue-100 p-3 mb-2">
                    <CameraIcon />
                  </div>
                  <h3 className="text-base font-medium">Captura una foto</h3>
                  <p className="text-sm text-[--muted-foreground]">
                    Habilita tu cámara para tomar una foto o sube una imagen desde tu dispositivo.
                  </p>
                </div>
              )}
            </div>
            <canvas ref={canvasRef} className="hidden" />
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2 justify-center">
        {!active && !captured && (
          <>
            <Button
              variant="outline"
              type="button"
              onClick={start}
              isLoading={isLoading}
              leftIcon={!isLoading && <CameraIcon />}
              disabled={isLoading}
            >
              {isLoading ? 'Iniciando cámara...' : 'Habilitar cámara'}
            </Button>
            <Button
              variant="secondary"
              type="button"
              onClick={triggerFileInput}
              leftIcon={<UploadIcon />}
              disabled={isLoading}
            >
              Subir imagen
            </Button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="image/*"
              className="hidden"
            />
          </>
        )}

        {active && (
          <>
            <Button
              type="button"
              onClick={capture}
              variant="primary"
              leftIcon={<CaptureIcon />}
            >
              Capturar ahora
            </Button>
            <Button
              type="button"
              onClick={startCountdown}
              variant="secondary"
              leftIcon={<TimerIcon />}
              disabled={countdown !== null}
            >
              {countdown !== null ? `Capturando en ${countdown}...` : 'Temporizador (3s)'}
            </Button>
            <Button
              type="button"
              onClick={stop}
              variant="outline"
              leftIcon={<CloseIcon />}
            >
              Cancelar
            </Button>
          </>
        )}

        {captured && (
          <>
            <Button
              type="button"
              onClick={clear}
              variant="outline"
              leftIcon={<RefreshIcon />}
            >
              Tomar otra foto
            </Button>
            <Button
              type="button"
              onClick={triggerFileInput}
              variant="secondary"
              leftIcon={<UploadIcon />}
            >
              Cambiar imagen
            </Button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="image/*"
              className="hidden"
            />
          </>
        )}
      </div>
    </div>
  )
}

// Icons
function CameraIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M23 19C23 19.5304 22.7893 20.0391 22.4142 20.4142C22.0391 20.7893 21.5304 21 21 21H3C2.46957 21 1.96086 20.7893 1.58579 20.4142C1.21071 20.0391 1 19.5304 1 19V8C1 7.46957 1.21071 6.96086 1.58579 6.58579C1.96086 6.21071 2.46957 6 3 6H7L9 3H15L17 6H21C21.5304 6 22.0391 6.21071 22.4142 6.58579C22.7893 6.96086 23 7.46957 23 8V19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M12 17C14.2091 17 16 15.2091 16 13C16 10.7909 14.2091 9 12 9C9.79086 9 8 10.7909 8 13C8 15.2091 9.79086 17 12 17Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function CameraOffIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M1 1L23 23" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M21 21H3C2.46957 21 1.96086 20.7893 1.58579 20.4142C1.21071 20.0391 1 19.5304 1 19V8C1 7.46957 1.21071 6.96086 1.58579 6.58579C1.96086 6.21071 2.46957 6 3 6H7L9 3H15L17 6H21C21.5304 6 22.0391 6.21071 22.4142 6.58579C22.7893 6.96086 23 7.46957 23 8V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M9.13721 9.13721C8.40024 9.87418 7.99597 10.9105 8.00002 11.9884C8.00407 13.0663 8.41611 14.0992 9.15847 14.8301C9.90082 15.561 10.9416 15.9575 12.0195 15.9455C13.0975 15.9336 14.1288 15.5138 14.8533 14.7633" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function UploadIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M17 8L12 3L7 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M12 3V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 6H5H21" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function CaptureIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="12" cy="12" r="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function TimerIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function RefreshIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M23 4V10H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M1 20V14H7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M3.51 9.00001C4.01717 7.56584 4.87913 6.28525 6.01547 5.27529C7.1518 4.26532 8.52547 3.55969 10.0083 3.22427C11.4911 2.88886 13.0348 2.93436 14.4952 3.35676C15.9556 3.77915 17.2853 4.56467 18.36 5.64001L23 10M1 14L5.64 18.36C6.71475 19.4354 8.04437 20.2209 9.50481 20.6433C10.9652 21.0657 12.5089 21.1112 13.9917 20.7758C15.4745 20.4403 16.8482 19.7347 17.9845 18.7247C19.1209 17.7148 19.9828 16.4342 20.49 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function CloseIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
