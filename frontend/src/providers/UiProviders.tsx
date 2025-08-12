import type { PropsWithChildren } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ToastProvider } from '@/shared/ui/Toast'

// Crear una instancia del cliente de consulta
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000
    }
  }
})

/**
 * Proveedor de UI que encapsula todos los proveedores necesarios para la aplicación
 * - QueryClientProvider: Para gestionar el estado de las consultas y mutaciones
 * - ToastProvider: Para mostrar notificaciones toast con estilo premium
 */
export function UiProviders({ children }: PropsWithChildren) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ToastProvider 
        position="top-right"
        closeButton
        visibleToasts={3}
      />
    </QueryClientProvider>
  )
}
export default UiProviders
