import { Toaster as SonnerToaster } from 'sonner'

interface ToastProviderProps {
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center'
  duration?: number
  gap?: number
  visibleToasts?: number
  closeButton?: boolean
}

/**
 * Proveedor de notificaciones toast con estilo premium
 * Basado en la biblioteca Sonner con estilos personalizados
 */
export function ToastProvider({
  position = 'top-right',
  duration = 4000,
  gap = 8,
  visibleToasts = 3,
  closeButton = true
}: ToastProviderProps) {
  return (
    <SonnerToaster
      position={position}
      duration={duration}
      gap={gap}
      visibleToasts={visibleToasts}
      closeButton={closeButton}
      theme="system"
      className="toast-premium"
      toastOptions={{
        classNames: {
          toast: "group toast-premium-item rounded-lg border border-border bg-background p-4 shadow-lg",
          title: "text-sm font-semibold text-foreground",
          description: "text-sm text-muted-foreground",
          actionButton: "bg-primary text-primary-foreground hover:bg-primary/90",
          cancelButton: "bg-muted hover:bg-muted/80",
          error: "!bg-destructive/15 border-destructive/30 text-destructive",
          success: "!bg-success/15 border-success/30 text-success-foreground",
          warning: "!bg-warning/15 border-warning/30 text-warning-foreground",
          info: "!bg-info/15 border-info/30 text-info-foreground",
          closeButton: "text-foreground/50 hover:text-foreground"
        }
      }}
    />
  )
}

// Re-exportamos las funciones de toast para facilitar su uso
export { toast } from 'sonner'
