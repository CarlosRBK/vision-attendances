import axios from 'axios'
import { toast } from 'sonner'

const api = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'
})

// Request interceptor
api.interceptors.request.use((config) => {
  // JSON by default, but never set for FormData (let the browser set boundary)
  const headers = ((config.headers as any) ?? {}) as Record<string, string>
  const isFormData = typeof FormData !== 'undefined' && config.data instanceof FormData
  if (isFormData) {
    // Ensure we don't carry a stale content-type
    delete (headers as any)['Content-Type']
  } else if (!headers['Content-Type'] && config.data !== undefined) {
    headers['Content-Type'] = 'application/json'
  }
  config.headers = headers as any
  return config
})

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error: any) => {
    const status = error.response?.status
    const payload = error.response?.data as any
    const message =
      payload?.error?.message ||
      payload?.detail?.[0]?.msg ||
      payload?.message ||
      error.message ||
      'Error de red'

    if (status && status >= 400) {
      toast.error(`Error ${status}`, { description: String(message) })
    } else {
      toast.error('Error', { description: String(message) })
    }

    return Promise.reject(error)
  }
)

export default api
